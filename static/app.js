/* Local Growth & SEO Suite — Unified Frontend Logic */

function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

  if (tabName === 'scraper') {
    document.getElementById('tabBtnScraper').classList.add('active');
    document.getElementById('tabScraper').classList.add('active');
  } else {
    document.getElementById('tabBtnSeo').classList.add('active');
    document.getElementById('tabSeo').classList.add('active');
  }
}

// ─── TAB 1: Lead Scraper ──────────────────────────────────────────────────────
let scEventSource = null;

function startScrape() {
  const category = document.getElementById('scCategory').value.trim();
  const city     = document.getElementById('scCity').value.trim();
  const maxRes   = document.getElementById('scMax').value.trim();
  const noWeb    = document.getElementById('scNoWeb').checked;
  const only247  = document.getElementById('scOnly247').checked;
  const onlyHot  = document.getElementById('scOnlyHot').checked;

  if (!category || !city) {
    alert('Please enter Business Category and City.');
    return;
  }

  const btn = document.getElementById('scBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Scraping Google Maps Leads...';
  document.getElementById('scDownloadBtn').style.display = 'none';

  const logBox = document.getElementById('scLogBox');
  logBox.innerHTML = '';

  fetch('/api/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category, city, max_results: maxRes, only_no_website: noWeb, only_24_7: only247, only_hot_leads: onlyHot })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
      btn.disabled = false;
      btn.textContent = '🚀 Start Scraping Leads';
      return;
    }
    listenScrapeProgress();
  })
  .catch(err => {
    alert('Failed to connect to backend.');
    btn.disabled = false;
    btn.textContent = '🚀 Start Scraping Leads';
  });
}

function listenScrapeProgress() {
  if (scEventSource) scEventSource.close();
  scEventSource = new EventSource('/api/progress/scrape');

  const logBox = document.getElementById('scLogBox');

  scEventSource.onmessage = function(e) {
    const msg = JSON.parse(e.data);
    if (msg === '__PING__') return;

    if (msg === '__END__') {
      scEventSource.close();
      const btn = document.getElementById('scBtn');
      btn.disabled = false;
      btn.textContent = '🚀 Start Scraping Leads';
      document.getElementById('scDownloadBtn').style.display = 'block';
      fetchScrapedLeadsTable();
      return;
    }

    const line = document.createElement('div');
    line.textContent = msg;
    if (msg.startsWith('[SEARCH]')) line.className = 'log-start';
    else if (msg.startsWith('[SCROLL]')) line.className = 'log-gbp';
    else if (msg.startsWith('[DONE]')) line.className = 'log-done';
    else if (msg.startsWith('[ERROR]')) line.className = 'log-error';

    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
  };
}

function downloadScrapeReport() {
  window.location.href = '/api/download/scrape';
}


// ─── TAB 2: SEO & Competitor Analyzer ─────────────────────────────────────────
let seoEventSource = null;

function startSeoAnalysis() {
  const business_name   = document.getElementById('seoBusinessName').value.trim();
  const category        = document.getElementById('seoCategory').value.trim();
  const location        = document.getElementById('seoLocation').value.trim();
  const website_url     = document.getElementById('seoWebsiteUrl').value.trim();
  const competitor_name = document.getElementById('seoCompName').value.trim();
  const competitor_url  = document.getElementById('seoCompUrl').value.trim();

  if (!business_name || !category || !location) {
    alert('Please enter Client Business Name, Category, and Location.');
    return;
  }

  const btn = document.getElementById('seoBtn');
  btn.disabled = true;
  btn.textContent = '⏳ Analyzing Business & Competitor...';

  document.getElementById('statsStrip').style.display = 'none';
  document.getElementById('seoDownloadBtn').style.display = 'none';
  document.getElementById('comparisonCard').style.display = 'none';

  const logBox = document.getElementById('seoLogBox');
  logBox.innerHTML = '';

  fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ business_name, category, location, website_url, competitor_name, competitor_url })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
      btn.disabled = false;
      btn.textContent = '🔍 Analyze & Compare';
      return;
    }
    listenSeoProgress();
  })
  .catch(err => {
    alert('Failed to connect to backend server.');
    btn.disabled = false;
    btn.textContent = '🔍 Analyze & Compare';
  });
}

