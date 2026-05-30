const startBtn = document.getElementById('startBtn');
const refreshBtn = document.getElementById('refreshBtn');
const progressBar = document.getElementById('progressBar');
const progressRing = document.getElementById('progressRing');
const statusText = document.getElementById('statusText');
const doneText = document.getElementById('doneText');
const totalText = document.getElementById('totalText');
const currentText = document.getElementById('currentText');
const speedText = document.getElementById('speedText');
const etaText = document.getElementById('etaText');
const downloadList = document.getElementById('downloadList');
const failedCard = document.getElementById('failedCard');
const failedList = document.getElementById('failedList');

let polling = null;

function setPercent(percent) {
  const safePercent = Math.max(0, Math.min(100, Number(percent) || 0));
  const rounded = safePercent.toFixed(1);
  progressBar.style.width = `${safePercent}%`;
  progressRing.style.background = `conic-gradient(var(--primary) ${safePercent * 3.6}deg, var(--ring) 0deg)`;
  progressRing.setAttribute('data-label', `${rounded}%`);
}

function renderFiles(files = []) {
  if (!files.length) {
    downloadList.className = 'download-list empty';
    downloadList.innerHTML = `
      <i class="fa-regular fa-folder-open"></i>
      <p>No videos downloaded yet.</p>
    `;
    return;
  }

  downloadList.className = 'download-list';
  downloadList.innerHTML = files.map(file => `
    <article class="video-item">
      <div class="video-icon"><i class="fa-solid fa-video"></i></div>
      <div>
        <p class="video-name">${escapeHtml(file.name)}</p>
        <p class="video-size">${file.size} MB</p>
      </div>
    </article>
  `).join('');
}

function renderFailures(failed = []) {
  if (!failed.length) {
    failedCard.hidden = true;
    failedList.innerHTML = '';
    return;
  }

  failedCard.hidden = false;
  failedList.innerHTML = failed.map(item => `
    <li><strong>${escapeHtml(item.url)}</strong><br><small>${escapeHtml(item.error)}</small></li>
  `).join('');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

async function fetchProgress() {
  try {
    const response = await fetch('/progress');
    const data = await response.json();

    setPercent(data.percent);
    statusText.textContent = data.status || 'idle';
    doneText.textContent = data.done || 0;
    totalText.textContent = data.total || 0;
    currentText.textContent = data.current || data.message || 'Ready to download';
    speedText.textContent = data.speed || '0';
    etaText.textContent = data.eta || '0';
    renderFiles(data.downloaded_files || []);
    renderFailures(data.failed || []);

    startBtn.disabled = data.status === 'downloading';
    startBtn.innerHTML = data.status === 'downloading'
      ? '<i class="fa-solid fa-spinner fa-spin"></i> Downloading...'
      : '<i class="fa-solid fa-play"></i> Start Download';

    if (data.status === 'completed' && polling) {
      clearInterval(polling);
      polling = null;
    }
  } catch (error) {
    console.error(error);
  }
}

async function startDownload() {
  startBtn.disabled = true;
  startBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Starting...';

  const response = await fetch('/start', { method: 'POST' });
  const data = await response.json();

  if (!response.ok) {
    alert(data.message || 'Download could not start');
  }

  fetchProgress();
  if (!polling) {
    polling = setInterval(fetchProgress, 1000);
  }
}

startBtn.addEventListener('click', startDownload);
refreshBtn.addEventListener('click', fetchProgress);
fetchProgress();
