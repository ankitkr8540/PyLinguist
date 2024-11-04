import torch
from deep_translator import GoogleTranslator
import re
import time
import warnings
import pandas as pd
warnings.filterwarnings('ignore')


def load_keywords(target_language):
    print(target_language)
    keywords = pd.read_csv('segregated_data.csv')
    keywords.dropna(inplace=True)
    if target_language == 'hi':
        keywords_dict = {row['EnglishKey.txt']: row['HindiKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'fr':
        keywords_dict = {row['EnglishKey.txt']: row['FrenchKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'es':
        keywords_dict = {row['EnglishKey.txt']: row['SpanishKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'ku':
        keywords_dict = {row['EnglishKey.txt']: row['KurdishKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'bn':
        keywords_dict = {row['EnglishKey.txt']: row['BengaliKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'zh-CN':
        keywords_dict = {row['EnglishKey.txt']: row['MandarinKey.txt'] for _, row in keywords.iterrows()}
    elif target_language == 'el':
        keywords_dict = {row['EnglishKey.txt']: row['GreekKey.txt'] for _, row in keywords.iterrows()}
    else:    
        keywords_dict = {row['EnglishKey.txt']: row['EnglishKey.txt'] for _, row in keywords.iterrows()}
    return keywords_dict

class HindiCodeConverter:
    def __init__(self, keywords_dict,source_language, target_language):
        self.target_language = target_language
        self.source_language = source_language
        self.translator = GoogleTranslator(source=self.source_language, target= self.target_language)
        self.keywords = keywords_dict
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Add common translations
        # self.special_translations = {
        #     'i': 'ई',
        #     'j': 'जे',
        #     'k': 'के'
        # }
        # self.keywords.update(self.special_translations)

    
    def safe_translate(self, text, max_retries=3):
        """Translate text with retry mechanism"""
        if not text or not isinstance(text, str):
            return text
            
        for attempt in range(max_retries):
            try:
                time.sleep(0.2)
                return self.translator.translate(text)
            except Exception as e:
                if attempt == max_retries - 1:
                    return text
                time.sleep(0.5)
        return text
    
    def translate_line(self, line):
        """Translate a single line of code"""
        indent = len(line) - len(line.lstrip())
        line = line.lstrip()
        
        if not line:
            return line
        
        try:
            # Handle comments
            if '#' in line:
                code_part, comment_part = line.split('#', 1)
                translated_comment = self.safe_translate(comment_part.strip())
                
                if code_part:
                    tokens = re.findall(r'[a-zA-Z_]+|\d+|[^\w\s]|\s+', code_part)
                    translated_tokens = []
                    
                    for token in tokens:
                        if token.isspace():
                            translated_tokens.append(token)
                        elif token.isalpha():
                            translated = self.keywords.get(token, self.safe_translate(token))
                            translated_tokens.append(translated)
                        else:
                            translated_tokens.append(token)
                    
                    translated_code = ''.join(translated_tokens)
                    return ' ' * indent + translated_code.rstrip() + ' #' + translated_comment
                else:
                    return ' ' * indent + '#' + translated_comment
            
            # Handle code-only lines
            tokens = re.findall(r'[a-zA-Z_]+|\d+|[^\w\s]|\s+', line)
            translated_tokens = []
            
            for token in tokens:
                if token.isspace():
                    translated_tokens.append(token)
                elif token.isalpha():
                    translated = self.keywords.get(token, self.safe_translate(token))
                    translated_tokens.append(translated)
                else:
                    translated_tokens.append(token)
            
            return ' ' * indent + ''.join(translated_tokens)
            
        except Exception as e:
            print(f"Line translation error: {str(e)}")
            return line
    
    def translate_code(self, code):
        """Translate complete code block"""
        if not isinstance(code, str):
            return ""
        
        # Handle literal \n in the input
        if '\\n' in code:
            lines = code.strip("'\"").split('\\n')
            translated_lines = []
            
            for line in lines:
                translated_line = self.translate_line(line.strip())
                translated_lines.append(translated_line)
            
            return '\\n '.join(translated_lines)
        
        # Handle regular newlines
        lines = code.split('\n')
        translated_lines = []
        
        for line in lines:
            translated_line = self.translate_line(line)
            translated_lines.append(translated_line)
        
        return '\n'.join(translated_lines)

def translate_to_hindi(english_code, source_language, target_language, keywords_dict=None):
    """
    Simple function to translate English code to Hindi
    
    Args:
        english_code (str): Python code in English
        keywords_dict (dict, optional): Dictionary of keyword translations
        
    Returns:
        str: Translated Hindi code
    """
    if keywords_dict is None:
        # Load default keywords if not provided
        keywords_dict = load_keywords(target_language)
    
    # Initialize converter
    converter = HindiCodeConverter(keywords_dict,source_language, target_language)
    
    # Translate the code
    hindi_code = converter.translate_code(english_code)
    
    return hindi_code

# Example usage:
def test_translation(code,source_language, target_language):
    # Translate code
    hindi_version = translate_to_hindi(code,source_language,target_language)
    return hindi_version