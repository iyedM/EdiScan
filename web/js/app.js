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

// === QUICK MODE ===
function setQuickMode() {
    quickModeInput.value = 'on';
}

// Reset quick mode on normal submit
if (submitBtn) {
    submitBtn.addEventListener('click', () => {
        quickModeInput.value = 'off';
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
    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag events
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
            handleFileSelect(files[0]);
        }
    });
}

// === FILE INPUT ===
if (fileInput) {
    fileInput.addEventListener('change', e => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// === FILE HANDLER ===
function handleFileSelect(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff', 'image/webp'];
    if (!validTypes.some(type => file.type.includes(type.split('/')[1]))) {
        showToast('Format non supporté', false);
        return;
    }

    // Show preview in center card
    const reader = new FileReader();
    reader.onload = e => {
        const previewDisplay = document.getElementById('preview-display');
        const imageEmpty = document.getElementById('image-empty');
        
        // Hide other images
        document.querySelectorAll('.display-img').forEach(img => {
            img.classList.add('image-hidden');
        });
        
        if (imageEmpty) imageEmpty.style.display = 'none';
        
        previewDisplay.src = e.target.result;
        previewDisplay.classList.remove('image-hidden');
        submitBtn.disabled = false;
        quickBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// === FORM SUBMIT ===
if (uploadForm) {
    uploadForm.addEventListener('submit', () => {
        const isQuickMode = quickModeInput.value === 'on';
        const loadingText = document.querySelector('.loading-text');
        
        if (isQuickMode) {
            loadingText.textContent = '⚡ Scan rapide en cours...';
        } else {
            loadingText.textContent = 'Analyse en cours...';
        }
        
        loading.classList.add('visible');
        animateLoadingSteps(isQuickMode);
    });
}

// === LOADING ANIMATION ===
function animateLoadingSteps(isQuick = false) {
    const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
    let current = 0;
    
    // En mode rapide, on saute l'étape 2 (prétraitement) et on va plus vite
    const delay = isQuick ? 400 : 800;
    
    // Reset all steps
    steps.forEach(step => {
        const el = document.getElementById(step);
        if (el) {
            el.classList.remove('active', 'done');
        }
    });
    
    // Skip preprocessing step in quick mode
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
            if (currentStep) {
                currentStep.classList.add('active');
            }
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
    event.target.classList.add('active');
    
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

// === COPY TEXT ===
function copyText() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const text = textOutput.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
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
    
    const text = textOutput.textContent;
    
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
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
    
    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

// === QUICK COPY ===
function quickCopy() {
    const textOutput = document.getElementById('text-output');
    if (!textOutput) return;
    
    const text = textOutput.textContent;
    const quickCopyBtn = document.getElementById('quick-copy-btn');
    
    navigator.clipboard.writeText(text).then(() => {
        if (quickCopyBtn) {
            // Update button state
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
    // Ctrl+Shift+C = Quick Copy
    if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        e.preventDefault();
        const textOutput = document.getElementById('text-output');
        if (textOutput) {
            quickCopy();
        }
    }
});

// === AUTO COPY PREFERENCE ===
if (autoCopyToggle) {
    // Load saved preference
    if (localStorage.getItem('autoCopy') === 'true') {
        autoCopyToggle.checked = true;
    }

    // Save preference
    autoCopyToggle.addEventListener('change', (e) => {
        localStorage.setItem('autoCopy', e.target.checked);
    });
}

// === INIT ON DOM READY ===
document.addEventListener('DOMContentLoaded', () => {
    const textOutput = document.getElementById('text-output');
    const autoCopyEnabled = localStorage.getItem('autoCopy') === 'true';
    
    // Auto-copy if text exists and auto-copy is enabled
    if (textOutput && autoCopyEnabled && textOutput.textContent.trim()) {
        setTimeout(() => {
            quickCopy();
            showToast('⚡ Copie automatique effectuée !', true);
        }, 500);
    }
});

