from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import easyocr
import cv2
import numpy as np
import os
import json
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

# Indiquer à Flask que les templates sont dans ../web et les fichiers statiques
app = Flask(__name__, 
            template_folder='../web',
            static_folder='../web',
            static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Vérifier si GPU disponible (CUDA)
import torch
GPU_AVAILABLE = torch.cuda.is_available()
print(f"🚀 GPU CUDA disponible: {GPU_AVAILABLE}")

# Initialiser le reader avec GPU si disponible
# Note: Arabe incompatible avec Français, utiliser séparément si besoin
reader = easyocr.Reader(
    ['fr', 'en'],  # Français et Anglais
    gpu=GPU_AVAILABLE,
    model_storage_directory='models',
    download_enabled=True
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path, output_path=None):
    """
    Prétraitement de l'image pour améliorer la qualité OCR
    - Redimensionnement intelligent
    - Amélioration du contraste
    - Réduction du bruit
    - Binarisation adaptative
    """
    # Charger l'image avec PIL
    img = Image.open(image_path)
    
    # Convertir en RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Redimensionner si l'image est trop grande (max 2000px de large)
    max_width = 2000
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Améliorer le contraste
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)
    
    # Améliorer la netteté
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    # Convertir en numpy pour OpenCV
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Débruitage
    img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 6, 6, 7, 21)
    
    # Sauvegarder l'image prétraitée si chemin fourni
    if output_path:
        cv2.imwrite(output_path, img_cv)
        return output_path
    
    return img_cv


def sort_text_by_position(ocr_results, line_threshold=15):
    """
    Trier les résultats OCR par position spatiale:
    - D'abord par ligne (haut vers bas)
    - Puis par colonne (gauche vers droite)
    - Regrouper les textes sur la même ligne
    """
    if not ocr_results:
        return []
    
    # Extraire les informations de position
    text_items = []
    for (bbox, text, confidence) in ocr_results:
        # Calculer le centre de la boîte
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        center_x = sum(x_coords) / 4
        center_y = sum(y_coords) / 4
        top_y = min(y_coords)
        
        text_items.append({
            'text': text,
            'confidence': confidence,
            'center_x': center_x,
            'center_y': center_y,
            'top_y': top_y,
            'bbox': bbox
        })
    
    # Trier par position Y (haut vers bas)
    text_items.sort(key=lambda x: x['top_y'])
    
    # Regrouper par lignes
    lines = []
    current_line = [text_items[0]]
    
    for item in text_items[1:]:
        # Si le texte est sur la même ligne (écart Y < seuil)
        if abs(item['top_y'] - current_line[0]['top_y']) < line_threshold:
            current_line.append(item)
        else:
            # Nouvelle ligne
            lines.append(current_line)
            current_line = [item]
    lines.append(current_line)
    
    # Trier chaque ligne par position X (gauche vers droite)
    sorted_lines = []
    for line in lines:
        sorted_line = sorted(line, key=lambda x: x['center_x'])
        sorted_lines.append(sorted_line)
    
    return sorted_lines


