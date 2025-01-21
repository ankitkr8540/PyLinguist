# pylinguist/utils/partial_translator.py

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging
from ..utils.language_extractor import extract_keyword_header, extract_language
from ..utils.logger import setup_logger
from tqdm import tqdm
import sys

logger = setup_logger()

class PartialTranslator:
    """Handles partial translation using Joshua keywords while preserving code structure."""
    
    def __init__(self, source_lang: str, target_lang: str, 
                 keywords_path: Path = Path("data/keywords/Joshua_Keywords.csv")):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.keywords_path = keywords_path
        self.keyword_dict = self._load_keywords()
        
    def _load_keywords(self) -> Dict[str, str]:
        """Load keyword mappings for specified languages."""
        try:
            source_col = extract_keyword_header(self.source_lang)
            target_col = extract_keyword_header(self.target_lang)
            
            keywords_df = pd.read_csv(self.keywords_path)
            
            translation_dict = {}
            for _, row in keywords_df.iterrows():
                source_word = str(row[source_col]).strip()
                target_word = str(row[target_col]).strip()
                if pd.notna(source_word) and pd.notna(target_word):
                    translation_dict[source_word] = target_word
                    
            logger.info(f"Loaded keywords dictionary for {extract_language(self.source_lang)} "
                     f"to {extract_language(self.target_lang)}")
                     
            return translation_dict
            
        except Exception as e:
            logger.error(f"Error loading keywords: {str(e)}")
            sys.exit(1)
            raise
    
    def translate_word(self, word: str) -> str:
        """Translate a single word if it's in the keyword dictionary."""
        # Handle compound words with underscores
        if '_' in word:
            parts = word.split('_')
            translated_parts = [self.keyword_dict.get(part, part) for part in parts]
            return '_'.join(translated_parts)
        return self.keyword_dict.get(word, word)
    
    def translate_code(self, code: str) -> str:
        """
        Translate code while preserving structure, comments, and strings.
        Only translates keywords from the dictionary.
        """
        # Split code into lines
        lines = code.split('\n')
        translated_lines = []
        
        for line in lines:
            # Handle empty lines
            if not line.strip():
                translated_lines.append(line)
                continue
            
            # Split line into code and comment if exists
            code_part = line
            comment_part = ""
            if '#' in line:
                code_part, comment_part = line.split('#', 1)
                comment_part = '#' + comment_part
            
            # Find string literals and create placeholders
            strings = []
            string_pattern = r'(\".*?\"|\'.*?\')'
            for match in re.finditer(string_pattern, code_part):
                strings.append(match.group(0))
            
            # Replace strings with placeholders
            placeholder_code = re.sub(string_pattern, 'STRING_PLACEHOLDER', code_part)
            
            # Split into words while preserving whitespace
            tokens = re.findall(r'\S+|\s+', placeholder_code)
            
            # Translate only non-whitespace tokens that are keywords
            translated_tokens = []
            for token in tokens:
                if token.isspace():
                    translated_tokens.append(token)
                else:
                    translated_tokens.append(self.translate_word(token))
            
            # Reconstruct code with original strings
            translated_code = ''.join(translated_tokens)
            for string in strings:
                translated_code = translated_code.replace('STRING_PLACEHOLDER', string, 1)
            
            # Combine code and comment
            translated_line = translated_code + comment_part
            translated_lines.append(translated_line)
        
        return '\n'.join(translated_lines)

def partial_translate_examples(data_path: Path, source_lang: str, target_lang: str, 
                            start_index: int, test_samples: int, train_samples: int) -> pd.DataFrame:
    """
    Translate multiple examples from dataset.
    Returns DataFrame with original and translated code.
    """
    try:
        df = pd.read_csv(data_path)
        translator = PartialTranslator(source_lang, target_lang)
        
        total_samples = test_samples + train_samples
        if start_index + total_samples > len(df):
            logger.warning("Requested range exceeds dataset size. Adjusting start index...")
            start_index = 0
            
        selected_df = df.iloc[start_index:start_index + total_samples]
        
        translations = []
        
        for _, row in tqdm(pd.DataFrame(selected_df).iterrows(), total=len(selected_df), desc="Translating code"):
            translated_code = translator.translate_code(row['English_code'])
            translations.append({
            'English_code': row['English_code'],
            'Partial_translated_code': translated_code
            })
        
        return pd.DataFrame(translations)
        
    except Exception as e:
        logger.error(f"Error in partial translation: {str(e)}")
        raise