function listenSeoProgress() {
  if (seoEventSource) seoEventSource.close();
  seoEventSource = new EventSource('/api/progress/analyze');

  const logBox = document.getElementById('seoLogBox');

  seoEventSource.onmessage = function(e) {
    const msg = JSON.parse(e.data);
    if (msg === '__PING__') return;

    if (msg === '__END__') {
      seoEventSource.close();
      const btn = document.getElementById('seoBtn');
      btn.disabled = false;
      btn.textContent = '🔍 Analyze & Compare';
      fetchSummaryData();
      return;
    }

    const line = document.createElement('div');
    line.textContent = msg;
    if (msg.startsWith('[START]')) line.className = 'log-start';
    else if (msg.startsWith('[GBP]')) line.className = 'log-gbp';
    else if (msg.startsWith('[WEB]')) line.className = 'log-web';
    else if (msg.startsWith('[SCORE]')) line.className = 'log-score';
    else if (msg.startsWith('[DONE]')) line.className = 'log-done';
    else if (msg.startsWith('[ERROR]')) line.className = 'log-error';

    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
  };
}

function fetchSummaryData() {
  fetch('/api/summary')
    .then(res => res.json())
    .then(data => {
      if (data && data.client && data.client.scores) {
        const s = data.client.scores;
        document.getElementById('gbpScore').textContent   = s.gbp_score;
        document.getElementById('webScore').textContent   = s.web_score;
        document.getElementById('localScore').textContent = s.local_score;
        document.getElementById('totalScore').textContent = `${s.total_score} (${s.grade})`;

        document.getElementById('statsStrip').style.display = 'grid';
        document.getElementById('seoDownloadBtn').style.display = 'block';

        if (data.comparison) {
          renderComparisonUI(data.comparison);
        }
      }
    });
}

