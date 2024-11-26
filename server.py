import pandas as pd
from openai import OpenAI
from google_trans_new import google_translator
import warnings
warnings.filterwarnings('ignore')


# Initialize the OpenAI client and translator
API_KEY = st.secrets["openai"]['api_key']
client = OpenAI(api_key=API_KEY)
translator = google_translator()

def get_language_code(language):
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

def load_examples(source_language, target_language):
    """Load translation examples for the specified language pair"""
    try:
        examples_df = pd.read_csv('code_example.csv')
        
        source_col = f'{source_language}_code'
        target_col = f'{target_language}_code'
        
        # Create pairs of examples
        examples = list(zip(examples_df[source_col], examples_df[target_col]))
        return examples
    except Exception as e:
        print(f"Error loading examples: {str(e)}")
        return []

def create_few_shot_prompt(source_code, examples, source_language, target_language):
    """Create a prompt with few-shot examples"""
    prompt = f"Translate the following {source_language} code to {target_language}. Here are some examples:\n\n"
    
    # Add examples
    for src, tgt in examples[:5]:  # Use only first 5 examples to keep prompt size manageable
        prompt += f"{source_language} code:\n```python\n{src}\n```\n"
        prompt += f"{target_language} code:\n```python\n{tgt}\n```\n\n"
    
    # Add the actual code to translate
    prompt += f"Now translate this {source_language} code to {target_language}:\n```python\n{source_code}\n```"
    return prompt

def translate_code_with_gpt(source_code, source_language, target_language):
    """Translate code using GPT-4 with few-shot examples"""
    try:
        # Load translation examples
        examples = load_examples(source_language, target_language)
        
        # Create the few-shot prompt
        prompt = create_few_shot_prompt(source_code, examples, source_language, target_language)
        
        print(prompt)
        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to "gpt-3.5-turbo" for a cheaper option
            messages=[
                {
                    "role": "system", 
                    "content": "You are a code translation assistant that translates Python code between different languages while preserving functionality and sense of the code. Maintain proper indentation and code structure."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent translations
            max_tokens=1500
        )

        print(response)
        
        # Extract the translated code from the response
        translated_code = response.choices[0].message.content
        
        # Clean up the response to extract just the code
        if "```python" in translated_code:
            translated_code = translated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in translated_code:
            translated_code = translated_code.split("```")[1].strip()
            
        return translated_code
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return source_code

def translate_comments(code, source_language, target_language):
    """Translate comments in the code using google_trans_new"""
    try:
        lines = code.split('\n')
        translated_lines = []
        
        for line in lines:
            if '#' in line:
                code_part, comment_part = line.split('#', 1)
                translated_comment = translator.translate(comment_part.strip(), 
                                                       lang_src=get_language_code(source_language),
                                                       lang_tgt=get_language_code(target_language))
                translated_lines.append(f"{code_part}# {translated_comment}")
            else:
                translated_lines.append(line)
                
        return '\n'.join(translated_lines)
    except Exception as e:
        print(f"Comment translation error: {str(e)}")
        return code

def test_translation(code, source_language, target_language):
    """Main function to test code translation"""
    try:
        # First translate the code structure using GPT
        translated_code = translate_code_with_gpt(code, source_language, target_language)
        
        # Then translate any comments using google_trans_new
        translated_code_with_comments = translate_comments(translated_code, source_language, target_language)
        
        return translated_code_with_comments
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return code