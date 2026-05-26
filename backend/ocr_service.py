"""
OCR Service for extracting text from medical reports (images and PDFs)
"""
import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import cv2
import numpy as np
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Lazy load OCR engines
_ocr_engine = None


def get_ocr_engine():
    """Lazy load and return OCR engine (EasyOCR)"""
    global _ocr_engine
    
    if _ocr_engine is None:
        try:
            import easyocr
            _ocr_engine = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized successfully")
        except ImportError as ie:
            logger.error("EasyOCR not installed! Install with: pip install easyocr")
            raise ImportError(
                "EasyOCR not installed. Please run: pip install easyocr"
            ) from ie
        except Exception as e:
            logger.error(f"Failed to initialize OCR engine: {e}")
            raise
    
    return _ocr_engine


def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess image for better OCR results"""
    try:
        # Read image
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Threshold
        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        return thresh
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original.")
        return cv2.imread(image_path)


def extract_text_from_image(image_path: str) -> Tuple[str, float]:
    """
    Extract text from an image using OCR
    
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    try:
        # Get OCR engine
        ocr = get_ocr_engine()
        
        # EasyOCR works best with the original image path
        result = ocr.readtext(image_path)
        
        if not result:
            # Retry with preprocessed image
            logger.info("No text with original image, retrying with preprocessing...")
            processed_img = preprocess_image(image_path)
            result = ocr.readtext(processed_img)
        
        if not result:
            return "", 0.0
        
        texts = [item[1] for item in result]
        confidences = [float(item[2]) for item in result]
        
        full_text = "\n".join(texts)
        avg_confidence = float(sum(confidences) / len(confidences)) if confidences else 0.0
        
        return full_text, avg_confidence
            
    except Exception as e:
        logger.error(f"OCR failed for image {image_path}: {e}")
        return "", 0.0


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, float]:
    """
    Extract text from PDF - first try text extraction, fallback to OCR
    
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    try:
        # Try text extraction first
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If we got meaningful text, return it
            if text.strip() and len(text.strip()) > 50:
                logger.info("PDF text extracted successfully")
                return text.strip(), 1.0  # High confidence for text extraction
        
        # Fallback to OCR if text extraction failed
        logger.info("PDF text extraction insufficient, using OCR")
        return extract_text_from_pdf_ocr(pdf_path)
        
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return "", 0.0


def extract_text_from_pdf_ocr(pdf_path: str) -> Tuple[str, float]:
    """Convert PDF pages to images and OCR them"""
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        all_text = []
        all_confidences = []
        
        # Create temp directory if needed (cross-platform)
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        for i, image in enumerate(images):
            # Save temp image (Windows-compatible path)
            temp_image_path = os.path.join(temp_dir, f"pdf_page_{i}.png")
            image.save(temp_image_path, "PNG")
            
            # OCR the image
            text, confidence = extract_text_from_image(temp_image_path)
            
            if text:
                all_text.append(text)
                all_confidences.append(confidence)
            
            # Cleanup temp file
            try:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
            except:
                pass  # Ignore cleanup errors
        
        full_text = "\n\n".join(all_text)
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        return full_text, avg_confidence
        
    except Exception as e:
        logger.error(f"PDF OCR failed: {e}")
        return "", 0.0


def extract_text_from_file(file_path: str) -> Tuple[str, float, str]:
    """
    Main entry point for text extraction from any file
    
    Returns:
        Tuple of (extracted_text, confidence, ocr_engine_used)
    """
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == ".pdf":
            text, confidence = extract_text_from_pdf(file_path)
            engine = "pdfplumber+ocr" if confidence < 1.0 else "pdfplumber"
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            text, confidence = extract_text_from_image(file_path)
            engine = "easyocr"
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        logger.info(f"Text extraction complete. Length: {len(text)}, Confidence: {confidence:.2f}")
        return text, confidence, engine
        
    except Exception as e:
        logger.error(f"Text extraction failed for {file_path}: {e}")
        return "", 0.0, "none"
