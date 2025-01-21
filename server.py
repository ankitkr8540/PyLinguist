import pandas as pd
from openai import OpenAI
import warnings
import streamlit as st
from typing import Optional
from google_translator import GoogleCodeTranslator
from gpt_translator import GPTCodeTranslator

warnings.filterwarnings('ignore')

class TranslationService:
    """Main service to handle code translation requests"""
    
    def __init__(self):
        self.google_translator = GoogleCodeTranslator()
        self.gpt_translator: Optional[GPTCodeTranslator] = None
        self.supported_languages = {
            'English': {'code': 'en', 'flag': '🇬🇧'},
            'Hindi': {'code': 'hi', 'flag': '🇮🇳'},
            'Bengali': {'code': 'bn', 'flag': '🇧🇩'},
            'French': {'code': 'fr', 'flag': '🇫🇷'},
            'Spanish': {'code': 'es', 'flag': '🇪🇸'},
            'Mandarin': {'code': 'zh', 'flag': '🇨🇳'},
            'Greek': {'code': 'el', 'flag': '🇬🇷'},
        }

    def _clean_language_name(self, lang_name: str) -> str:
        """Remove any emojis or extra spaces from language name"""
        for lang in self.supported_languages:
            if lang in lang_name:
                return lang
        return lang_name.strip()

    def translate(self, 
                 code: str, 
                 source_lang: str, 
                 target_lang: str, 
                 use_gpt: bool = False) -> Optional[str]:
        """Main translation method"""
        try:
            # Clean language names
            source_lang = self._clean_language_name(source_lang)
            target_lang = self._clean_language_name(target_lang)
            
            # Validate inputs
            if not code or not code.strip():
                st.error("Please enter some code to translate")
                return None
                
            if source_lang == target_lang:
                st.error("Source and target languages must be different")
                return None
                
            # Handle GPT translation
            if use_gpt:
                api_key = st.session_state.get('api_key')
                if not api_key:
                    st.error("API key is required for GPT translation")
                    return None
                    
                if not self.gpt_translator:
                    self.gpt_translator = GPTCodeTranslator(api_key)
                
                try:
                    return self.gpt_translator.translate_code(code, source_lang, target_lang)
                except Exception as e:
                    st.warning(f"GPT translation error: {str(e)}. Falling back to Google Translator")
                    return self.google_translator.translate_code(code, source_lang, target_lang)
            
            # Use Google translator
            return self.google_translator.translate_code(code, source_lang, target_lang)
            
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            return None

# Initialize global translation service
translation_service = TranslationService()

def test_translation(code: str, source_language: str, target_language: str, use_gpt: bool = False) -> Optional[str]:
    """Main translation function called from app.py"""
    try:
        # Perform translation
        translated_code = translation_service.translate(
            code=code,
            source_lang=source_language,
            target_lang=target_language,
            use_gpt=use_gpt
        )
        
        if translated_code:
            # Update translation history
            if 'translation_history' in st.session_state:
                st.session_state.translation_history.append({
                    'source_lang': source_language,
                    'target_lang': target_language,
                    'source_code': code,
                    'translated_code': translated_code,
                    'mode': 'GPT-Enhanced' if use_gpt else 'Basic'
                })
            return translated_code
        
        return None
        
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def get_supported_languages() -> dict:
    """Get list of supported languages"""
    return translation_service.supported_languages