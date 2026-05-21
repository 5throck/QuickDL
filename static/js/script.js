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

    let currentUrl = '';

    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        // Reset UI
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

            // Update UI with video info
            videoThumbnail.src = data.thumbnail;
            videoTitle.textContent = data.title;
            videoChannel.textContent = data.channel;
            videoDuration.textContent = data.duration || '';

            loading.classList.add('hidden');
            videoCard.classList.remove('hidden');

        } catch (error) {
            loading.classList.add('hidden');
            showStatus(error.message, 'error');
        } finally {
            fetchBtn.disabled = false;
        }
    });

    function setDownloadingState() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.style.cssText = 'width:20px;height:20px;border-width:2px;display:inline-block;vertical-align:middle;';
        downloadBtn.replaceChildren(spinner, document.createTextNode(' ' + window.I18N['ui.downloading']));
        downloadBtn.classList.add('downloading');
        downloadBtn.disabled = true;
    }

    function resetDownloadBtn() {
        downloadBtn.textContent = window.I18N['ui.btn_download'];
        downloadBtn.classList.remove('downloading');
        downloadBtn.disabled = false;
    }

    downloadBtn.addEventListener('click', async () => {
        if (!currentUrl) return;

        setDownloadingState();
        hideStatus();

        let pollTimer = null;

        function stopPolling() {
            if (pollTimer !== null) {
                clearInterval(pollTimer);
                pollTimer = null;
            }
            resetDownloadBtn();
        }

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: currentUrl })
            });

            const data = await response.json();

            if (!response.ok) {
                resetDownloadBtn();
                showStatus(data.error || window.I18N['ui.error_download'], 'error');
                return;
            }

            const jobId = data.job_id;

            pollTimer = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/api/status/${jobId}`);
                    const statusData = await statusRes.json();

                    if (statusData.status === 'done') {
                        stopPolling();
                        const link = document.createElement('a');
                        link.href = `/api/file/${jobId}`;
                        link.textContent = window.I18N['ui.success_download'];
                        link.download = '';
                        link.addEventListener('click', () => {
                            setTimeout(() => link.remove(), 100);  // disable after first click
                        });
                        statusMessage.replaceChildren(link);
                        statusMessage.className = '';
                        statusMessage.classList.add('status-success');
                        statusMessage.classList.remove('hidden');
                    } else if (statusData.status === 'error') {
                        stopPolling();
                        showStatus(statusData.error || window.I18N['ui.error_download'], 'error');
                    }
                } catch (_) {
                    stopPolling();
                    showStatus(window.I18N['ui.error_download'], 'error');
                }
            }, 2000);

        } catch (error) {
            resetDownloadBtn();
            showStatus(error.message, 'error');
        }
    });

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = ''; // remove hidden and other classes
        statusMessage.classList.add('status-' + type);
        statusMessage.classList.remove('hidden');
    }

    function hideStatus() {
        statusMessage.classList.add('hidden');
    }
});
