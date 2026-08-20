"""
Unified Desktop Application — Local Growth & SEO Suite
Combines Google Maps Lead Scraper AND Local SEO & Competitor Analyzer in one multi-tab window.
"""
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from analyzer import run_analysis
from scraper import export_to_excel as export_leads, scrape_google_maps

# Palette
TEAL      = "#006D77"
TEAL_DARK = "#004F58"
TEAL_LT   = "#83C5BE"
TEAL_PALE = "#E8F8F5"
BG        = "#F4F7F6"
CARD_BG   = "#FFFFFF"
TEXT      = "#1E2235"
MUTED     = "#6B7280"
BORDER    = "#E5E7EB"


class UnifiedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Local Growth & SEO Suite | Elenco Corporation")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.configure(bg=BG)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8],
                        background="#D1E7DD", foreground=TEAL_DARK, borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", TEAL)], foreground=[("selected", "white")])

        # Header
        hdr = tk.Frame(self, bg=TEAL, height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⚡ LOCAL GROWTH & SEO SUITE", font=("Segoe UI", 14, "bold"),
                 bg=TEAL, fg="white").pack(side=tk.LEFT, padx=20)
        tk.Label(hdr, text="Lead Generation + SEO Audit Platform", font=("Segoe UI", 9),
                 bg=TEAL, fg=TEAL_LT).pack(side=tk.LEFT, padx=(0, 20))

        # Notebook (Tabs)
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Create Tab 1 & Tab 2
        self._tab_scraper = tk.Frame(self._notebook, bg=BG)
        self._tab_seo     = tk.Frame(self._notebook, bg=BG)

        self._notebook.add(self._tab_scraper, text="📍 1. Google Maps Lead Scraper")
        self._notebook.add(self._tab_seo, text="📊 2. Local SEO & Competitor Analyzer")

        self._build_scraper_tab()
        self._build_seo_tab()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — GOOGLE MAPS LEAD SCRAPER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_scraper_tab(self):
        main = tk.Frame(self._tab_scraper, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main.columnconfigure(0, weight=4)
        main.columnconfigure(1, weight=6)
        main.rowconfigure(0, weight=1)

        # Left panel: Inputs
        left = tk.Frame(main, bg=CARD_BG, padx=16, pady=16,
                        highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(left, text="📍 LEAD SCRAPER INPUTS", font=("Segoe UI", 10, "bold"),
                 bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 10))

        def make_entry(label, ph=""):
            tk.Label(left, text=label, font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT).pack(anchor="w", pady=(4, 2))
            var = tk.StringVar()
            ent = tk.Entry(left, textvariable=var, font=("Segoe UI", 10), bg="#FAFCFD", fg=TEXT, relief="flat",
                           highlightthickness=1, highlightbackground=BORDER, highlightcolor=TEAL)
            ent.pack(fill=tk.X, ipady=6)
            if ph:
                ent.insert(0, ph)
                ent.config(fg=MUTED)
                def fi(e, r=ent, p=ph):
                    if r.get() == p: r.delete(0, tk.END); r.config(fg=TEXT)
                def fo(e, r=ent, p=ph):
                    if not r.get(): r.insert(0, p); r.config(fg=MUTED)
                ent.bind("<FocusIn>", fi); ent.bind("<FocusOut>", fo)
            return var, ent

        self._sc_cat_var, _ = make_entry("Business Category *", "e.g. Dentist, Restaurant")
        self._sc_city_var, _ = make_entry("City / Location *", "e.g. Pune, Mumbai")
        self._sc_max_var, _ = make_entry("Max Results", "e.g. 50 (or 'all')")

        self._sc_no_web_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(left, text="Only scrape businesses WITHOUT website", variable=self._sc_no_web_var,
                            font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#B91C1C", activebackground=CARD_BG)
        cb.pack(anchor="w", pady=(8, 2))

        self._sc_only_247_var = tk.BooleanVar(value=False)
        cb2 = tk.Checkbutton(left, text="🕒 Only scrape businesses open 24/7", variable=self._sc_only_247_var,
                             font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#047857", activebackground=CARD_BG)
        cb2.pack(anchor="w", pady=(2, 2))

        self._sc_only_hot_var = tk.BooleanVar(value=False)
        cb3 = tk.Checkbutton(left, text="🔥 Only export HOT LEADS (High Intent)", variable=self._sc_only_hot_var,
                             font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#B91C1C", activebackground=CARD_BG)
        cb3.pack(anchor="w", pady=(2, 10))

        self._sc_btn = tk.Button(left, text="🚀 Start Scraping Leads", font=("Segoe UI", 11, "bold"),
                                 bg=TEAL, fg="white", activebackground=TEAL_DARK, relief="flat", cursor="hand2", pady=10,
                                 command=self._start_scraping)
        self._sc_btn.pack(fill=tk.X, pady=(10, 0))

        # Right panel: Log
        right = tk.Frame(main, bg=CARD_BG, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="📡 SCRAPER LOG", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 6))

        sf = tk.Frame(right, bg=TEXT)
        sf.pack(fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(sf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._sc_log = tk.Text(sf, font=("Consolas", 9), bg=TEXT, fg="#A7F3D0",
                               yscrollcommand=sb.set, relief="flat", wrap=tk.WORD)
        self._sc_log.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._sc_log.yview)

        # Bottom panel: Scraped Leads Table
        bot = tk.Frame(main, bg=CARD_BG, padx=16, pady=12, highlightthickness=1, highlightbackground=BORDER)
        bot.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        main.rowconfigure(1, weight=1)

        tk.Label(bot, text="📍 SCRAPED LEADS RESULTS TABLE", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 6))

        tv_frame = tk.Frame(bot, bg=CARD_BG)
        tv_frame.pack(fill=tk.BOTH, expand=True)

        tv_scroll_y = tk.Scrollbar(tv_frame, orient=tk.VERTICAL)
        tv_scroll_x = tk.Scrollbar(tv_frame, orient=tk.HORIZONTAL)

        cols = ("Name", "Intent", "Tier", "Rating", "Reviews", "Call Window", "Phone", "Website")
        self._sc_tree = ttk.Treeview(tv_frame, columns=cols, show="headings",
                                     yscrollcommand=tv_scroll_y.set, xscrollcommand=tv_scroll_x.set)
        tv_scroll_y.config(command=self._sc_tree.yview)
        tv_scroll_x.config(command=self._sc_tree.xview)

        tv_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tv_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self._sc_tree.pack(fill=tk.BOTH, expand=True)

        col_widths = {"Name": 170, "Intent": 115, "Tier": 140, "Rating": 50, "Reviews": 55, "Call Window": 140, "Phone": 95, "Website": 140}
        for c in cols:
            self._sc_tree.heading(c, text=c)
            self._sc_tree.column(c, width=col_widths.get(c, 100), anchor="w" if c in ("Name", "Website") else "center")

        hint = tk.Label(bot, text="💡 Double-click any row to view Cold Call Script, WhatsApp & Email Templates",
                        font=("Segoe UI", 8), bg=CARD_BG, fg=MUTED)
        hint.pack(anchor="w", pady=(4, 0))
        self._sc_tree.bind("<Double-1>", self._on_lead_double_click)

        self._sc_file  = ""
        self._sc_running = False
        self._sc_leads = []

    def _start_scraping(self):
        cat = self._sc_cat_var.get().strip()
        city = self._sc_city_var.get().strip()
        max_str = self._sc_max_var.get().strip().lower()
        no_web = self._sc_no_web_var.get()
        only_247 = self._sc_only_247_var.get()
        only_hot = self._sc_only_hot_var.get()

        if not cat or not city or cat.startswith("e.g.") or city.startswith("e.g."):
            messagebox.showwarning("Missing Inputs", "Please enter Category and City.")
            return

        if self._sc_running: return
        self._sc_running = True
        self._sc_btn.config(state=tk.DISABLED, bg="#9CA3AF")
        self._sc_log.config(state=tk.NORMAL)
        self._sc_log.delete("1.0", tk.END)
        self._sc_log.config(state=tk.DISABLED)

        # Clear treeview
        for item in self._sc_tree.get_children():
            self._sc_tree.delete(item)

        max_res = 999_999 if max_str in ("all", "") else (int(max_str) if max_str.isdigit() else 50)

        def log_cb(msg):
            self._sc_log.config(state=tk.NORMAL)
            self._sc_log.insert(tk.END, msg + "\n")
            self._sc_log.see(tk.END)
            self._sc_log.config(state=tk.DISABLED)

        def worker():
            try:
                leads = scrape_google_maps(cat, city, max_res, progress_callback=log_cb, only_no_website=no_web, only_24_7=only_247, only_hot_leads=only_hot)
                if leads:
                    fp = export_leads(leads, cat, city)
                    log_cb(f"\n[DONE] 🎉 Saved {len(leads)} leads to: {fp}")

                    # Populate treeview
                    self._sc_leads = leads
                    for lead in leads:
                        call_win = (lead.get("Best Call Window") or "N/A").split("(")[0].strip()
                        self._sc_tree.insert("", tk.END, values=(
                            lead.get("Business Name", ""),
                            lead.get("Conversion Score", "N/A"),
                            lead.get("Tier", "N/A"),
                            lead.get("Rating", "N/A"),
                            lead.get("Number of Reviews", "N/A"),
                            call_win,
                            lead.get("Phone Number", "N/A"),
                            lead.get("Website", "N/A")
                        ))

                    messagebox.showinfo("Scraping Complete", f"Successfully scraped {len(leads)} leads!\nTable populated below & Excel saved.")
                else:
                    log_cb("\n[WARN] No leads collected.")
            except Exception as e:
                log_cb(f"\n[ERROR] {e}")
            finally:
                self._sc_running = False
                self._sc_btn.config(state=tk.NORMAL, bg=TEAL)

        threading.Thread(target=worker, daemon=True).start()

    def _on_lead_double_click(self, event):
        sel = self._sc_tree.selection()
        if not sel:
            return
        idx = self._sc_tree.index(sel[0])
        if not hasattr(self, '_sc_leads') or idx >= len(self._sc_leads):
            return
        self._show_lead_scripts(self._sc_leads[idx])

    def _show_lead_scripts(self, lead):
        win = tk.Toplevel(self)
        win.title(f"Scripts: {lead.get('Business Name', '')}")
        win.geometry("700x640")
        win.configure(bg=CARD_BG)
        win.grab_set()

        # Header
        hdr = tk.Frame(win, bg=TEAL, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  💼 {lead.get('Business Name', '')}", font=("Segoe UI", 12, "bold"),
                 bg=TEAL, fg="white").pack(side=tk.LEFT, padx=12)
        tk.Label(hdr, text=lead.get('Conversion Score', ''), font=("Segoe UI", 10, "bold"),
                 bg=TEAL, fg="#FCD34D").pack(side=tk.LEFT)

        info = tk.Frame(win, bg="#F0F9FA", pady=6, padx=14)
        info.pack(fill=tk.X)
        tier = lead.get('Tier', '')
        call = lead.get('Best Call Window', 'N/A')
        tk.Label(info, text=f"{tier}   |   🕐 Best Call: {call}", font=("Segoe UI", 9),
                 bg="#F0F9FA", fg=TEAL_DARK).pack(anchor="w")
        pains = lead.get('All Pain Points', 'N/A')
        tk.Label(info, text=f"⚠️ Pain Points: {pains}", font=("Segoe UI", 8),
                 bg="#F0F9FA", fg="#991B1B", wraplength=660, justify="left").pack(anchor="w", pady=(2, 0))

        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        def make_tab(title, content):
            frm = tk.Frame(nb, bg=CARD_BG)
            nb.add(frm, text=title)
            txt = tk.Text(frm, font=("Segoe UI", 9), bg="#FAFCFD", fg=TEXT,
                          relief="flat", wrap=tk.WORD, padx=10, pady=8)
            txt.insert(tk.END, content or "N/A")
            txt.config(state=tk.DISABLED)
            sb = tk.Scrollbar(frm, command=txt.yview)
            txt.config(yscrollcommand=sb.set)
            sb.pack(side=tk.RIGHT, fill=tk.Y)
            txt.pack(fill=tk.BOTH, expand=True)
            def copy_it():
                win.clipboard_clear()
                win.clipboard_append(content or "")
                btn.config(text="✅ Copied!")
                win.after(2000, lambda: btn.config(text=f"📋 Copy {title}"))
            btn = tk.Button(frm, text=f"📋 Copy {title}", command=copy_it,
                            font=("Segoe UI", 9, "bold"), bg=TEAL, fg="white",
                            relief="flat", cursor="hand2", pady=4)
            btn.pack(fill=tk.X, padx=0)

        make_tab("📞 Cold Call Script", lead.get("Cold Call Pitch Script", ""))
        make_tab("💬 WhatsApp", lead.get("WhatsApp Message", ""))
        email_full = f"SUBJECT: {lead.get('Email Subject', '')}\n\n{lead.get('Follow-Up Email', '')}"
        make_tab("📧 Follow-Up Email", email_full)


    def _build_seo_tab(self):
        main = tk.Frame(self._tab_seo, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main.columnconfigure(0, weight=4)
        main.columnconfigure(1, weight=6)
        main.rowconfigure(0, weight=1)

        # Left panel
        left = tk.Frame(main, bg=CARD_BG, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(left, text="🔍 CLIENT BUSINESS DETAILS", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 6))

        def make_entry(label, ph=""):
            tk.Label(left, text=label, font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT).pack(anchor="w", pady=(2, 1))
            var = tk.StringVar()
            ent = tk.Entry(left, textvariable=var, font=("Segoe UI", 9), bg="#FAFCFD", fg=TEXT, relief="flat",
                           highlightthickness=1, highlightbackground=BORDER, highlightcolor=TEAL)
            ent.pack(fill=tk.X, ipady=5)
            if ph:
                ent.insert(0, ph)
                ent.config(fg=MUTED)
                def fi(e, r=ent, p=ph):
                    if r.get() == p: r.delete(0, tk.END); r.config(fg=TEXT)
                def fo(e, r=ent, p=ph):
                    if not r.get(): r.insert(0, p); r.config(fg=MUTED)
                ent.bind("<FocusIn>", fi); ent.bind("<FocusOut>", fo)
            return var, ent

        self._seo_biz_var, _  = make_entry("Client Name *", "e.g. Ruby Hall Clinic")
        self._seo_cat_var, _  = make_entry("Category *", "e.g. Hospital")
        self._seo_loc_var, _  = make_entry("Location *", "e.g. Pune")
        self._seo_url_var, _  = make_entry("Client Website (optional)", "https://")

        tk.Label(left, text="⚔️ COMPETITOR COMPARISON (AUTO-DISCOVERS IF BLANK)", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(10, 2))

        self._seo_comp_name_var, _ = make_entry("Competitor Name (or leave blank to auto-discover)", "e.g. Jehangir Hospital (or leave blank)")
        self._seo_comp_url_var, _  = make_entry("Competitor Website (or leave blank)", "https:// (or leave blank)")

        self._seo_btn = tk.Button(left, text="🔍 Analyze & Compare", font=("Segoe UI", 11, "bold"),
                                  bg=TEAL, fg="white", activebackground=TEAL_DARK, relief="flat", cursor="hand2", pady=10,
                                  command=self._start_seo_analysis)
        self._seo_btn.pack(fill=tk.X, pady=(12, 0))

        # Open Excel Report Button
        self._seo_open_btn = tk.Button(left, text="📥 Open Excel Report (.xlsx)", font=("Segoe UI", 10, "bold"),
                                       bg="#10B981", fg="white", activebackground="#059669", relief="flat", cursor="hand2", pady=8,
                                       command=self._open_seo_report)
        self._seo_open_btn.pack(fill=tk.X, pady=(8, 0))
        self._seo_open_btn.pack_forget()  # Hidden until analysis completes

        # Score Summary Chip Label
        self._seo_score_lbl = tk.Label(left, text="", font=("Segoe UI", 9, "bold"), bg=TEAL_PALE, fg=TEAL_DARK,
                                       padx=8, pady=8, justify=tk.LEFT, wraplength=280)
        self._seo_score_lbl.pack(fill=tk.X, pady=(10, 0))
        self._seo_score_lbl.pack_forget()

        # Right panel: Log
        right = tk.Frame(main, bg=CARD_BG, padx=16, pady=16, highlightthickness=1, highlightbackground=BORDER)
        right.grid(row=0, column=1, sticky="nsew")

        tk.Label(right, text="📡 SEO ANALYSIS LOG", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 6))

        sf = tk.Frame(right, bg=TEXT)
        sf.pack(fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(sf)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._seo_log = tk.Text(sf, font=("Consolas", 9), bg=TEXT, fg="#A7F3D0",
                                yscrollcommand=sb.set, relief="flat", wrap=tk.WORD)
        self._seo_log.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._seo_log.yview)

        # Bottom panel: Competitor Comparison Table & Recommendations
        bot = tk.Frame(main, bg=CARD_BG, padx=16, pady=12, highlightthickness=1, highlightbackground=BORDER)
        bot.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        main.rowconfigure(1, weight=1)

        tk.Label(bot, text="⚔️ COMPETITOR COMPARISON TABLE & ACTIONABLE INSIGHTS", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=TEAL).pack(anchor="w", pady=(0, 6))

        tv_frame = tk.Frame(bot, bg=CARD_BG)
        tv_frame.pack(fill=tk.BOTH, expand=True)

        tv_scroll_y = tk.Scrollbar(tv_frame, orient=tk.VERTICAL)
        tv_scroll_x = tk.Scrollbar(tv_frame, orient=tk.HORIZONTAL)

        cols = ("Metric", "Client", "Competitor", "Winner / Advantage")
        self._seo_tree = ttk.Treeview(tv_frame, columns=cols, show="headings",
                                      yscrollcommand=tv_scroll_y.set, xscrollcommand=tv_scroll_x.set)
        tv_scroll_y.config(command=self._seo_tree.yview)
        tv_scroll_x.config(command=self._seo_tree.xview)

        tv_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tv_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self._seo_tree.pack(fill=tk.BOTH, expand=True)

        col_widths = {"Metric": 200, "Client": 250, "Competitor": 250, "Winner / Advantage": 160}
        for c in cols:
            self._seo_tree.heading(c, text=c)
            self._seo_tree.column(c, width=col_widths.get(c, 150), anchor="w" if c != "Winner / Advantage" else "center")

        # Recommendations / Strengths Text Box below treeview
        self._seo_recs_box = tk.Text(bot, font=("Segoe UI", 9), bg="#F8FAFC", fg=TEXT, height=5, relief="flat", wrap=tk.WORD)
        self._seo_recs_box.pack(fill=tk.X, pady=(6, 0))

        self._seo_file = ""
        self._seo_running = False

    def _open_seo_report(self):
        if self._seo_file and os.path.exists(self._seo_file):
            try:
                os.startfile(self._seo_file)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        else:
            messagebox.showwarning("File Missing", "No generated report file found.")

    def _start_seo_analysis(self):
        biz = self._seo_biz_var.get().strip()
        cat = self._seo_cat_var.get().strip()
        loc = self._seo_loc_var.get().strip()
        url = self._seo_url_var.get().strip()
        c_nm = self._seo_comp_name_var.get().strip()
        c_ur = self._seo_comp_url_var.get().strip()

        if url.startswith("https://") and len(url) == 8: url = ""
        if c_ur.startswith("https://") and len(c_ur) == 8: c_ur = ""
        if biz.startswith("e.g."): biz = ""
        if cat.startswith("e.g."): cat = ""
        if loc.startswith("e.g."): loc = ""
        if c_nm.startswith("e.g."): c_nm = ""

        if not biz or not cat or not loc:
            messagebox.showwarning("Missing Fields", "Please fill Client Name, Category, and Location.")
            return

        if self._seo_running: return
        self._seo_running = True
        self._seo_btn.config(state=tk.DISABLED, bg="#9CA3AF")
        self._seo_open_btn.pack_forget()
        self._seo_score_lbl.pack_forget()
        self._seo_log.config(state=tk.NORMAL)
        self._seo_log.delete("1.0", tk.END)
        self._seo_log.config(state=tk.DISABLED)

        # Clear Treeview & Recs Box
        for item in self._seo_tree.get_children():
            self._seo_tree.delete(item)
        self._seo_recs_box.delete("1.0", tk.END)

        def log_cb(msg):
            self._seo_log.config(state=tk.NORMAL)
            self._seo_log.insert(tk.END, msg + "\n")
            self._seo_log.see(tk.END)
            self._seo_log.config(state=tk.DISABLED)

        def worker():
            try:
                fp = run_analysis(biz, cat, loc, url, competitor_name=c_nm, competitor_url=c_ur, progress_callback=log_cb)
                self._seo_file = fp
                log_cb(f"\n[DONE] 🎉 SEO Report saved to: {fp}")

                # Retrieve analysis summary data
                from analyzer import get_latest_analysis_data
                data = get_latest_analysis_data()

                if data:
                    client_scores = data.get("client", {}).get("scores", {})
                    if client_scores:
                        score_text = (
                            f"🏆 OVERALL SCORE: {client_scores.get('total_score', 0)} / 100 (Grade: {client_scores.get('grade', 'F')})\n"
                            f"GBP: {client_scores.get('gbp_score', 0)}/30 | Website: {client_scores.get('web_score', 0)}/40 | Local: {client_scores.get('local_score', 0)}/30"
                        )
                        self._seo_score_lbl.config(text=score_text)
                        self._seo_score_lbl.pack(fill=tk.X, pady=(10, 0))

                    comp = data.get("comparison")
                    if comp:
                        # Update heading text
                        self._seo_tree.heading("Client", text=f"Client: {comp.get('client_name', 'Client')}")
                        self._seo_tree.heading("Competitor", text=f"Competitor: {comp.get('comp_name', 'Competitor')}")

                        for r in comp.get("rows", []):
                            self._seo_tree.insert("", tk.END, values=(
                                r.get("metric", ""),
                                r.get("client", ""),
                                r.get("competitor", ""),
                                r.get("advantage", "—")
                            ))

                        recs_txt = "🟢 CLIENT STRENGTHS:\n"
                        for s in comp.get("strengths", []):
                            recs_txt += f"  • {s}\n"
                        recs_txt += "\n🔴 COMPETITOR ADVANTAGES & INSIGHTS:\n"
                        for w in comp.get("weaknesses", []):
                            recs_txt += f"  • {w}\n"

                        self._seo_recs_box.insert(tk.END, recs_txt)

                self._seo_open_btn.pack(fill=tk.X, pady=(8, 0))
                messagebox.showinfo("SEO Analysis Complete", f"Report saved & comparison table populated!\nClick 'Open Excel Report' to view .xlsx file.")

            except Exception as e:
                log_cb(f"\n[ERROR] {e}")
            finally:
                self._seo_running = False
                self._seo_btn.config(state=tk.NORMAL, bg=TEAL)

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = UnifiedApp()
    app.mainloop()


if __name__ == "__main__":
    main()
