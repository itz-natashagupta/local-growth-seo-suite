"""
Local Growth & SEO Suite — Unified Web Application
Runs both Google Maps Lead Scraper AND Local SEO & Competitor Analyzer
Port: 5001 (http://localhost:5001)
"""
import json
import os
import queue
import threading

from flask import Flask, Response, jsonify, render_template, request, send_file

from analyzer import get_latest_analysis_data, run_analysis
from scraper import export_to_excel as export_leads, scrape_google_maps

app = Flask(__name__)

# Scraper state queues
_scrape_q: queue.Queue   = queue.Queue()
_scrape_file: str        = ""
_scrape_running: bool    = False
_latest_scraped_leads: list = []

# SEO Analyzer state queues
_seo_q: queue.Queue    = queue.Queue()
_seo_file: str         = ""
_seo_running: bool     = False


@app.route("/")
def index():
    return render_template("index.html")


# ─── TOOL 1: Google Maps Lead Scraper Endpoints ──────────────────────────────
@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    global _scrape_running, _scrape_file, _scrape_q, _latest_scraped_leads

    if _scrape_running:
        return jsonify({"error": "Lead scraping is already in progress."}), 409

    data            = request.get_json() or {}
    category        = (data.get("category") or "").strip()
    city            = (data.get("city") or "").strip()
    max_results_raw = (data.get("max_results") or "50").strip().lower()
    only_no_website = bool(data.get("only_no_website", False))
    only_24_7       = bool(data.get("only_24_7", False))
    only_hot_leads  = bool(data.get("only_hot_leads", False))

    if not category or not city:
        return jsonify({"error": "Category and City are required fields."}), 400

    if max_results_raw == "all":
        max_results = 999_999
    elif max_results_raw.isdigit():
        max_results = int(max_results_raw)
    else:
        max_results = 50

    _scrape_q             = queue.Queue()
    _scrape_file          = ""
    _latest_scraped_leads = []
    _scrape_running       = True

    def run():
        global _scrape_running, _scrape_file, _latest_scraped_leads
        try:
            leads = scrape_google_maps(
                category, city, max_results,
                progress_callback=lambda m: _scrape_q.put(m),
                only_no_website=only_no_website,
                only_24_7=only_24_7,
                only_hot_leads=only_hot_leads
            )
            if leads:
                filepath = export_leads(leads, category, city)
                _scrape_file = filepath
                _latest_scraped_leads = leads
                _scrape_q.put(f"[DONE] Lead scraping complete! Total: {len(leads)} leads. File: {os.path.basename(filepath)}")
            else:
                _scrape_q.put("[WARN] No leads collected.")
        except Exception as exc:
            _scrape_q.put(f"[ERROR] {exc}")
        finally:
            _scrape_running = False
            _scrape_q.put("__END__")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/leads_data")
def leads_data():
    return jsonify({"leads": _latest_scraped_leads, "filepath": _scrape_file})


@app.route("/api/lead_detail/<int:idx>")
def lead_detail(idx):
    if idx < 0 or idx >= len(_latest_scraped_leads):
        return jsonify({"error": "Lead index out of range"}), 404
    lead = _latest_scraped_leads[idx]
    return jsonify({
        "name":          lead.get("Business Name", ""),
        "tier":          lead.get("Tier", ""),
        "badge":         lead.get("Conversion Score", ""),
        "all_pains":     lead.get("All Pain Points", ""),
        "best_call":     lead.get("Best Call Window", ""),
        "pitch":         lead.get("Cold Call Pitch Script", ""),
        "whatsapp":      lead.get("WhatsApp Message", ""),
        "email_subject": lead.get("Email Subject", ""),
        "email_body":    lead.get("Follow-Up Email", ""),
        "phone":         lead.get("Phone Number", ""),
        "rating":        lead.get("Rating", ""),
        "reviews":       lead.get("Number of Reviews", ""),
        "website":       lead.get("Website", ""),
        "address":       lead.get("Address", ""),
    })


@app.route("/api/progress/scrape")
def scrape_progress():
    def stream():
        while True:
            try:
                msg = _scrape_q.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg == "__END__":
                    break
            except queue.Empty:
                yield f"data: {json.dumps('__PING__')}\n\n"
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/download/scrape")
def download_scrape():
    if _scrape_file and os.path.exists(_scrape_file):
        return send_file(_scrape_file, as_attachment=True)
    return jsonify({"error": "No lead report available yet."}), 404


# ─── TOOL 2: Local SEO & Competitor Analyzer Endpoints ───────────────────────
@app.route("/api/analyze", methods=["POST"])
def start_analyze():
    global _seo_running, _seo_file, _seo_q

    if _seo_running:
        return jsonify({"error": "SEO Analysis is already in progress."}), 409

    data            = request.get_json() or {}
    business_name   = (data.get("business_name") or "").strip()
    category        = (data.get("category") or "").strip()
    location        = (data.get("location") or "").strip()
    website_url     = (data.get("website_url") or "").strip()
    competitor_name = (data.get("competitor_name") or "").strip()
    competitor_url  = (data.get("competitor_url") or "").strip()

    if not business_name or not category or not location:
        return jsonify({"error": "Business Name, Category and Location are required."}), 400

    _seo_q       = queue.Queue()
    _seo_file    = ""
    _seo_running = True

    def run():
        global _seo_running, _seo_file
        try:
            filepath = run_analysis(
                business_name, category, location, website_url,
                competitor_name=competitor_name,
                competitor_url=competitor_url,
                progress_callback=lambda m: _seo_q.put(m),
            )
            _seo_file = filepath
            _seo_q.put(f"[DONE] SEO Analysis complete! Report ready: {os.path.basename(filepath)}")
        except Exception as exc:
            _seo_q.put(f"[ERROR] {exc}")
        finally:
            _seo_running = False
            _seo_q.put("__END__")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/progress/analyze")
def analyze_progress():
    def stream():
        while True:
            try:
                msg = _seo_q.get(timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
                if msg == "__END__":
                    break
            except queue.Empty:
                yield f"data: {json.dumps('__PING__')}\n\n"
    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/summary")
def summary():
    data = get_latest_analysis_data()
    return jsonify(data)


@app.route("/api/download/analyze")
def download_analyze():
    if _seo_file and os.path.exists(_seo_file):
        return send_file(_seo_file, as_attachment=True)
    return jsonify({"error": "No SEO report available yet."}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001, threaded=True)
