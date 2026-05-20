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
        loadingText.textContent = '비디오 정보를 불러오는 중...';
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
                throw new Error(data.error || '정보를 불러오는데 실패했습니다.');
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

    downloadBtn.addEventListener('click', async () => {
        if (!currentUrl) return;

        // Update Button State
        const originalBtnText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = `
            <div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div>
            다운로드 중...
        `;
        downloadBtn.classList.add('downloading');
        hideStatus();

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: currentUrl })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '다운로드에 실패했습니다.');
            }

            showStatus(`성공! 파일 경로: ${data.filepath}`, 'success');

        } catch (error) {
            showStatus(error.message, 'error');
        } finally {
            downloadBtn.innerHTML = originalBtnText;
            downloadBtn.classList.remove('downloading');
        }
    });

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = ''; // remove hidden and other classes
        statusMessage.classList.add(`status-${type}`);
        statusMessage.classList.remove('hidden');
    }

    function hideStatus() {
        statusMessage.classList.add('hidden');
    }
});
