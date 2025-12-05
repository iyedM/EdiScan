"""
EdiScan - Additional Features Module
PDF, Translation, QR Code, Audio, Summary, etc.
"""

import os
import re
import io
import base64
from PIL import Image

# PDF
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Translation
try:
    from deep_translator import GoogleTranslator
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False

# QR Code
try:
    from pyzbar.pyzbar import decode as decode_qr
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Audio
try:
    import whisper
    WHISPER_AVAILABLE = True
    whisper_model = None
except ImportError:
    WHISPER_AVAILABLE = False

# Text-to-Speech
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Summary
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    SUMMARY_AVAILABLE = True
except ImportError:
    SUMMARY_AVAILABLE = False

# Phone numbers
try:
    import phonenumbers
    PHONE_AVAILABLE = True
except ImportError:
    PHONE_AVAILABLE = False


def get_available_features():
    """Return dict of available features"""
    return {
        'pdf': PDF_AVAILABLE,
        'docx': DOCX_AVAILABLE,
        'translation': TRANSLATION_AVAILABLE,
        'qr_code': QR_AVAILABLE,
        'speech_to_text': WHISPER_AVAILABLE,
        'text_to_speech': TTS_AVAILABLE,
        'summary': SUMMARY_AVAILABLE,
        'phone_extraction': PHONE_AVAILABLE
    }


# ==========================================
# PDF Functions
# ==========================================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return None, "PDF support not installed"
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        if not text.strip():
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        
        return text.strip(), None
    except Exception as e:
        return None, str(e)


def extract_text_from_docx(docx_path):
    """Extract text from Word document"""
    if not DOCX_AVAILABLE:
        return None, "DOCX support not installed"
    
    try:
        doc = Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text])
        return text, None
    except Exception as e:
        return None, str(e)


# ==========================================
# Translation Functions
# ==========================================

SUPPORTED_LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'ar': 'العربية',
    'es': 'Español',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'zh-CN': '中文',
    'ja': '日本語',
    'ko': '한국어',
    'ru': 'Русский',
    'tr': 'Türkçe'
}

def translate_text(text, source='auto', target='en'):
    """Translate text to target language"""
    if not TRANSLATION_AVAILABLE:
        return None, "Translation not installed"
    
    try:
        translator = GoogleTranslator(source=source, target=target)
        
        # Split long text into chunks (max 5000 chars)
        max_length = 4500
        if len(text) <= max_length:
            result = translator.translate(text)
        else:
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            result = " ".join([translator.translate(chunk) for chunk in chunks])
        
        return result, None
    except Exception as e:
        return None, str(e)


def detect_language(text):
    """Detect language of text"""
    if not TRANSLATION_AVAILABLE:
        return 'unknown'
    
    try:
        from deep_translator import single_detection
        return single_detection(text[:500], api_key=None)
    except:
        return 'unknown'


# ==========================================
# QR Code Functions
# ==========================================

def scan_qr_code(image_path):
    """Scan QR code from image"""
    if not QR_AVAILABLE:
        return None, "QR Code support not installed"
    
    try:
        img = Image.open(image_path)
        decoded = decode_qr(img)
        
        if decoded:
            results = []
            for obj in decoded:
                results.append({
                    'data': obj.data.decode('utf-8'),
                    'type': obj.type
                })
            return results, None
        else:
            return [], "No QR code found"
    except Exception as e:
        return None, str(e)


def generate_qr_code(data, filename='qrcode.png'):
    """Generate QR code image"""
    if not QR_AVAILABLE:
        return None, "QR Code support not installed"
    
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64, None
    except Exception as e:
        return None, str(e)


# ==========================================
# Audio Functions (Speech-to-Text)
# ==========================================

def transcribe_audio(audio_path, language='fr'):
    """Transcribe audio file to text using Whisper"""
    global whisper_model
    
    if not WHISPER_AVAILABLE:
        return None, "Whisper not installed"
    
    try:
        # Load model on first use
        if whisper_model is None:
            whisper_model = whisper.load_model("base")
        
        result = whisper_model.transcribe(audio_path, language=language)
        return result['text'], None
    except Exception as e:
        return None, str(e)


def text_to_speech(text, language='fr', filename='speech.mp3'):
    """Convert text to speech"""
    if not TTS_AVAILABLE:
        return None, "Text-to-Speech not installed"
    
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        
        audio_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return audio_base64, None
    except Exception as e:
        return None, str(e)


# ==========================================
# Summary Functions
# ==========================================

def summarize_text(text, sentences_count=5):
    """Summarize text to key sentences"""
    if not SUMMARY_AVAILABLE:
        return None, "Summary not installed"
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("french"))
        summarizer = LsaSummarizer()
        
        summary = summarizer(parser.document, sentences_count)
        result = " ".join([str(sentence) for sentence in summary])
        
        return result, None
    except Exception as e:
        return None, str(e)


# ==========================================
# Extraction Functions
# ==========================================

def extract_emails(text):
    """Extract email addresses from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, text)
    return list(set(emails))


def extract_phone_numbers(text, region='FR'):
    """Extract phone numbers from text"""
    if not PHONE_AVAILABLE:
        # Fallback regex
        pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{0,4}'
        phones = re.findall(pattern, text)
        return [p.strip() for p in phones if len(p.strip()) >= 8]
    
    try:
        phones = []
        for match in phonenumbers.PhoneNumberMatcher(text, region):
            phones.append(phonenumbers.format_number(
                match.number, 
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ))
        return phones
    except:
        return []


def extract_urls(text):
    """Extract URLs from text"""
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*'
    urls = re.findall(pattern, text)
    return list(set(urls))


def extract_dates(text):
    """Extract dates from text"""
    patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}',
        r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}',
    ]
    
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return list(set(dates))


def extract_all_info(text):
    """Extract all types of info from text"""
    return {
        'emails': extract_emails(text),
        'phones': extract_phone_numbers(text),
        'urls': extract_urls(text),
        'dates': extract_dates(text)
    }


# ==========================================
# Statistics
# ==========================================

def get_text_stats(text):
    """Get detailed text statistics"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    paragraphs = text.split('\n\n')
    
    return {
        'characters': len(text),
        'characters_no_spaces': len(text.replace(' ', '').replace('\n', '')),
        'words': len(words),
        'sentences': len([s for s in sentences if s.strip()]),
        'paragraphs': len([p for p in paragraphs if p.strip()]),
        'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0
    }

