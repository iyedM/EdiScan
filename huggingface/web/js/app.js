const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const submitBtn = document.getElementById('submit-btn');
const quickBtn = document.getElementById('quick-btn');
const uploadForm = document.getElementById('upload-form');
const loading = document.getElementById('loading');
const confidenceSlider = document.getElementById('confidence-slider');
const confidenceValue = document.getElementById('confidence-value');
const quickModeInput = document.getElementById('quick-mode-input');
const autoCopyToggle = document.getElementById('auto-copy-toggle');
const fileCountBadge = document.getElementById('file-count');
const fileList = document.getElementById('file-list');
const fileListItems = document.getElementById('file-list-items');

function setQuickMode() {
    if (quickModeInput) quickModeInput.value = 'on';
}

if (submitBtn) {
    submitBtn.addEventListener('click', () => {
        if (quickModeInput) quickModeInput.value = 'off';
    });
}

if (confidenceSlider) {
    confidenceSlider.addEventListener('input', (e) => {
        confidenceValue.textContent = Math.round(e.target.value * 100) + '%';
    });
}

if (dropZone) {
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            handleFilesSelect(files);
        }
    });
}

if (fileInput) {
    fileInput.addEventListener('change', e => {
        if (e.target.files.length) {
            handleFilesSelect(e.target.files);
        }
    });
}

function handleFilesSelect(files) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff', 'image/webp'];
    const validFiles = [];
    
    for (let file of files) {
        if (validTypes.some(type => file.type.includes(type.split('/')[1]))) {
            validFiles.push(file);
        }
    }
    
    if (validFiles.length === 0) {
        showToast('Aucun fichier valide', false);
        return;
    }
    
    if (fileCountBadge) {
        fileCountBadge.textContent = validFiles.length;
        fileCountBadge.style.display = 'inline';
    }
    
    if (fileList && fileListItems) {
        fileListItems.innerHTML = '';
        validFiles.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file.name;
            fileListItems.appendChild(li);
        });
        fileList.style.display = 'block';
    }
    
    if (validFiles.length === 1) {
        const reader = new FileReader();
        reader.onload = e => {
            const previewDisplay = document.getElementById('preview-display');
            const imageEmpty = document.getElementById('image-empty');
            
            document.querySelectorAll('.display-img').forEach(img => {
                img.classList.add('image-hidden');
            });
            
            if (imageEmpty) imageEmpty.style.display = 'none';
            
            if (previewDisplay) {
                previewDisplay.src = e.target.result;
                previewDisplay.classList.remove('image-hidden');
            }
        };
        reader.readAsDataURL(validFiles[0]);
    } else {
        const imageEmpty = document.getElementById('image-empty');
        if (imageEmpty) {
            imageEmpty.innerHTML = `<div class="empty-icon">📁</div><p>${validFiles.length} fichiers sélectionnés</p>`;
            imageEmpty.style.display = 'block';
        }
    }
    
    if (submitBtn) submitBtn.disabled = false;
    if (quickBtn) quickBtn.disabled = false;
}

function clearFiles() {
    if (fileInput) fileInput.value = '';
    if (fileCountBadge) fileCountBadge.style.display = 'none';
    if (fileList) fileList.style.display = 'none';
    if (fileListItems) fileListItems.innerHTML = '';
    if (submitBtn) submitBtn.disabled = true;
    if (quickBtn) quickBtn.disabled = true;
    
    const imageEmpty = document.getElementById('image-empty');
    if (imageEmpty) {
        imageEmpty.innerHTML = `<div class="empty-icon">🖼️</div><p>L'image apparaîtra ici</p>`;
        imageEmpty.style.display = 'block';
    }
    
    const previewDisplay = document.getElementById('preview-display');
    if (previewDisplay) previewDisplay.classList.add('image-hidden');
}

if (uploadForm) {
    uploadForm.addEventListener('submit', () => {
        const isQuickMode = quickModeInput && quickModeInput.value === 'on';
        const loadingText = document.querySelector('.loading-text');
        const fileCount = fileInput ? fileInput.files.length : 1;
        
        if (loadingText) {
            if (fileCount > 1) {
                loadingText.textContent = `Traitement de ${fileCount} images...`;
            } else if (isQuickMode) {
                loadingText.textContent = 'Scan rapide...';
            } else {
                loadingText.textContent = 'Analyse en cours...';
            }
        }
        
        if (loading) loading.classList.add('visible');
        animateLoadingSteps(isQuickMode);
    });
}

function animateLoadingSteps(isQuick = false) {
    const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
    let current = 0;
    const delay = isQuick ? 400 : 800;
    
    steps.forEach(step => {
        const el = document.getElementById(step);
        if (el) el.classList.remove('active', 'done');
    });
    
    const step2 = document.getElementById('step-2');
    if (step2) {
        step2.textContent = isQuick ? '⏭️ Prétraitement ignoré' : '✨ Prétraitement';
    }
    
    const interval = setInterval(() => {
        if (current > 0) {
            const prevStep = document.getElementById(steps[current - 1]);
            if (prevStep) {
                prevStep.classList.remove('active');
                prevStep.classList.add('done');
            }
        }
        if (current < steps.length) {
            const currentStep = document.getElementById(steps[current]);
            if (currentStep) currentStep.classList.add('active');
            current++;
        } else {
            clearInterval(interval);
        }
    }, delay);
}

