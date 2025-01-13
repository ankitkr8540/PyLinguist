from google_trans_new import google_translator
import re
import pandas as pd
from typing import Dict, Optional

class KeywordManager:
    """Manages programming keyword translations for multiple languages"""
    def __init__(self, keywords_path: str = './segregated_data.csv'):
        self.keywords_path = keywords_path
        self.keywords = self._load_keywords()
        self._add_special_cases()

    def _load_keywords(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Load keyword translations for all languages"""
        try:
            df = pd.read_csv(self.keywords_path)
            
            # Create dictionaries for each language pair
            language_pairs = {}
            source_languages = ['EnglishKey.txt', 'FrenchKey.txt', 'SpanishKey.txt', 
                              'KurdishKey.txt', 'HindiKey.txt', 'BengaliKey.txt', 
                              'MandarinKey.txt', 'GreekKey.txt']
            
            for source in source_languages:
                source_name = source.replace('Key.txt', '')
                language_pairs[source_name] = {}
                
                for target in source_languages:
                    if source != target:
                        target_name = target.replace('Key.txt', '')
                        translations = {
                            row[source]: row[target]
                            for _, row in df.iterrows()
                            if pd.notna(row[source]) and pd.notna(row[target])
                        }
                        language_pairs[source_name][target_name] = translations
            
            return language_pairs
        except Exception as e:
            print(f"Error loading keywords: {str(e)}")
            return {}

    def _add_special_cases(self) -> None:
        """Add special case translations for all languages"""
        special_cases = {
            'English': {
                'Hindi': {'True': 'सत्य', 'False': 'असत्य'},
                'Bengali': {'True': 'সত্য', 'False': 'মিথ্যা'},
                'Mandarin': {'True': '真', 'False': '假'},
                'Greek': {'True': 'αληθής', 'False': 'ψευδής'},
                'French': {'True': 'Vrai', 'False': 'Faux'},
                'Spanish': {'True': 'Verdadero', 'False': 'Falso'},
                'Kurdish': {'True': 'Rast', 'False': 'Şaş'}
            }
        }
        
        for source_lang, targets in special_cases.items():
            if source_lang not in self.keywords:
                self.keywords[source_lang] = {}
            for target_lang, translations in targets.items():
                if target_lang not in self.keywords[source_lang]:
                    self.keywords[source_lang][target_lang] = {}
                self.keywords[source_lang][target_lang].update(translations)

    def get_translation(self, word: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get translation for a keyword if available"""
        try:
            return self.keywords.get(source_lang, {}).get(target_lang, {}).get(word)
        except Exception:
            return None

class GoogleCodeTranslator:
    def __init__(self):
        self.translator = google_translator()
        self.keyword_manager = KeywordManager()

    def get_language_code(self, language: str) -> str:
        """Convert language names to codes"""
        language_codes = {
            'English': 'en',
            'Hindi': 'hi',
            'French': 'fr',
            'Spanish': 'es',
            'Kurdish': 'ku',
            'Bengali': 'bn',
            'Mandarin': 'zh-CN',
            'Greek': 'el'
        }
        return language_codes.get(language, 'en')

    def translate_token(self, token: str, source_lang: str, target_lang: str) -> str:
        """Translate a single token while preserving special characters"""
        if token.isspace():
            return token
        elif '_' in token:
            parts = token.split('_')
            translated_parts = [
                self.translate_token(part, source_lang, target_lang) 
                for part in parts if part
            ]
            return '_'.join(translated_parts)
        elif token.isalpha():
            keyword_trans = self.keyword_manager.get_translation(token, source_lang, target_lang)
            if keyword_trans:
                return keyword_trans
            try:
                translation = self.translator.translate(
                    token,
                    lang_src=self.get_language_code(source_lang),
                    lang_tgt=self.get_language_code(target_lang)
                )
                return translation.replace(' ', '_')
            except Exception:
                return token
        return token

    def translate_line(self, line: str, source_lang: str, target_lang: str) -> str:
        """Translate a single line of code"""
        indent = len(line) - len(line.lstrip())
        line = line.lstrip()

        if not line:
            return line

        try:
            if '#' in line:
                code_part, comment_part = line.split('#', 1)
                translated_comment = self.translator.translate(
                    comment_part.strip(),
                    lang_src=self.get_language_code(source_lang),
                    lang_tgt=self.get_language_code(target_lang)
                )

                if code_part:
                    tokens = re.findall(r'[a-zA-Z_]+|\d+|[^\w\s]|\s+', code_part)
                    translated_tokens = [
                        self.translate_token(token, source_lang, target_lang) 
                        for token in tokens
                    ]
                    translated_code = ''.join(translated_tokens)
                    return ' ' * indent + translated_code.rstrip() + ' #' + translated_comment
                return ' ' * indent + '#' + translated_comment

            tokens = re.findall(r'[a-zA-Z_]+|\d+|[^\w\s]|\s+', line)
            translated_tokens = [
                self.translate_token(token, source_lang, target_lang) 
                for token in tokens
            ]
            return ' ' * indent + ''.join(translated_tokens)

        except Exception as e:
            print(f"Line translation error: {str(e)}")
            return line

    def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        """Translate entire code while preserving structure"""
        if not isinstance(code, str):
            return ""

        lines = code.split('\n')
        translated_lines = [
            self.translate_line(line, source_lang, target_lang) 
            for line in lines
        ]
        return '\n'.join(translated_lines)