def get_language_code(language):
    language_codes = {
        'English': 'en',
        'Hindi': 'hi',
        'French': 'fr',
        'Spanish': 'es',
        'Kurdish': 'ku',  # Kurdish (Kurmanji)
        'Bengali': 'bn',
        'Mandarin': 'zh-CN',  # Chinese (Simplified)
        'Greek': 'el'
    }
    return language_codes.get(language, 'en')