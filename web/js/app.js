/* =========================================
   EdiScan - JavaScript Application
   ========================================= */

// === DOM ELEMENTS ===
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

// === QUICK MODE ===
function setQuickMode() {
    if (quickModeInput) quickModeInput.value = 'on';
}

// Reset quick mode on normal submit
if (submitBtn) {
    submitBtn.addEventListener('click', () => {
        if (quickModeInput) quickModeInput.value = 'off';
    });
}

// === CONFIDENCE SLIDER ===
if (confidenceSlider) {
    confidenceSlider.addEventListener('input', (e) => {
        confidenceValue.textContent = Math.round(e.target.value * 100) + '%';
    });
}

// === DRAG & DROP ===
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

// === FILE INPUT ===
if (fileInput) {
    fileInput.addEventListener('change', e => {
        if (e.target.files.length) {
            handleFilesSelect(e.target.files);
        }
    });
}

// === FILE HANDLER (Multi-file) ===
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
    
    // Update file count badge
    if (fileCountBadge) {
        fileCountBadge.textContent = validFiles.length;
        fileCountBadge.style.display = 'inline';
    }
    
    // Show file list
    if (fileList && fileListItems) {
        fileListItems.innerHTML = '';
        validFiles.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file.name;
            fileListItems.appendChild(li);
        });
        fileList.style.display = 'block';
    }
    
    // Show preview for first file
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
        // Multiple files - hide single preview
        const imageEmpty = document.getElementById('image-empty');
        if (imageEmpty) {
            imageEmpty.innerHTML = `<div class="empty-icon">📁</div><p>${validFiles.length} fichiers sélectionnés</p>`;
            imageEmpty.style.display = 'block';
        }
    }
    
    // Enable buttons
    if (submitBtn) submitBtn.disabled = false;
    if (quickBtn) quickBtn.disabled = false;
}

// === CLEAR FILES ===
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

// === FORM SUBMIT ===
if (uploadForm) {
    uploadForm.addEventListener('submit', () => {
        const isQuickMode = quickModeInput && quickModeInput.value === 'on';
        const loadingText = document.querySelector('.loading-text');
        const fileCount = fileInput ? fileInput.files.length : 1;
        
        if (loadingText) {
            if (fileCount > 1) {
                loadingText.textContent = `⚡ Traitement de ${fileCount} images...`;
            } else if (isQuickMode) {
                loadingText.textContent = '⚡ Scan rapide en cours...';
            } else {
                loadingText.textContent = 'Analyse en cours...';
            }
        }
        
        if (loading) loading.classList.add('visible');
        animateLoadingSteps(isQuickMode);
    });
}

// === LOADING ANIMATION ===
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

// === IMAGE TOGGLE ===
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

// === BATCH RESULTS ===
function showBatchResult(index) {
    if (typeof batchData === 'undefined') return;
    
    const result = batchData[index];
    if (!result) return;
    
    // Update text output
    const textOutput = document.getElementById('text-output');
    if (textOutput) textOutput.textContent = result.text;
    
    // Update stats
    const statWords = document.getElementById('stat-words');
    const statLines = document.getElementById('stat-lines');
    const statChars = document.getElementById('stat-chars');
    const statDetections = document.getElementById('stat-detections');
    
    if (statWords) statWords.textContent = result.stats.word_count;
    if (statLines) statLines.textContent = result.stats.line_count;
    if (statChars) statChars.textContent = result.stats.char_count;
    if (statDetections) statDetections.textContent = result.stats.detection_count;
    
    // Highlight active batch item
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
        showToast(`📋 ${batchData.length} textes copiés !`, true);
    });
}

// === COPY TEXT ===
function copyText() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    navigator.clipboard.writeText(textOutput.textContent).then(() => {
        const copyBtn = document.getElementById('copy-btn');
        if (copyBtn) {
            copyBtn.classList.add('copied');
            copyBtn.innerHTML = '<span>✅</span><span>Copié!</span>';
            showToast('Texte copié dans le presse-papier !', true);
            setTimeout(() => {
                copyBtn.classList.remove('copied');
                copyBtn.innerHTML = '<span>📋</span><span>Copier</span>';
            }, 2000);
        }
    });
}

// === DOWNLOAD TEXT ===
function downloadText() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const blob = new Blob([textOutput.textContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ediscan-texte-extrait.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Fichier téléchargé !', true);
}

// === CLEAR ALL ===
function clearAll() {
    window.location.href = '/';
}

// === TOAST NOTIFICATION ===
function showToast(message, success = true) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.querySelector('.toast-message').textContent = message;
    toast.querySelector('.toast-icon').textContent = success ? '✅' : '❌';
    toast.classList.toggle('success', success);
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3000);
}

// === QUICK COPY ===
function quickCopy() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const quickCopyBtn = document.getElementById('quick-copy-btn');
    
    navigator.clipboard.writeText(textOutput.textContent).then(() => {
        if (quickCopyBtn) {
            quickCopyBtn.classList.remove('pulse');
            quickCopyBtn.classList.add('copied');
            quickCopyBtn.innerHTML = '<span class="icon">✅</span><span>Copié !</span>';
            showToast('📋 Texte copié dans le presse-papier !', true);
            setTimeout(() => {
                quickCopyBtn.classList.remove('copied');
                quickCopyBtn.innerHTML = '<span class="icon">📋</span><span>Copie Rapide</span><span class="shortcut">Ctrl+Shift+C</span>';
            }, 2000);
        }
    });
}

// === KEYBOARD SHORTCUTS ===
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        const textOutput = document.getElementById('text-output');
        if (textOutput) quickCopy();
    }
});

// === HISTORY ===
function loadFromHistory(entryId) {
    window.location.href = `/history/${entryId}`;
}

// === AUTO COPY PREFERENCE ===
if (autoCopyToggle) {
    if (localStorage.getItem('autoCopy') === 'true') {
        autoCopyToggle.checked = true;
    }
    autoCopyToggle.addEventListener('change', (e) => {
        localStorage.setItem('autoCopy', e.target.checked);
    });
}

// === INIT ON DOM READY ===
document.addEventListener('DOMContentLoaded', () => {
    const textOutput = document.getElementById('text-output');
    const autoCopyEnabled = localStorage.getItem('autoCopy') === 'true';
    
    if (textOutput && autoCopyEnabled && textOutput.textContent.trim()) {
        setTimeout(() => {
            quickCopy();
            showToast('⚡ Copie automatique effectuée !', true);
        }, 500);
    }
    
    // Initialize first batch result if exists
    if (typeof batchData !== 'undefined' && batchData.length > 0) {
        document.querySelector('.batch-item')?.classList.add('active');
    }
});