def format_text_output(sorted_lines, min_confidence=0.3):
    """
    Formater le texte extrait en texte lisible
    - Filtrer par confiance minimale
    - Joindre les mots sur la même ligne
    - Détecter les paragraphes
    """
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
    """
    Dessiner les boîtes de détection sur l'image
    """
    img = cv2.imread(image_path)
    
    for (bbox, text, confidence) in ocr_results:
        # Convertir les points en format OpenCV
        pts = np.array(bbox, dtype=np.int32)
        
        # Couleur basée sur la confiance (vert = haute, rouge = basse)
        color = (
            int(255 * (1 - confidence)),  # B
            int(255 * confidence),         # G
            0                              # R
        )
        
        # Dessiner le polygone
        cv2.polylines(img, [pts], True, color, 2)
        
        # Ajouter le pourcentage de confiance
        conf_text = f"{int(confidence * 100)}%"
        cv2.putText(img, conf_text, (pts[0][0], pts[0][1] - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    cv2.imwrite(output_path, img)
    return output_path


def calculate_stats(detailed_results, full_text):
    """
    Calculer les statistiques du texte extrait
    """
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Servir les images uploadées"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', UPLOAD_FOLDER), 
        filename
    )


@app.route('/processed/<filename>')
def processed_file(filename):
    """Servir les images traitées avec les boîtes"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', PROCESSED_FOLDER), 
        filename
    )


@app.route('/', methods=['GET', 'POST'])
def index():
    ocr_text = ""
    uploaded_image = None
    processed_image = None
    uploaded_filename = None
    stats = None
    detailed_results = []
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Créer les dossiers si nécessaire
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Récupérer les paramètres
            min_confidence = float(request.form.get('min_confidence', 0.3))
            use_preprocessing = request.form.get('preprocessing', 'on') == 'on'
            quick_mode = request.form.get('quick_mode') == 'on'
            
            # Mode rapide : paramètres optimisés pour la vitesse
            if quick_mode:
                # Pas de prétraitement en mode rapide
                ocr_input = filepath
                
                # OCR rapide - paramètres légers
                result = reader.readtext(
                    ocr_input,
                    paragraph=False,
                    min_size=20,          # Ignore les petits caractères
                    text_threshold=0.6,   # Seuil plus bas
                    low_text=0.3,
                    link_threshold=0.3,
                    canvas_size=1280,     # Canvas réduit = plus rapide
                    mag_ratio=1.0         # Pas d'agrandissement
                )
            else:
                # Prétraitement optionnel (mode normal)
                if use_preprocessing:
                    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f"pre_{filename}")
                    preprocess_image(filepath, processed_path)
                    ocr_input = processed_path
                else:
                    ocr_input = filepath
                
                # OCR normal avec paramètres optimisés
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
            
            # Trier et formater le texte
            sorted_lines = sort_text_by_position(result)
            ocr_text, detailed_results = format_text_output(sorted_lines, min_confidence)
            
            # Calculer les statistiques
            stats = calculate_stats(detailed_results, ocr_text)
            
            # Dessiner les boîtes sur l'image
            boxed_filename = f"boxed_{filename}"
            boxed_path = os.path.join(app.config['PROCESSED_FOLDER'], boxed_filename)
            draw_boxes_on_image(filepath, result, boxed_path)
            
            # Chemins pour afficher les images
            uploaded_image = url_for('uploaded_file', filename=filename)
            processed_image = url_for('processed_file', filename=boxed_filename)
            uploaded_filename = filename
            
    return render_template('index.html', 
                         ocr_text=ocr_text, 
                         uploaded_image=uploaded_image,
                         processed_image=processed_image,
                         uploaded_filename=uploaded_filename,
                         stats=stats,
                         detailed_results=json.dumps(detailed_results),
                         gpu_available=GPU_AVAILABLE)


@app.route('/api/ocr', methods=['POST'])
def api_ocr():
    """API endpoint pour l'OCR (pour utilisation AJAX future)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)
    
    min_confidence = float(request.form.get('min_confidence', 0.3))
    
    # OCR
    result = reader.readtext(filepath)
    sorted_lines = sort_text_by_position(result)
    ocr_text, detailed_results = format_text_output(sorted_lines, min_confidence)
    stats = calculate_stats(detailed_results, ocr_text)
    
    return jsonify({
        'text': ocr_text,
        'details': detailed_results,
        'stats': stats
    })


if __name__ == "__main__":
    print("=" * 50)
    print("🔍 EdiScan - OCR Intelligent")
    print(f"🖥️  GPU CUDA: {'✅ Activé' if GPU_AVAILABLE else '❌ Désactivé (CPU)'}")
    print(f"🌐 Langues: Français, Anglais")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