function renderComparisonUI(comp) {
  const container = document.getElementById('comparisonContainer');
  let html = `
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;font-size:13px;">
      <thead>
        <tr style="background:#1B4F72;color:white;">
          <th style="padding:10px;text-align:left;">Metric / SEO Factor</th>
          <th style="padding:10px;text-align:left;background:#006D77;">Client: ${comp.client_name}</th>
          <th style="padding:10px;text-align:left;background:#2E4053;">Competitor: ${comp.comp_name}</th>
          <th style="padding:10px;text-align:center;">Winner / Advantage</th>
        </tr>
      </thead>
      <tbody>
  `;

  comp.rows.forEach(r => {
    const advClass = r.advantage.includes('Client') ? 'background:#D4EDDA;color:#155724;' :
                     (r.advantage.includes('Competitor') ? 'background:#F8D7DA;color:#721C24;' : '');
    html += `
      <tr style="border-bottom:1px solid #E5E7EB;">
        <td style="padding:8px 10px;font-weight:600;">${r.metric}</td>
        <td style="padding:8px 10px;">${r.client}</td>
        <td style="padding:8px 10px;">${r.competitor}</td>
        <td style="padding:8px 10px;text-align:center;font-weight:bold;${advClass}">${r.advantage}</td>
      </tr>
    `;
  });

  html += `</tbody></table>`;

  if (comp.strengths && comp.strengths.length) {
    html += `
      <div style="background:#E8F8F5;border-left:4px solid #27AE60;padding:12px;margin-bottom:12px;border-radius:4px;">
        <strong style="color:#27AE60;">🟢 Client Competitive Strengths:</strong>
        <ul style="margin-top:6px;margin-left:20px;font-size:13px;">
          ${comp.strengths.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  if (comp.weaknesses && comp.weaknesses.length) {
    html += `
      <div style="background:#F8D7DA;border-left:4px solid #C0392B;padding:12px;border-radius:4px;">
        <strong style="color:#C0392B;">🔴 Competitor Advantages & Actionable Insights:</strong>
        <ul style="margin-top:6px;margin-left:20px;font-size:13px;">
          ${comp.weaknesses.map(w => `<li>${w}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  container.innerHTML = html;
  document.getElementById('comparisonCard').style.display = 'block';
}

function downloadSeoReport() {
  window.location.href = '/api/download/analyze';
}

function fetchScrapedLeadsTable() {
  fetch('/api/leads_data')
    .then(res => res.json())
    .then(data => {
      if (data && data.leads && data.leads.length > 0) {
        const tbody = document.getElementById('scLeadsBody');
        document.getElementById('scLeadsCount').textContent = data.leads.length;

        let rowsHtml = '';
        data.leads.forEach((lead, idx) => {
          const ratingStr = lead['Rating'] && lead['Rating'] !== 'N/A' ? `${lead['Rating']} ★` : 'N/A';
          const rtgBadge  = lead['Rating'] && parseFloat(lead['Rating']) >= 4.0
            ? 'background:#D4EDDA;color:#155724;padding:2px 8px;border-radius:12px;font-weight:bold;'
            : 'background:#F8D7DA;color:#721C24;padding:2px 8px;border-radius:12px;';

          const webLink = lead['Website'] && lead['Website'] !== 'N/A'
            ? `<a href="${lead['Website']}" target="_blank" style="color:#006D77;text-decoration:underline;">${lead['Website'].replace(/^https?:\/\//, '').substring(0,28)}</a>`
            : '<span style="color:#9CA3AF;">No Website</span>';

          const intentBadge = lead['Conversion Score'] || '❄️ 60% COLD LEAD';
          const intentBg = intentBadge.includes('🔥') || intentBadge.includes('HOT')
            ? 'background:#FEE2E2;color:#991B1B;padding:3px 8px;border-radius:12px;font-weight:bold;font-size:11px;'
            : (intentBadge.includes('⚡') || intentBadge.includes('WARM')
              ? 'background:#FEF3C7;color:#92400E;padding:3px 8px;border-radius:12px;font-weight:bold;font-size:11px;'
              : 'background:#E5E7EB;color:#374151;padding:3px 8px;border-radius:12px;font-size:11px;');

          const tierBadge = lead['Tier'] || '';
          const tierBg = tierBadge.includes('Tier A')
            ? 'background:#FEE2E2;color:#B91C1C;padding:3px 8px;border-radius:12px;font-size:10px;font-weight:700;'
            : (tierBadge.includes('Tier B')
              ? 'background:#FEF3C7;color:#92400E;padding:3px 8px;border-radius:12px;font-size:10px;font-weight:700;'
              : 'background:#E5E7EB;color:#374151;padding:3px 8px;border-radius:12px;font-size:10px;');

          const callWin = (lead['Best Call Window'] || 'N/A').split('(')[0].trim();
          const rowBg = intentBadge.includes('HOT') ? 'background:#FFF5F5;' : (intentBadge.includes('WARM') ? 'background:#FFFDF0;' : '');

          rowsHtml += `
            <tr style="border-bottom:1px solid #E5E7EB;${rowBg}cursor:pointer;transition:background 0.15s;" onmouseover="this.style.filter='brightness(0.96)'" onmouseout="this.style.filter=''" onclick="showLeadDetail(${idx})">
              <td style="padding:10px;text-align:center;font-weight:bold;color:#6B7280;">${idx + 1}</td>
              <td style="padding:10px;font-weight:600;">${lead['Business Name']}</td>
              <td style="padding:10px;text-align:center;"><span style="${intentBg}">${intentBadge}</span></td>
              <td style="padding:10px;text-align:center;"><span style="${tierBg}">${tierBadge}</span></td>
              <td style="padding:10px;text-align:center;"><span style="${rtgBadge}">${ratingStr}</span></td>
              <td style="padding:10px;text-align:center;">${lead['Number of Reviews'] || 'N/A'}</td>
              <td style="padding:10px;text-align:center;font-size:11px;color:#374151;">${callWin}</td>
              <td style="padding:10px;">${lead['Phone Number'] || 'N/A'}</td>
              <td style="padding:10px;">${webLink}</td>
              <td style="padding:10px;text-align:center;">
                <button onclick="event.stopPropagation();showLeadDetail(${idx})" style="background:linear-gradient(135deg,#006D77,#004D54);color:white;border:none;padding:5px 10px;border-radius:6px;font-size:11px;cursor:pointer;white-space:nowrap;">💼 View Scripts</button>
              </td>
            </tr>
          `;
        });

        tbody.innerHTML = rowsHtml;
        document.getElementById('scLeadsCard').style.display = 'block';
        document.getElementById('scLeadsCard').scrollIntoView({ behavior: 'smooth' });
      }
    });
}

