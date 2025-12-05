from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import easyocr
import cv2
import numpy as np
import os
import json
import sqlite3
import threading
import time
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import uuid

# === CONFIGURATION ===
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
PROCESSED_FOLDER = os.environ.get('PROCESSED_FOLDER', 'processed')
DATABASE_FILE = os.environ.get('DATABASE_FILE', 'ediscan.db')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
MAX_FILE_AGE_HOURS = int(os.environ.get('MAX_FILE_AGE_HOURS', 24))
CLEANUP_INTERVAL_SECONDS = int(os.environ.get('CLEANUP_INTERVAL_SECONDS', 3600))
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')
DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'

# Indiquer à Flask que les templates sont dans ../web et les fichiers statiques
app = Flask(__name__, 
            template_folder='../web',
            static_folder='../web',
            static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB

# Vérifier si GPU disponible (CUDA)
import torch
GPU_AVAILABLE = torch.cuda.is_available()
print(f"🚀 GPU CUDA disponible: {GPU_AVAILABLE}")

# Initialiser le reader avec GPU si disponible
reader = easyocr.Reader(
    ['fr', 'en'],
    gpu=GPU_AVAILABLE,
    model_storage_directory='models',
    download_enabled=True
)


# ==========================================
# DATABASE - Historique des extractions
# ==========================================

def init_database():
    """Initialiser la base de données SQLite"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Table historique
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT,
            extracted_text TEXT,
            confidence REAL,
            word_count INTEGER,
            char_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            thumbnail_path TEXT,
            image_hash TEXT
        )
    ''')
    
    # Table cache pour éviter de re-OCR les mêmes images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocr_cache (
            image_hash TEXT PRIMARY KEY,
            extracted_text TEXT,
            confidence REAL,
            word_count INTEGER,
            char_count INTEGER,
            line_count INTEGER,
            detection_count INTEGER,
            detailed_results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Index pour recherche rapide par hash
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_hash ON ocr_cache(image_hash)')
    
    conn.commit()
    conn.close()
    print("📦 Base de données initialisée")
    print("💾 Cache OCR activé")


def save_to_history(entry_id, filename, original_filename, text, confidence, word_count, char_count, image_path, image_hash=None):
    """Sauvegarder une extraction dans l'historique"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO history (id, filename, original_filename, extracted_text, confidence, word_count, char_count, image_path, image_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (entry_id, filename, original_filename, text, confidence, word_count, char_count, image_path, image_hash))
    
    conn.commit()
    conn.close()


# ==========================================
# CACHE INTELLIGENT - Éviter de re-OCR
# ==========================================

def calculate_image_hash(filepath):
    """Calculer un hash unique pour une image"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        # Lire par blocs pour les grandes images
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_from_cache(image_hash):
    """Récupérer un résultat OCR depuis le cache"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ocr_cache WHERE image_hash = ?', (image_hash,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'text': row['extracted_text'],
            'confidence': row['confidence'],
            'word_count': row['word_count'],
            'char_count': row['char_count'],
            'line_count': row['line_count'],
            'detection_count': row['detection_count'],
            'detailed_results': json.loads(row['detailed_results']) if row['detailed_results'] else []
        }
    return None


def save_to_cache(image_hash, text, stats, detailed_results):
    """Sauvegarder un résultat OCR dans le cache"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO ocr_cache 
        (image_hash, extracted_text, confidence, word_count, char_count, line_count, detection_count, detailed_results)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        image_hash,
        text,
        stats['avg_confidence'],
        stats['word_count'],
        stats['char_count'],
        stats['line_count'],
        stats['detection_count'],
        json.dumps(detailed_results)
    ))
    
    conn.commit()
    conn.close()


def get_cache_stats():
    """Obtenir les statistiques du cache"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM ocr_cache')
    count = cursor.fetchone()[0]
    
    conn.close()
    return {'cached_images': count}


def clear_cache():
    """Vider le cache OCR"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ocr_cache')
    conn.commit()
    conn.close()


def get_history(limit=20):
    """Récupérer l'historique des extractions"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM history 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_history_entry(entry_id):
    """Récupérer une entrée spécifique de l'historique"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM history WHERE id = ?', (entry_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def delete_history_entry(entry_id):
    """Supprimer une entrée de l'historique"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM history WHERE id = ?', (entry_id,))
    
    conn.commit()
    conn.close()


