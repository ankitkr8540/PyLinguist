from openai import OpenAI
import pandas as pd
from typing import List, Tuple, Optional
import re

class GPTCodeTranslator:
    def __init__(self, api_key: str):
        """Initialize GPT translator with OpenAI API key"""
        self.client = OpenAI(api_key=api_key)
        
    def load_examples(self, source_lang: str, target_lang: str, 
                     examples_path: str = 'few_shot_Learning_data.csv') -> List[Tuple[str, str]]:
        """Load translation examples for few-shot learning"""
        try:
            examples_df = pd.read_csv(examples_path)
            source_col = f'{source_lang}_code'
            target_col = f'{target_lang}_code'
            
            if source_col in examples_df.columns and target_col in examples_df.columns:
                examples = list(zip(examples_df[source_col], examples_df[target_col]))
                return examples[:5]  # Return top 5 examples
            return []
        except Exception as e:
            print(f"Error loading examples: {str(e)}")
            return []

    def create_translation_prompt(self, code: str, source_lang: str, target_lang: str, 
                                examples: Optional[List[Tuple[str, str]]] = None) -> str:
        """Create a detailed prompt for code translation"""
        prompt = f"""Translate this Python code from {source_lang} to {target_lang}.
Rules:
1. Preserve all Python syntax and functionality
2. Translate variable names, function names, and comments
3. Maintain code structure and indentation
4. Keep string literals semantic meaning
5. Preserve special characters and operators
6. Join multi-word translations with underscores
7. Keep numeric values and mathematical operations unchanged

"""
        if examples:
            prompt += "Here are some example translations:\n\n"
            for src, tgt in examples:
                prompt += f"{source_lang} code:\n{src}\n"
                prompt += f"{target_lang} code:\n{tgt}\n\n"

        prompt += f"\nNow translate this code:\n{code}"
        return prompt

    def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        """Translate code using GPT with few-shot learning"""
        try:
            # Load examples for few-shot learning
            examples = self.load_examples(source_lang, target_lang)
            
            # Create the translation prompt
            prompt = self.create_translation_prompt(code, source_lang, target_lang, examples)

            # Get translation from GPT
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert Python code translator specializing in translating between {source_lang} and {target_lang}. Maintain code functionality while translating identifiers and comments."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1500
            )
            
            translated_code = response.choices[0].message.content.strip()
            
            # Clean up the response
            if "```python" in translated_code:
                translated_code = translated_code.split("```python")[1].split("```")[0].strip()
            elif "```" in translated_code:
                translated_code = translated_code.split("```")[1].strip()
                
            return translated_code

        except Exception as e:
            print(f"GPT translation error: {str(e)}")
            return code

    def translate_comments(self, code: str, source_lang: str, target_lang: str) -> str:
        """Translate only the comments in the code"""
        try:
            prompt = f"""Translate only the comments in this Python code from {source_lang} to {target_lang}. 
Keep all code unchanged. Only translate text after # symbols:

{code}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code comment translator. Only translate comments (#) while preserving all code."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Comment translation error: {str(e)}")
            return code

    def evaluate_translation(self, original_code: str, translated_code: str) -> dict:
        """Evaluate the quality of the translation"""
        try:
            prompt = f"""Evaluate this code translation for quality and correctness:

Original code:
{original_code}

Translated code:
{translated_code}

Evaluate:
1. Syntax correctness
2. Semantic preservation
3. Variable name translation accuracy
4. Comment translation accuracy
5. Overall functionality preservation"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code translation quality evaluator. Provide detailed analysis."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=500
            )
            
            return {
                'evaluation': response.choices[0].message.content.strip(),
                'success': True
            }
            
        except Exception as e:
            return {
                'evaluation': f"Evaluation error: {str(e)}",
                'success': False
            }