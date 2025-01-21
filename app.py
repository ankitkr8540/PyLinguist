import streamlit as st
import streamlit_ace
from server import test_translation

# Initialize session state
if 'source_index' not in st.session_state:
    st.session_state.source_index = 0  # Default to English
if 'target_index' not in st.session_state:
    st.session_state.target_index = 1  # Default to Hindi
if 'source_code' not in st.session_state:
    st.session_state.source_code = "print('Hello, World!')"
if 'translated_code' not in st.session_state:
    st.session_state.translated_code = ""
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'previous_translation_mode' not in st.session_state:
    st.session_state.previous_translation_mode = False

# Page setup
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; padding: 50px'>PyLinguist</h1>", unsafe_allow_html=True)

# Available languages
languages = ['English', 'Hindi', 'French', 'Spanish', 'Bengali', 'Mandarin', 'Greek']

# Translation mode selection
col1, col2 = st.columns(2)
with col1:
    use_chatgpt = st.checkbox("Use ChatGPT", value=False, key='translation_mode')
    
    # Clear translated code if translation mode changes
    if use_chatgpt != st.session_state.previous_translation_mode:
        st.session_state.translated_code = ""
        st.session_state.previous_translation_mode = use_chatgpt
    
    if use_chatgpt:
        st.write("Using ChatGPT to translate the code")
        if not st.session_state.api_key:
            st.session_state.api_key = st.text_input(
                "Enter your OpenAI API Key",
                type="password",
                value=st.secrets["openai"]['api_key']
            )
    else:
        st.write("Using Google Translator to translate the code")

# Add spacing
st.write("")
st.write("")

# Language selection
col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    source_language = st.selectbox(
        'Select a language to translate from',
        languages,
        index=st.session_state.source_index,
        key='source_language'
    )

with col3:
    target_language = st.selectbox(
        'Select a language to translate to',
        languages,
        index=st.session_state.target_index,
        key='target_language'
    )

# Update indices
st.session_state.source_index = languages.index(source_language)
st.session_state.target_index = languages.index(target_language)

# Add spacing
st.write("")
st.write("")

# Code editors
col1, col2 = st.columns(2)

with col1:
    code_input = streamlit_ace.st_ace(
        value=st.session_state.source_code,
        language='python',
        theme='monokai',
        keybinding='vscode',
        font_size=14,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        height=400,
        key=f'code_input_{st.session_state.editor_key}'
    )
    
    # Update source code
    if code_input != st.session_state.source_code:
        st.session_state.source_code = code_input
        st.session_state.translated_code = ""
    
    # Translation button
    if st.button('Translate', use_container_width=True):
        with st.spinner("Translating..."):
            translated = test_translation(
                st.session_state.source_code,
                source_language,
                target_language,
                use_chatgpt
            )
            if translated:
                st.session_state.translated_code = translated
                st.success("Translation complete!")
            else:
                st.error("Translation failed. Please try again.")

# Display translated code
with col2:
    if st.session_state.translated_code:
        streamlit_ace.st_ace(
            value=st.session_state.translated_code,
            language='python',
            theme='monokai',
            keybinding='vscode',
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=True,
            auto_update=True,
            height=400,
            readonly=True,
            key=f'translated_code_output_{st.session_state.editor_key}'
        )
    else:
        st.info("Waiting for translation...")