function showImage(type) {
    const tabs = document.querySelectorAll('.image-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    const originalImg = document.getElementById('original-img');
    const detectedImg = document.getElementById('detected-img');
    
    if (type === 'original') {
        if (originalImg) originalImg.classList.remove('image-hidden');
        if (detectedImg) detectedImg.classList.add('image-hidden');
    } else {
        if (originalImg) originalImg.classList.add('image-hidden');
        if (detectedImg) detectedImg.classList.remove('image-hidden');
    }
}

function showBatchResult(index) {
    if (typeof batchData === 'undefined') return;
    
    const result = batchData[index];
    if (!result) return;
    
    const textOutput = document.getElementById('text-output');
    if (textOutput) textOutput.textContent = result.text;
    
    const statWords = document.getElementById('stat-words');
    const statLines = document.getElementById('stat-lines');
    const statChars = document.getElementById('stat-chars');
    const statDetections = document.getElementById('stat-detections');
    
    if (statWords) statWords.textContent = result.stats.word_count;
    if (statLines) statLines.textContent = result.stats.line_count;
    if (statChars) statChars.textContent = result.stats.char_count;
    if (statDetections) statDetections.textContent = result.stats.detection_count;
    
    document.querySelectorAll('.batch-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
}

function copyAllBatch() {
    if (typeof batchData === 'undefined') return;
    
    const allText = batchData.map((r, i) => 
        `=== ${r.original_filename} ===\n${r.text}`
    ).join('\n\n');
    
    navigator.clipboard.writeText(allText).then(() => {
        showToast(`${batchData.length} textes copiés !`, true);
    });
}

function copyText() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    navigator.clipboard.writeText(textOutput.textContent).then(() => {
        const copyBtn = document.getElementById('copy-btn');
        if (copyBtn) {
            copyBtn.classList.add('copied');
            copyBtn.innerHTML = '<span>✅</span><span>Copié!</span>';
            showToast('Texte copié !', true);
            setTimeout(() => {
                copyBtn.classList.remove('copied');
                copyBtn.innerHTML = '<span>📋</span><span>Copier</span>';
            }, 2000);
        }
    });
}

function downloadText() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const blob = new Blob([textOutput.textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ediscan-texte.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Fichier téléchargé !', true);
}

function clearAll() {
    window.location.href = '/';
}

function showToast(message, success = true) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.querySelector('.toast-message').textContent = message;
    toast.querySelector('.toast-icon').textContent = success ? '✅' : '❌';
    toast.classList.toggle('success', success);
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3000);
}

function quickCopy() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const quickCopyBtn = document.getElementById('quick-copy-btn');
    
    navigator.clipboard.writeText(textOutput.textContent).then(() => {
        if (quickCopyBtn) {
            quickCopyBtn.classList.remove('pulse');
            quickCopyBtn.classList.add('copied');
            quickCopyBtn.innerHTML = '<span class="icon">✅</span><span>Copié !</span>';
            showToast('Texte copié !', true);
            setTimeout(() => {
                quickCopyBtn.classList.remove('copied');
                quickCopyBtn.innerHTML = '<span class="icon">📋</span><span>Copie Rapide</span><span class="shortcut">Ctrl+Shift+C</span>';
            }, 2000);
        }
    });
}

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        const textOutput = document.getElementById('text-output');
        if (textOutput) quickCopy();
    }
    
    if (e.ctrlKey && e.key === 'v') {
        if (document.activeElement.tagName !== 'INPUT' && 
            document.activeElement.tagName !== 'TEXTAREA') {
            handlePasteShortcut();
        }
    }
});

async function handlePasteShortcut() {
    try {
        const clipboardItems = await navigator.clipboard.read();
        
        for (const item of clipboardItems) {
            const imageType = item.types.find(type => type.startsWith('image/'));
            
            if (imageType) {
                const blob = await item.getType(imageType);
                const file = new File([blob], `clipboard_${Date.now()}.png`, { type: imageType });
                
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                
                if (fileInput) {
                    fileInput.files = dataTransfer.files;
                    handleFilesSelect([file]);
                    showToast('Image collée !', true);
                }
                return;
            }
        }
        
        showToast('Aucune image dans le presse-papier', false);
    } catch (err) {
        console.error('Paste error:', err);
        showToast('Utilisez Ctrl+V sur la zone de dépôt', false);
    }
}

document.addEventListener('paste', async (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    
    for (let item of items) {
        if (item.type.startsWith('image/')) {
            e.preventDefault();
            
            const file = item.getAsFile();
            if (file) {
                const renamedFile = new File([file], `clipboard_${Date.now()}.png`, { type: file.type });
                
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(renamedFile);
                
                if (fileInput) {
                    fileInput.files = dataTransfer.files;
                    handleFilesSelect([renamedFile]);
                    showToast('Image collée !', true);
                }
            }
            return;
        }
    }
});

function loadFromHistory(entryId) {
    window.location.href = `/history/${entryId}`;
}

if (autoCopyToggle) {
    if (localStorage.getItem('autoCopy') === 'true') {
        autoCopyToggle.checked = true;
    }
    autoCopyToggle.addEventListener('change', (e) => {
        localStorage.setItem('autoCopy', e.target.checked);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const textOutput = document.getElementById('text-output');
    const autoCopyEnabled = localStorage.getItem('autoCopy') === 'true';
    
    if (textOutput && autoCopyEnabled && textOutput.textContent.trim()) {
        setTimeout(() => {
            quickCopy();
            showToast('Copie automatique !', true);
        }, 500);
    }
    
    if (typeof batchData !== 'undefined' && batchData.length > 0) {
        document.querySelector('.batch-item')?.classList.add('active');
    }
});
