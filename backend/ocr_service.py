"""
OCR Service for extracting text from medical reports (images and PDFs)
"""
import os
import logging
from pathlib import Path
from typing import Tuple
import cv2
import numpy as np
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def preprocess_image(image_path: str) -> np.ndarray:
    """Preprocess image for better OCR results"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original.")
        img = cv2.imread(image_path)
        return img if img is not None else np.array([])


def extract_text_from_image(image_path: str) -> Tuple[str, float]:
    """Extract text from an image using Tesseract OCR"""
    try:
        import pytesseract

        # Try original image first
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')

        if not text.strip():
            # Retry with preprocessed image
            logger.info("No text with original image, retrying with preprocessing...")
            processed = preprocess_image(image_path)
            if processed.size > 0:
                text = pytesseract.image_to_string(
                    Image.fromarray(processed), config='--psm 6'
                )

        text = text.strip()
        confidence = 0.85 if text else 0.0
        return text, confidence

    except Exception as e:
        logger.error(f"OCR failed for image {image_path}: {e}")
        return "", 0.0


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, float]:
    """Extract text from PDF — direct text first, OCR fallback"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip() and len(text.strip()) > 50:
                logger.info("PDF text extracted successfully")
                return text.strip(), 1.0
        logger.info("PDF text extraction insufficient, using OCR")
        return extract_text_from_pdf_ocr(pdf_path)
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        return "", 0.0


def extract_text_from_pdf_ocr(pdf_path: str) -> Tuple[str, float]:
    """Convert PDF pages to images and OCR them"""
    try:
        import tempfile
        images = convert_from_path(pdf_path, dpi=200)
        temp_dir = tempfile.gettempdir()
        all_text = []

        for i, image in enumerate(images):
            temp_path = os.path.join(temp_dir, f"pdf_page_{i}.png")
            image.save(temp_path, "PNG")
            text, _ = extract_text_from_image(temp_path)
            if text:
                all_text.append(text)
            try:
                os.remove(temp_path)
            except Exception:
                pass

        full_text = "\n\n".join(all_text)
        return full_text, 0.85 if full_text else 0.0

    except Exception as e:
        logger.error(f"PDF OCR failed: {e}")
        return "", 0.0


def extract_text_from_file(file_path: str) -> Tuple[str, float, str]:
    """Main entry point for text extraction from any file"""
    file_ext = Path(file_path).suffix.lower()
    try:
        if file_ext == ".pdf":
            text, confidence = extract_text_from_pdf(file_path)
            engine = "pdfplumber" if confidence == 1.0 else "tesseract"
        elif file_ext in [".jpg", ".jpeg", ".png"]:
            text, confidence = extract_text_from_image(file_path)
            engine = "tesseract"
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        logger.info(f"Text extraction complete. Length: {len(text)}, Confidence: {confidence:.2f}")
        return text, confidence, engine

    except Exception as e:
        logger.error(f"Text extraction failed for {file_path}: {e}")
        return "", 0.0, "none"
