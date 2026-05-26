"""
Multi-language support configuration
Provides internationalization (i18n) for the backend
"""
import os
from enum import Enum
from typing import Dict

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    ARABIC = "ar"
    CHINESE = "zh"


# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # General
        "app_name": "Medical Report Interpreter",
        "welcome": "Welcome",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        
        # Report statuses
        "status_queued": "Queued for processing",
        "status_processing": "Processing",
        "status_done": "Complete",
        "status_failed": "Failed",
        
        # Lab result statuses
        "result_normal": "Normal",
        "result_high": "High",
        "result_low": "Low",
        "result_unknown": "Unknown",
        
        # Messages
        "upload_success": "Report uploaded successfully",
        "processing_started": "Analysis started",
        "report_ready": "Your report is ready",
        "no_results": "No results found",
        
        # Disclaimer
        "medical_disclaimer": "This is for educational purposes only. Always consult your doctor.",
    },
    
    "es": {
        # Spanish translations
        "app_name": "Intérprete de Informes Médicos",
        "welcome": "Bienvenido",
        "loading": "Cargando...",
        "error": "Error",
        "success": "Éxito",
        
        "status_queued": "En cola para procesar",
        "status_processing": "Procesando",
        "status_done": "Completado",
        "status_failed": "Fallido",
        
        "result_normal": "Normal",
        "result_high": "Alto",
        "result_low": "Bajo",
        "result_unknown": "Desconocido",
        
        "upload_success": "Informe subido exitosamente",
        "processing_started": "Análisis iniciado",
        "report_ready": "Su informe está listo",
        "no_results": "No se encontraron resultados",
        
        "medical_disclaimer": "Esto es solo con fines educativos. Siempre consulte a su médico.",
    },
    
    "fr": {
        # French translations
        "app_name": "Interprète de Rapport Médical",
        "welcome": "Bienvenue",
        "loading": "Chargement...",
        "error": "Erreur",
        "success": "Succès",
        
        "status_queued": "En file d'attente",
        "status_processing": "En cours de traitement",
        "status_done": "Terminé",
        "status_failed": "Échoué",
        
        "result_normal": "Normal",
        "result_high": "Élevé",
        "result_low": "Bas",
        "result_unknown": "Inconnu",
        
        "upload_success": "Rapport téléchargé avec succès",
        "processing_started": "Analyse commencée",
        "report_ready": "Votre rapport est prêt",
        "no_results": "Aucun résultat trouvé",
        
        "medical_disclaimer": "Ceci est à des fins éducatives uniquement. Consultez toujours votre médecin.",
    },
    
    "ar": {
        # Arabic translations
        "app_name": "مترجم التقارير الطبية",
        "welcome": "مرحباً",
        "loading": "جارٍ التحميل...",
        "error": "خطأ",
        "success": "نجح",
        
        "status_queued": "في قائمة الانتظار",
        "status_processing": "قيد المعالجة",
        "status_done": "مكتمل",
        "status_failed": "فشل",
        
        "result_normal": "طبيعي",
        "result_high": "مرتفع",
        "result_low": "منخفض",
        "result_unknown": "غير معروف",
        
        "upload_success": "تم رفع التقرير بنجاح",
        "processing_started": "بدأ التحليل",
        "report_ready": "تقريرك جاهز",
        "no_results": "لم يتم العثور على نتائج",
        
        "medical_disclaimer": "هذا لأغراض تعليمية فقط. استشر طبيبك دائماً.",
    },
    
    "zh": {
        # Chinese translations
        "app_name": "医学报告解释器",
        "welcome": "欢迎",
        "loading": "加载中...",
        "error": "错误",
        "success": "成功",
        
        "status_queued": "待处理",
        "status_processing": "处理中",
        "status_done": "完成",
        "status_failed": "失败",
        
        "result_normal": "正常",
        "result_high": "偏高",
        "result_low": "偏低",
        "result_unknown": "未知",
        
        "upload_success": "报告上传成功",
        "processing_started": "分析已开始",
        "report_ready": "您的报告已准备好",
        "no_results": "未找到结果",
        
        "medical_disclaimer": "这仅供教育目的。请始终咨询您的医生。",
    }
}


class Translator:
    """Simple translator class"""
    
    def __init__(self, language: str = "en"):
        self.language = language if language in TRANSLATIONS else "en"
    
    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language
        
        Args:
            key: Translation key
            **kwargs: Variable substitutions
            
        Returns:
            Translated string
        """
        translations = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        text = translations.get(key, key)
        
        # Replace variables
        for var, value in kwargs.items():
            text = text.replace(f"{{{var}}}", str(value))
        
        return text
    
    def set_language(self, language: str):
        """Change the current language"""
        if language in TRANSLATIONS:
            self.language = language
    
    def get_available_languages(self) -> list:
        """Get list of available languages"""
        return list(TRANSLATIONS.keys())


# Global translator instance
_translator = Translator()

def get_translator(language: str = None) -> Translator:
    """Get translator instance"""
    if language:
        _translator.set_language(language)
    return _translator


def t(key: str, language: str = "en", **kwargs) -> str:
    """
    Quick translate function
    
    Args:
        key: Translation key
        language: Language code
        **kwargs: Variable substitutions
        
    Returns:
        Translated string
    """
    translator = Translator(language)
    return translator.translate(key, **kwargs)
