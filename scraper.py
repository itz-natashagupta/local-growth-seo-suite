"""
Google Maps Lead Scraper — Core Engine
Scrapes business leads from Google Maps based on category and city,
filters by website availability if requested, and exports formatted Excel files.
"""
import os
import random
import re
import sys
import time
from datetime import datetime

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

MAX_RESULTS = 50
SCROLL_PAUSE = 0.2
ACTION_DELAY = (0.2, 0.5)
HEADLESS = True


def human_delay(low: float = ACTION_DELAY[0], high: float = ACTION_DELAY[1]) -> None:
    time.sleep(random.uniform(low, high))


def safe_text(locator, timeout: int = 1500) -> str:
    try:
        return locator.first.inner_text(timeout=timeout).strip()
    except Exception:
        return ""


def safe_attribute(locator, attr: str, timeout: int = 1500) -> str:
    try:
        return (locator.first.get_attribute(attr, timeout=timeout) or "").strip()
    except Exception:
        return ""


def extract_lead(page) -> dict:
    lead = {
        "Business Name": "",
        "Rating": "",
        "Number of Reviews": "",
        "Address": "",
        "Phone Number": "",
        "Website": "",
        "Google Maps Link": page.url,
    }

    try:
        lead["Business Name"] = safe_text(page.locator('h1.DUwDvf, h1[class*="fontHeadlineLarge"]'))

        rating, reviews = page.evaluate("""() => {
            const feed = document.querySelector('div[role="feed"]');
            function inFeed(el) { return feed ? feed.contains(el) : false; }
            const allEls = Array.from(document.querySelectorAll('[aria-label]'));
            const allSpans = Array.from(document.querySelectorAll('span'));
            let rating = '';
            let reviews = '';

            for (const el of allEls) {
                if (inFeed(el)) continue;
                const label = el.getAttribute('aria-label') || '';
                const m = label.match(/([1-5][.,][0-9])\\s*stars?/i);
                if (m) { rating = m[1].replace(',', '.'); break; }
            }
            if (!rating) {
                for (const span of allSpans) {
                    if (inFeed(span)) continue;
                    const txt = span.textContent.strip ? span.textContent.strip() : span.textContent.trim();
                    if (/^[1-5]\\.[0-9]$/.test(txt)) { rating = txt; break; }
                }
            }

            for (const el of allEls) {
                if (inFeed(el)) continue;
                const label = el.getAttribute('aria-label') || '';
                const m = label.match(/^([ \\d,]+)\\s*reviews?$/i);
                if (m) { reviews = m[1].replace(/[, ]/g, ''); break; }
            }
            if (!reviews) {
                for (const el of allEls) {
                    if (inFeed(el)) continue;
                    const label = el.getAttribute('aria-label') || '';
                    const m = label.match(/([\\d,]+)\\s*reviews?/i);
                    if (m) { reviews = m[1].replace(/,/g, ''); break; }
                }
            }
            if (!reviews) {
                for (const span of allSpans) {
                    if (inFeed(span)) continue;
                    const txt = span.textContent.trim();
                    const m = txt.match(/^\\(([\\d,]+)\\)$/);
                    if (m) { reviews = m[1].replace(/,/g, ''); break; }
                }
            }
            return [rating, reviews];
        }""")

        lead["Rating"] = rating
        lead["Number of Reviews"] = reviews

        address_el = page.locator('[data-item-id="address"] .Io6YTe, [data-tooltip="Copy address"] .Io6YTe')
        lead["Address"] = safe_text(address_el)

        phone_el = page.locator('[data-item-id^="phone:"] .Io6YTe')
        lead["Phone Number"] = safe_text(phone_el)

        website_el = page.locator('[data-item-id="authority"] a, [aria-label^="Website:"] a')
        lead["Website"] = safe_attribute(website_el, "href")
        if not lead["Website"]:
            lead["Website"] = safe_text(page.locator('[data-item-id="authority"] .Io6YTe'))

        if lead["Website"] and not lead["Website"].startswith("http"):
            lead["Website"] = "https://" + lead["Website"]

        maps_url = page.url
        if "google.com/maps/place" in maps_url:
            lead["Google Maps Link"] = maps_url.split("?")[0]

    except Exception as e:
        print(f"  [WARN] Error extracting details: {e}")

    return lead