// ─── Lead Detail Drawer ────────────────────────────────────────────────────────
function showLeadDetail(idx) {
  fetch(`/api/lead_detail/${idx}`)
    .then(res => res.json())
    .then(d => {
      if (d.error) { alert(d.error); return; }

      document.getElementById('drawerName').textContent  = d.name;
      document.getElementById('drawerTier').textContent  = d.tier;
      document.getElementById('drawerRating').textContent  = d.rating || 'N/A';
      document.getElementById('drawerReviews').textContent = d.reviews || '0';
      document.getElementById('drawerPhone').textContent   = d.phone || 'N/A';
      document.getElementById('drawerCallTime').textContent = d.best_call || 'N/A';

      // Badge colour
      const badge   = d.badge || '';
      const badgeEl = document.getElementById('drawerBadge');
      badgeEl.textContent = badge;
      badgeEl.style.background = badge.includes('HOT') ? 'rgba(239,68,68,0.3)'
        : badge.includes('WARM') ? 'rgba(251,191,36,0.3)' : 'rgba(255,255,255,0.2)';
      badgeEl.style.color = 'white';

      // Pain points as bullet list
      const pains = (d.all_pains || '').split(' | ').filter(Boolean);
      document.getElementById('drawerPains').innerHTML = pains.map(p =>
        `<div style="margin-bottom:4px;">⚠️ ${p}</div>`).join('') || '<div style="color:#9CA3AF;">None detected</div>';

      document.getElementById('drawerPitch').textContent    = d.pitch   || 'N/A';
      document.getElementById('drawerWhatsapp').textContent = d.whatsapp || 'N/A';
      document.getElementById('drawerEmailSubject').textContent = d.email_subject || '';
      document.getElementById('drawerEmail').textContent    = d.email_body || 'N/A';

      // Show drawer
      document.getElementById('leadDrawerOverlay').style.display = 'block';
      const drawer = document.getElementById('leadDrawer');
      drawer.style.display = 'block';
      drawer.scrollTop = 0;
      // Slide animation
      drawer.style.transform = 'translateX(100%)';
      drawer.style.transition = 'transform 0.28s cubic-bezier(0.4,0,0.2,1)';
      requestAnimationFrame(() => { drawer.style.transform = 'translateX(0)'; });
    });
}

function closeLeadDrawer() {
  const drawer = document.getElementById('leadDrawer');
  drawer.style.transform = 'translateX(100%)';
  setTimeout(() => {
    drawer.style.display = 'none';
    document.getElementById('leadDrawerOverlay').style.display = 'none';
  }, 280);
}

function copyDrawerText(elId, btnId) {
  const text = document.getElementById(elId).textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById(btnId);
    const orig = btn.textContent;
    btn.textContent = '✅ Copied!';
    btn.style.background = '#059669';
    setTimeout(() => { btn.textContent = orig; btn.style.background = ''; }, 2000);
  });
}