def clear_history():
    """Vider tout l'historique"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM history')
    
    conn.commit()
    conn.close()


# ==========================================
# NETTOYAGE AUTOMATIQUE
# ==========================================

def cleanup_old_files():
    """Supprimer les fichiers plus anciens que MAX_FILE_AGE_HOURS"""
    folders = [UPLOAD_FOLDER, PROCESSED_FOLDER]
    cutoff_time = datetime.now() - timedelta(hours=MAX_FILE_AGE_HOURS)
    deleted_count = 0
    
    for folder in folders:
        if not os.path.exists(folder):
            continue
            
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            
            if os.path.isfile(filepath):
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_modified < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️ Erreur suppression {filepath}: {e}")
    
    if deleted_count > 0:
        print(f"🧹 Nettoyage: {deleted_count} fichiers supprimés")
    
    return deleted_count


def start_cleanup_scheduler():
    """Démarrer le scheduler de nettoyage en arrière-plan"""
    def cleanup_loop():
        while True:
            time.sleep(CLEANUP_INTERVAL_SECONDS)
            cleanup_old_files()
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    print(f"🔄 Nettoyage automatique activé (toutes les {CLEANUP_INTERVAL_SECONDS//3600}h)")


# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """Générer un nom de fichier unique"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'png'
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}"


def preprocess_image(image_path, output_path=None):
    """Prétraitement de l'image pour améliorer la qualité OCR"""
    img = Image.open(image_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    max_width = 2000
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 6, 6, 7, 21)
    
    if output_path:
        cv2.imwrite(output_path, img_cv)
        return output_path
    
    return img_cv


def sort_text_by_position(ocr_results, line_threshold=15):
    """Trier les résultats OCR par position spatiale"""
    if not ocr_results:
        return []
    
    text_items = []
    for (bbox, text, confidence) in ocr_results:
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        center_x = sum(x_coords) / 4
        top_y = min(y_coords)
        
        text_items.append({
            'text': text,
            'confidence': confidence,
            'center_x': center_x,
            'top_y': top_y,
            'bbox': bbox
        })
    
    text_items.sort(key=lambda x: x['top_y'])
    
    lines = []
    current_line = [text_items[0]]
    
    for item in text_items[1:]:
        if abs(item['top_y'] - current_line[0]['top_y']) < line_threshold:
            current_line.append(item)
        else:
            lines.append(current_line)
            current_line = [item]
    lines.append(current_line)
    
    sorted_lines = []
    for line in lines:
        sorted_line = sorted(line, key=lambda x: x['center_x'])
        sorted_lines.append(sorted_line)
    
    return sorted_lines


def format_text_output(sorted_lines, min_confidence=0.3):
    """Formater le texte extrait"""
    output_lines = []
    detailed_results = []
    
    for line in sorted_lines:
        line_texts = []
        for item in line:
            if item['confidence'] >= min_confidence:
                line_texts.append(item['text'])
                detailed_results.append({
                    'text': item['text'],
                    'confidence': round(item['confidence'] * 100, 1),
                    'bbox': [[int(p[0]), int(p[1])] for p in item['bbox']]
                })
        
        if line_texts:
            output_lines.append(' '.join(line_texts))
    
    return '\n'.join(output_lines), detailed_results


