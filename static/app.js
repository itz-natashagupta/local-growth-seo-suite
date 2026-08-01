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
    body: JSON.stringify({ category, city, max_results: maxRes, only_no_website: noWeb })
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
            ? `<a href="${lead['Website']}" target="_blank" style="color:#006D77;text-decoration:underline;">${lead['Website'].replace(/^https?:\/\//, '').substring(0,30)}</a>`
            : '<span style="color:#9CA3AF;">No Website</span>';

          const mapsLink = lead['Google Maps Link'] && lead['Google Maps Link'] !== 'N/A'
            ? `<a href="${lead['Google Maps Link']}" target="_blank" style="color:#006D77;font-weight:bold;text-decoration:none;">🗺️ View</a>`
            : '—';

          rowsHtml += `
            <tr style="border-bottom:1px solid #E5E7EB;">
              <td style="padding:10px;text-align:center;font-weight:bold;color:#6B7280;">${idx + 1}</td>
              <td style="padding:10px;font-weight:600;">${lead['Business Name']}</td>
              <td style="padding:10px;text-align:center;"><span style="${rtgBadge}">${ratingStr}</span></td>
              <td style="padding:10px;text-align:center;">${lead['Number of Reviews'] || 'N/A'}</td>
              <td style="padding:10px;">${lead['Phone Number'] || 'N/A'}</td>
              <td style="padding:10px;font-size:12px;color:#4B5563;">${lead['Address'] || 'N/A'}</td>
              <td style="padding:10px;">${webLink}</td>
              <td style="padding:10px;text-align:center;">${mapsLink}</td>
            </tr>
          `;
        });

        tbody.innerHTML = rowsHtml;
        document.getElementById('scLeadsCard').style.display = 'block';
        document.getElementById('scLeadsCard').scrollIntoView({ behavior: 'smooth' });
      }
    });
}