def scrape_google_maps(category: str, city: str, max_results: int = MAX_RESULTS,
                       progress_callback=None, only_no_website: bool = False) -> list:
    def emit(msg):
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)

    search_query = f"{category} in {city}"
    search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
    leads = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=[
                "--start-maximized",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--ignore-certificate-errors",
                "--host-resolver-rules=",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        filter_msg = " [FILTER: NO WEBSITE ONLY]" if only_no_website else ""
        emit(f"[SEARCH] Searching Google Maps for: '{search_query}'{filter_msg}")
        emit(f"   URL: {search_url}")

        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        human_delay(2, 2.5)

        try:
            reject_btn = page.locator('button:has-text("Reject all"), button:has-text("Accept all")')
            if reject_btn.count() > 0:
                reject_btn.first.click()
                emit("   [OK] Handled cookie consent dialog.")
        except Exception:
            pass

        try:
            page.wait_for_selector('div[role="feed"]', timeout=15000)
        except PlaywrightTimeoutError:
            emit("   [WARN] Results panel did not appear.")
            browser.close()
            return leads

        try:
            page.wait_for_selector('a.hfpxzc', timeout=12000)
            emit("   [OK] Listings loaded. Starting collection...")
        except PlaywrightTimeoutError:
            emit("   [WARN] No listing cards found.")
            browser.close()
            return leads

        target_url_count = (max_results * 4) if (only_no_website and max_results < 9000) else max_results
        emit(f"[SCROLL] Collecting business links (target: {target_url_count})...")
        business_urls = []
        previous_count = 0
        no_new_count   = 0

        while len(business_urls) < target_url_count:
            cards = page.locator('a.hfpxzc').all()
            seen = set(business_urls)
            for card in cards:
                try:
                    href = card.get_attribute("href") or ""
                    if href and href not in seen:
                        business_urls.append(href)
                        seen.add(href)
                except Exception:
                    continue

            emit(f"   Found {len(business_urls)} links so far...")

            if page.locator('span.HlvSq').count() and page.locator('span.HlvSq').is_visible():
                emit(f"   [DONE] End of results. Total links: {len(business_urls)}")
                break

            if len(business_urls) == previous_count:
                no_new_count += 1
                if no_new_count >= 8:
                    emit(f"   [DONE] No new links after scrolling. Total: {len(business_urls)}")
                    break
                time.sleep(1.5)
            else:
                no_new_count = 0

            previous_count = len(business_urls)

            try:
                page.locator('div[role="feed"]').evaluate("el => el.scrollBy(0, 2500)")
            except Exception:
                page.keyboard.press("End")
            time.sleep(SCROLL_PAUSE)

        business_urls = business_urls[:target_url_count]
        emit(f"[OK] Collected {len(business_urls)} business URLs. Visiting each details page...")

        for idx, url in enumerate(business_urls, start=1):
            if len(leads) >= max_results:
                emit(f"[DONE] Collected target of {max_results} leads!")
                break
            try:
                emit(f"[{idx:02d}/{len(business_urls)}] Fetching lead details...")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                try:
                    page.wait_for_selector("h1", timeout=8000)
                except PlaywrightTimeoutError:
                    pass

                lead = extract_lead(page)
                has_website = bool(lead["Website"] and lead["Website"].strip() not in ("", "N/A"))

                if only_no_website and has_website:
                    emit(f"   [SKIP] Has website ({lead['Website']}): {lead['Business Name']}")
                    human_delay(*ACTION_DELAY)
                    continue

                leads.append(lead)
                emit(f"   DONE: {lead['Business Name']} | {lead['Rating']} ★ | 📞 {lead['Phone Number']}")
                human_delay(*ACTION_DELAY)

            except Exception as e:
                emit(f"  [{idx:02d}] [ERROR] {e}")
                continue

        browser.close()

    return leads


def export_to_excel(leads: list, category: str, city: str) -> str:
    if not leads:
        print("\n[WARN] No leads to export.")
        return ""

    df = pd.DataFrame(leads, columns=[
        "Business Name", "Rating", "Number of Reviews", "Address", "Phone Number", "Website", "Google Maps Link",
    ])

    for col in ["Phone Number", "Website", "Rating", "Number of Reviews"]:
        df[col] = df[col].replace("", "N/A").fillna("N/A")

    df = df.drop_duplicates(subset=["Business Name", "Google Maps Link"], keep="first").reset_index(drop=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_cat = re.sub(r'[^\w]', '_', category)
    safe_city = re.sub(r'[^\w]', '_', city)
    filename = f"leads_{safe_cat}_{safe_city}_{timestamp}.xlsx"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Leads")
        worksheet = writer.sheets["Leads"]

        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

        header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="1A73E8", end_color="1A73E8", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style="thin"), right=Side(style="thin"),
            top=Side(style="thin"), bottom=Side(style="thin")
        )

        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        light_fill = PatternFill(start_color="EAF1FB", end_color="EAF1FB", fill_type="solid")
        data_font = Font(name="Calibri", size=10)
        data_align = Alignment(vertical="center", wrap_text=False)

        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
            fill = light_fill if row_idx % 2 == 0 else PatternFill()
            for cell in row:
                cell.font = data_font
                cell.fill = fill
                cell.alignment = data_align
                cell.border = thin_border

        col_widths = {"A": 30, "B": 10, "C": 15, "D": 40, "E": 18, "F": 35, "G": 55}
        for col_letter, width in col_widths.items():
            worksheet.column_dimensions[col_letter].width = width

        worksheet.freeze_panes = "A2"

        for row in worksheet.iter_rows(min_row=2, min_col=6, max_col=7):
            for cell in row:
                if cell.value and str(cell.value).startswith("http"):
                    cell.hyperlink = cell.value
                    cell.font = Font(name="Calibri", size=10, color="1A73E8", underline="single")

        worksheet.auto_filter.ref = worksheet.dimensions

    print(f"\n[OK] Excel saved: {filepath}")
    return filepath