def draw_boxes_on_image(image_path, ocr_results, output_path):
    """Dessiner les boîtes de détection sur l'image"""
    img = cv2.imread(image_path)
    
    for (bbox, text, confidence) in ocr_results:
        pts = np.array(bbox, dtype=np.int32)
        color = (int(255 * (1 - confidence)), int(255 * confidence), 0)
        cv2.polylines(img, [pts], True, color, 2)
        conf_text = f"{int(confidence * 100)}%"
        cv2.putText(img, conf_text, (pts[0][0], pts[0][1] - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    cv2.imwrite(output_path, img)
    return output_path


def calculate_stats(detailed_results, full_text):
    """Calculer les statistiques du texte extrait"""
    if not detailed_results:
        return {
            'char_count': 0,
            'word_count': 0,
            'line_count': 0,
            'avg_confidence': 0,
            'detection_count': 0
        }
    
    confidences = [r['confidence'] for r in detailed_results]
    words = full_text.split()
    lines = [l for l in full_text.split('\n') if l.strip()]
    
    return {
        'char_count': len(full_text),
        'word_count': len(words),
        'line_count': len(lines),
        'avg_confidence': round(sum(confidences) / len(confidences), 1),
        'detection_count': len(detailed_results)
    }


def process_single_image(filepath, filename, original_filename, min_confidence, use_preprocessing, quick_mode):
    """Traiter une seule image et retourner les résultats"""
    
    # Calculer le hash de l'image pour le cache
    image_hash = calculate_image_hash(filepath)
    from_cache = False
    
    # Vérifier si l'image est déjà dans le cache
    cached_result = get_from_cache(image_hash)
    
    if cached_result:
        # Utiliser le résultat en cache
        ocr_text = cached_result['text']
        detailed_results = cached_result['detailed_results']
        stats = {
            'avg_confidence': cached_result['confidence'],
            'word_count': cached_result['word_count'],
            'char_count': cached_result['char_count'],
            'line_count': cached_result['line_count'],
            'detection_count': cached_result['detection_count']
        }
        from_cache = True
        print(f"⚡ Cache HIT pour {original_filename}")
        
        # On a besoin des résultats OCR bruts pour dessiner les boîtes
        # Donc on fait quand même un OCR rapide pour les boîtes
        result = reader.readtext(filepath, paragraph=False, min_size=20, canvas_size=1280, mag_ratio=1.0)
    else:
        # Pas en cache - faire l'OCR
        print(f"🔍 OCR pour {original_filename}...")
        
        if quick_mode:
            ocr_input = filepath
            result = reader.readtext(
                ocr_input,
                paragraph=False,
                min_size=20,
                text_threshold=0.6,
                low_text=0.3,
                link_threshold=0.3,
                canvas_size=1280,
                mag_ratio=1.0
            )
        else:
            if use_preprocessing:
                processed_path = os.path.join(PROCESSED_FOLDER, f"pre_{filename}")
                preprocess_image(filepath, processed_path)
                ocr_input = processed_path
            else:
                ocr_input = filepath
            
            result = reader.readtext(
                ocr_input,
                paragraph=False,
                min_size=10,
                text_threshold=0.7,
                low_text=0.4,
                link_threshold=0.4,
                canvas_size=2560,
                mag_ratio=1.5
            )
        
        sorted_lines = sort_text_by_position(result)
        ocr_text, detailed_results = format_text_output(sorted_lines, min_confidence)
        stats = calculate_stats(detailed_results, ocr_text)
        
        # Sauvegarder dans le cache
        save_to_cache(image_hash, ocr_text, stats, detailed_results)
        print(f"💾 Sauvegardé dans le cache")
    
    # Dessiner les boîtes sur l'image
    boxed_filename = f"boxed_{filename}"
    boxed_path = os.path.join(PROCESSED_FOLDER, boxed_filename)
    draw_boxes_on_image(filepath, result, boxed_path)
    
    # Sauvegarder dans l'historique
    entry_id = str(uuid.uuid4())[:12]
    save_to_history(
        entry_id=entry_id,
        filename=filename,
        original_filename=original_filename,
        text=ocr_text,
        confidence=stats['avg_confidence'],
        word_count=stats['word_count'],
        char_count=stats['char_count'],
        image_path=filepath,
        image_hash=image_hash
    )
    
    return {
        'id': entry_id,
        'filename': filename,
        'original_filename': original_filename,
        'text': ocr_text,
        'stats': stats,
        'detailed_results': detailed_results,
        'uploaded_image': url_for('uploaded_file', filename=filename),
        'processed_image': url_for('processed_file', filename=boxed_filename),
        'from_cache': from_cache
    }


# ==========================================
# ROUTES
# ==========================================

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir les images uploadées"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', UPLOAD_FOLDER), 
        filename
    )


@app.route('/processed/<filename>')
def processed_file(filename):
    """Servir les images traitées"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', PROCESSED_FOLDER), 
        filename
    )


@app.route('/', methods=['GET', 'POST'])
def index():
    """Page principale"""
    ocr_text = ""
    uploaded_image = None
    processed_image = None
    uploaded_filename = None
    stats = None
    detailed_results = []
    batch_results = []
    from_cache = False
    
    # Récupérer l'historique et stats cache
    history = get_history(10)
    cache_stats = get_cache_stats()
    
    if request.method == 'POST':
        files = request.files.getlist('file')
        
        if not files or files[0].filename == '':
            return redirect(request.url)
        
        # Créer les dossiers si nécessaire
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
        
        # Récupérer les paramètres
        min_confidence = float(request.form.get('min_confidence', 0.3))
        use_preprocessing = request.form.get('preprocessing', 'on') == 'on'
        quick_mode = request.form.get('quick_mode') == 'on'
        
        # Traiter chaque fichier
        for file in files:
            if file and allowed_file(file.filename):
                original_filename = file.filename
                filename = generate_unique_filename(original_filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                result = process_single_image(
                    filepath, filename, original_filename,
                    min_confidence, use_preprocessing, quick_mode
                )
                batch_results.append(result)
        
        # Si une seule image, afficher comme avant
        from_cache = False
        if len(batch_results) == 1:
            r = batch_results[0]
            ocr_text = r['text']
            uploaded_image = r['uploaded_image']
            processed_image = r['processed_image']
            uploaded_filename = r['original_filename']
            stats = r['stats']
            detailed_results = r['detailed_results']
            from_cache = r.get('from_cache', False)
            batch_results = []  # Pas de mode batch
        
        # Refresh history
        history = get_history(10)
        cache_stats = get_cache_stats()
    
    return render_template('index.html', 
                         ocr_text=ocr_text, 
                         uploaded_image=uploaded_image,
                         processed_image=processed_image,
                         uploaded_filename=uploaded_filename,
                         stats=stats,
                         detailed_results=json.dumps(detailed_results),
                         gpu_available=GPU_AVAILABLE,
                         history=history,
                         batch_results=batch_results,
                         from_cache=from_cache,
                         cache_stats=cache_stats)


@app.route('/history')
def history_page():
    """Page de l'historique"""
    history = get_history(50)
    return render_template('history.html', 
                         history=history,
                         gpu_available=GPU_AVAILABLE)


@app.route('/history/<entry_id>')
def history_detail(entry_id):
    """Détail d'une entrée de l'historique"""
    entry = get_history_entry(entry_id)
    if not entry:
        return redirect(url_for('history_page'))
    
    return render_template('history_detail.html',
                         entry=entry,
                         gpu_available=GPU_AVAILABLE)


@app.route('/api/history', methods=['GET'])
def api_get_history():
    """API: Récupérer l'historique"""
    limit = request.args.get('limit', 20, type=int)
    history = get_history(limit)
    return jsonify(history)


@app.route('/api/history/<entry_id>', methods=['DELETE'])
def api_delete_history(entry_id):
    """API: Supprimer une entrée de l'historique"""
    delete_history_entry(entry_id)
    return jsonify({'success': True})


@app.route('/api/history/clear', methods=['POST'])
def api_clear_history():
    """API: Vider tout l'historique"""
    clear_history()
    return jsonify({'success': True})


@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    """API: Forcer le nettoyage des fichiers"""
    deleted = cleanup_old_files()
    return jsonify({'deleted': deleted})


@app.route('/api/cache/stats', methods=['GET'])
def api_cache_stats():
    """API: Statistiques du cache"""
    stats = get_cache_stats()
    return jsonify(stats)


@app.route('/api/cache/clear', methods=['POST'])
def api_clear_cache():
    """API: Vider le cache OCR"""
    clear_cache()
    return jsonify({'success': True, 'message': 'Cache vidé'})


@app.route('/api/ocr', methods=['POST'])
def api_ocr():
    """API endpoint pour l'OCR"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    original_filename = file.filename
    filename = generate_unique_filename(original_filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    min_confidence = float(request.form.get('min_confidence', 0.3))
    quick_mode = request.form.get('quick_mode') == 'on'
    
    result = process_single_image(
        filepath, filename, original_filename,
        min_confidence, False, quick_mode
    )
    
    return jsonify(result)


@app.route('/api/batch', methods=['POST'])
def api_batch_ocr():
    """API: Traitement batch de plusieurs images"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files provided'}), 400
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    min_confidence = float(request.form.get('min_confidence', 0.3))
    quick_mode = request.form.get('quick_mode') == 'on'
    
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            original_filename = file.filename
            filename = generate_unique_filename(original_filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            result = process_single_image(
                filepath, filename, original_filename,
                min_confidence, False, quick_mode
            )
            results.append(result)
    
    return jsonify({'results': results, 'count': len(results)})


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    # Initialiser la base de données
    init_database()
    
    # Créer les dossiers
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    # Démarrer le nettoyage automatique
    start_cleanup_scheduler()
    
    # Premier nettoyage au démarrage
    cleanup_old_files()
    
    print("=" * 50)
    print("🔍 EdiScan - OCR Intelligent")
    print(f"🖥️  GPU CUDA: {'✅ Activé' if GPU_AVAILABLE else '❌ Désactivé (CPU)'}")
    print(f"🌐 Langues: Français, Anglais")
    print(f"📦 Base de données: {DATABASE_FILE}")
    print(f"🧹 Nettoyage auto: fichiers > {MAX_FILE_AGE_HOURS}h")
    print(f"🐳 Mode: {'Production' if not DEBUG else 'Développement'}")
    print(f"🌐 Serveur: http://{HOST}:{PORT}")
    print("=" * 50)
    
    app.run(debug=DEBUG, host=HOST, port=PORT)
