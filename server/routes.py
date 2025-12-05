"""
EdiScan - Tool Routes
"""

import os
import uuid
from flask import Blueprint, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

from features import (
    extract_text_from_pdf,
    extract_text_from_docx,
    translate_text,
    detect_language,
    scan_qr_code,
    generate_qr_code,
    transcribe_audio,
    text_to_speech,
    summarize_text,
    extract_all_info,
    get_text_stats,
    get_available_features,
    SUPPORTED_LANGUAGES
)

tools_bp = Blueprint('tools', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TOOL_CONFIGS = {
    'pdf': {
        'tool_name': 'PDF > Texte',
        'tool_icon': '📄',
        'tool_description': 'Extraire le texte d un fichier PDF',
        'input_type': 'file',
        'drop_text': 'Deposez votre PDF ici',
        'allowed_extensions': ['.pdf'],
        'accept_types': '.pdf',
        'button_text': 'Extraire',
        'empty_message': 'Le texte extrait apparaitra ici',
        'result_type': 'text'
    },
    'docx': {
        'tool_name': 'Word > Texte',
        'tool_icon': '📝',
        'tool_description': 'Extraire le texte d un document Word',
        'input_type': 'file',
        'drop_text': 'Deposez votre fichier Word ici',
        'allowed_extensions': ['.docx', '.doc'],
        'accept_types': '.docx,.doc',
        'button_text': 'Extraire',
        'empty_message': 'Le texte extrait apparaitra ici',
        'result_type': 'text'
    },
    'translate': {
        'tool_name': 'Traduction',
        'tool_icon': '🌐',
        'tool_description': 'Traduire du texte vers 12+ langues',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a traduire...',
        'button_text': 'Traduire',
        'empty_message': 'La traduction apparaitra ici',
        'result_type': 'text'
    },
    'detect-language': {
        'tool_name': 'Detection de langue',
        'tool_icon': '🔍',
        'tool_description': 'Identifier la langue d un texte',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a analyser...',
        'button_text': 'Detecter',
        'empty_message': 'La langue detectee apparaitra ici',
        'result_type': 'text'
    },
    'speech-to-text': {
        'tool_name': 'Audio > Texte',
        'tool_icon': '🎤',
        'tool_description': 'Transcrire un fichier audio avec Whisper AI',
        'input_type': 'file',
        'drop_text': 'Deposez votre fichier audio ici',
        'allowed_extensions': ['.mp3', '.wav', '.m4a', '.ogg'],
        'accept_types': '.mp3,.wav,.m4a,.ogg,audio/*',
        'button_text': 'Transcrire',
        'empty_message': 'La transcription apparaitra ici',
        'result_type': 'text'
    },
    'text-to-speech': {
        'tool_name': 'Texte > Audio',
        'tool_icon': '🔊',
        'tool_description': 'Convertir du texte en parole',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a convertir en audio...',
        'button_text': 'Generer audio',
        'empty_message': 'L audio apparaitra ici',
        'result_type': 'audio'
    },
    'summarize': {
        'tool_name': 'Resume automatique',
        'tool_icon': '📋',
        'tool_description': 'Resumer un long texte en quelques phrases',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a resumer...',
        'button_text': 'Resumer',
        'empty_message': 'Le resume apparaitra ici',
        'result_type': 'text'
    },
    'extract-info': {
        'tool_name': 'Extraction d infos',
        'tool_icon': '🔎',
        'tool_description': 'Extraire emails, telephones, URLs, dates',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a analyser...',
        'button_text': 'Extraire',
        'empty_message': 'Les informations extraites apparaitront ici',
        'result_type': 'info'
    },
    'qr-scan': {
        'tool_name': 'Scanner QR Code',
        'tool_icon': '📱',
        'tool_description': 'Lire un QR code depuis une image',
        'input_type': 'file',
        'drop_text': 'Deposez une image avec un QR code',
        'allowed_extensions': ['.png', '.jpg', '.jpeg'],
        'accept_types': '.png,.jpg,.jpeg,image/*',
        'button_text': 'Scanner',
        'empty_message': 'Le contenu du QR code apparaitra ici',
        'result_type': 'qr'
    },
    'qr-generate': {
        'tool_name': 'Generer QR Code',
        'tool_icon': '⬛',
        'tool_description': 'Creer un QR code depuis du texte',
        'input_type': 'text',
        'placeholder': 'Entrez le texte ou URL...',
        'button_text': 'Generer',
        'empty_message': 'Le QR code apparaitra ici',
        'result_type': 'image'
    },
    'stats': {
        'tool_name': 'Statistiques texte',
        'tool_icon': '📊',
        'tool_description': 'Compter mots, phrases, caracteres, etc.',
        'input_type': 'text',
        'placeholder': 'Entrez le texte a analyser...',
        'button_text': 'Analyser',
        'empty_message': 'Les statistiques apparaitront ici',
        'result_type': 'stats'
    }
}


def save_uploaded_file(file):
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    return filepath


@tools_bp.route('/tools')
def tools_list():
    return render_template('tools.html', features=get_available_features())


@tools_bp.route('/tool/<tool_id>', methods=['GET', 'POST'])
def tool_page(tool_id):
    if tool_id not in TOOL_CONFIGS:
        return redirect(url_for('tools.tools_list'))
    
    config = TOOL_CONFIGS[tool_id].copy()
    config['tool_id'] = tool_id
    config['result'] = None
    config['error'] = None
    config['input_text'] = ''
    
    if request.method == 'POST':
        try:
            if config['input_type'] == 'file':
                if 'file' not in request.files or not request.files['file'].filename:
                    config['error'] = 'Aucun fichier selectionne'
                else:
                    file = request.files['file']
                    filepath = save_uploaded_file(file)
                    
                    result, error = None, None
                    if tool_id == 'pdf':
                        result, error = extract_text_from_pdf(filepath)
                    elif tool_id == 'docx':
                        result, error = extract_text_from_docx(filepath)
                    elif tool_id == 'speech-to-text':
                        result, error = transcribe_audio(filepath)
                    elif tool_id == 'qr-scan':
                        result, error = scan_qr_code(filepath)
                    
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    
                    if error:
                        config['error'] = error
                    else:
                        config['result'] = result
            
            elif config['input_type'] == 'text':
                text = request.form.get('text', '').strip()
                qr_data = request.form.get('qr_data', '').strip()
                config['input_text'] = text
                
                if tool_id == 'qr-generate':
                    if not qr_data:
                        config['error'] = 'Veuillez entrer un texte ou URL'
                    else:
                        result, error = generate_qr_code(qr_data)
                        if error:
                            config['error'] = error
                        else:
                            config['result'] = result
                elif not text:
                    config['error'] = 'Veuillez entrer du texte'
                else:
                    result, error = None, None
                    if tool_id == 'translate':
                        source = request.form.get('source_lang', 'auto')
                        target = request.form.get('target_lang', 'en')
                        result, error = translate_text(text, source, target)
                    elif tool_id == 'detect-language':
                        lang = detect_language(text)
                        result = f"Langue detectee: {SUPPORTED_LANGUAGES.get(lang, lang)}"
                    elif tool_id == 'text-to-speech':
                        result, error = text_to_speech(text)
                    elif tool_id == 'summarize':
                        sentences = int(request.form.get('sentences', 5))
                        result, error = summarize_text(text, sentences)
                    elif tool_id == 'extract-info':
                        result = extract_all_info(text)
                    elif tool_id == 'stats':
                        result = get_text_stats(text)
                    
                    if error:
                        config['error'] = error
                    else:
                        config['result'] = result
        
        except Exception as e:
            config['error'] = f"Erreur: {str(e)}"
    
    return render_template('tool.html', **config)


@tools_bp.route('/api/features')
def api_features():
    return get_available_features()

