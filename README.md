# ⚡ Local Growth & SEO Suite

**All-In-One Enterprise Platform for Local Lead Generation & SEO Audits**

Developed as an end-to-end local growth engine combining:
1. **Google Maps Lead Scraper** (Lead generation & business prospecting with website availability filtering)
2. **Local SEO & Competitor Analyzer** (Audit Google Business Profile + Website SEO + Local SEO + Side-by-side Competitor comparison with 4-sheet Excel export)

---

## 🌟 Suite Capabilities

### 📍 Tool 1: Google Maps Lead Scraper
- Scrapes business name, star rating, total review count, address, phone number, website URL, and Google Maps link.
- **Filter**: Option to scrape **ONLY** businesses without a website to find high-intent digital agency leads.
- Formatted Excel export (`leads_<category>_<city>_<timestamp>.xlsx`).

### 📊 Tool 2: Local SEO & Competitor Analyzer
- Audits client's Google Business Profile, Website SEO, and Local SEO signals.
- **Competitor Comparison**: Compare client vs competitor on 17+ SEO metrics with automated strengths vs weaknesses.
- **4-Sheet Excel Export**:
  - **Sheet 1**: Business Information & Overall Score Summary.
  - **Sheet 2**: SEO Audit Check Results (20 checks).
  - **Sheet 3**: Actionable SEO Recommendations.
  - **Sheet 4**: Competitor Comparison Report.

---

## 🚀 Quick Start

### 1. Installation
```bash
cd C:\Users\natas\.gemini\antigravity\scratch\local_growth_suite
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Run Web Application (Multi-Tab Dashboard)
```bash
python app.py
```
Open **http://localhost:5001** in your browser.

### 3. Run Desktop Application (Native Tkinter Window)
```bash
python gui.py
```

---

## 📁 Directory Structure
```
local_growth_suite/
├── app.py              # Unified Flask Web App
├── gui.py              # Unified Desktop App (Tkinter)
├── scraper.py          # Lead Scraper Engine (Project 1)
├── analyzer.py         # SEO & Competitor Analyzer Engine (Project 2)
├── templates/
│   └── index.html      # Multi-Tab Web Interface
├── static/
│   ├── style.css       # Unified Teal CSS System
│   └── app.js          # Dual-Engine SSE Log & Summary JS
├── output/             # Generated Excel Reports
└── requirements.txt
```
