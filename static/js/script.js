document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const fetchBtn = document.getElementById('fetch-btn');

    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');

    const videoCard = document.getElementById('video-card');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const videoChannel = document.getElementById('video-channel');
    const videoDuration = document.getElementById('video-duration');

    const downloadBtn = document.getElementById('download-btn');
    const statusMessage = document.getElementById('status-message');
    const queuePanel = document.getElementById('queue-panel');
    const queueList = document.getElementById('queue-list');

    let currentUrl = '';
    let currentVideoTitle = '';

    // queue Map: jobId → { li: HTMLElement, pollTimer: number }
    const queue = new Map();

    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        hideStatus();
        videoCard.classList.add('hidden');
        loading.classList.remove('hidden');
        loadingText.textContent = window.I18N['ui.loading_info'];
        fetchBtn.disabled = true;
        currentUrl = url;

        try {
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || window.I18N['ui.error_info']);
            }

            videoThumbnail.src = data.thumbnail;
            videoTitle.textContent = data.title;
            videoChannel.textContent = data.channel;
            videoDuration.textContent = data.duration || '';
            currentVideoTitle = data.title;

            loading.classList.add('hidden');
            videoCard.classList.remove('hidden');

        } catch (error) {
            loading.classList.add('hidden');
            showStatus(error.message, 'error');
        } finally {
            fetchBtn.disabled = false;
        }
    });

    downloadBtn.addEventListener('click', async () => {
        if (!currentUrl) return;

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: currentUrl })
            });

            const data = await response.json();

            if (!response.ok) {
                showStatus(data.error || window.I18N['ui.error_download'], 'error');
                return;
            }

            addToQueue(data.job_id, currentVideoTitle);

        } catch (error) {
            showStatus(error.message, 'error');
        }
    });

    function addToQueue(jobId, title) {
        queuePanel.classList.remove('hidden');
        const emptyMsg = document.getElementById('queue-empty-msg');
        if (emptyMsg) emptyMsg.style.display = 'none';

        const li = document.createElement('li');
        li.className = 'queue-item';
        li.dataset.jobId = jobId;

        const titleEl = document.createElement('div');
        titleEl.className = 'queue-item-title';
        titleEl.textContent = title || jobId;

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'queue-cancel-btn';
        cancelBtn.textContent = window.I18N['ui.btn_cancel'];
        cancelBtn.addEventListener('click', () => cancelJob(jobId, cancelBtn));

        const progressWrapper = document.createElement('div');
        progressWrapper.className = 'queue-item-progress';

        const progressEl = document.createElement('progress');
        progressEl.value = 0;
        progressEl.max = 100;

        const speedEl = document.createElement('div');
        speedEl.className = 'queue-item-speed';

        progressWrapper.append(progressEl, speedEl);
        li.append(titleEl, cancelBtn, progressWrapper);
        queueList.appendChild(li);

        const pollTimer = setInterval(() => pollJob(jobId), 2000);
        queue.set(jobId, { li, pollTimer });
    }

    async function pollJob(jobId) {
        try {
            const res = await fetch(`/api/status/${jobId}`);
            const data = await res.json();
            updateQueueItem(jobId, data);
        } catch (_) {
            stopJobPolling(jobId);
        }
    }

    function updateQueueItem(jobId, statusData) {
        const entry = queue.get(jobId);
        if (!entry) return;
        const { li } = entry;

        const progressEl = li.querySelector('progress');
        const speedEl = li.querySelector('.queue-item-speed');
        const cancelBtn = li.querySelector('.queue-cancel-btn');

        if (statusData.status === 'running') {
            const pct = statusData.progress || 0;
            if (progressEl) progressEl.value = pct;
            if (speedEl) {
                speedEl.textContent = statusData.speed
                    ? window.I18N['ui.progress_speed']
                        .replace('{speed}', statusData.speed)
                        .replace('{eta}', statusData.eta ?? '?')
                    : window.I18N['ui.progress_label'].replace('{pct}', pct);
            }
        } else if (statusData.status === 'done') {
            stopJobPolling(jobId);
            if (cancelBtn) cancelBtn.remove();
            li.querySelector('.queue-item-progress')?.remove();

            const link = document.createElement('a');
            link.href = `/api/file/${jobId}`;
            link.textContent = window.I18N['ui.success_download'];
            link.className = 'queue-download-link';
            link.download = '';
            link.addEventListener('click', () => setTimeout(() => link.remove(), 100));
            li.appendChild(link);

        } else if (statusData.status === 'error' || statusData.status === 'cancelled') {
            stopJobPolling(jobId);
            if (cancelBtn) cancelBtn.remove();
            const msg = document.createElement('span');
            msg.className = 'queue-item-speed';
            msg.style.color = 'var(--primary-color)';
            msg.textContent = statusData.error || statusData.status;
            li.querySelector('.queue-item-progress')?.remove();
            li.appendChild(msg);
        }
    }

    async function cancelJob(jobId, cancelBtn) {
        cancelBtn.disabled = true;
        try {
            await fetch(`/api/status/${jobId}`, { method: 'DELETE' });
        } catch (_) { /* ignore */ }
    }

    function stopJobPolling(jobId) {
        const entry = queue.get(jobId);
        if (entry?.pollTimer) {
            clearInterval(entry.pollTimer);
        }
    }

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = '';
        statusMessage.classList.add('status-' + type);
        statusMessage.classList.remove('hidden');
    }

    function hideStatus() {
        statusMessage.classList.add('hidden');
    }
});
