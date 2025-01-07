import streamlit as st
import streamlit_ace
from server import test_translation

# Initialize session state
if 'swap_requested' not in st.session_state:
    st.session_state.swap_requested = False
if 'source_index' not in st.session_state:
    st.session_state.source_index = 0  # Default to English
if 'target_index' not in st.session_state:
    st.session_state.target_index = 1  # Default to Hindi
if 'source_code' not in st.session_state:
    st.session_state.source_code = "print('Hello, World!')"
if 'translated_code' not in st.session_state:
    st.session_state.translated_code = ""
if 'previous_source_lang' not in st.session_state:
    st.session_state.previous_source_lang = None
if 'previous_target_lang' not in st.session_state:
    st.session_state.previous_target_lang = None
if 'editor_key' not in st.session_state:
    st.session_state.editor_key = 0

def request_swap():
    """Request languages to be swapped"""
    # Swap languages
    temp_source = st.session_state.source_index
    st.session_state.source_index = st.session_state.target_index
    st.session_state.target_index = temp_source
    
    # Swap code content
    if st.session_state.translated_code:  # Only swap if there is translated code
        temp_code = st.session_state.source_code
        st.session_state.source_code = st.session_state.translated_code
        st.session_state.translated_code = temp_code
        
        # Increment editor key to force re-render
        st.session_state.editor_key += 1
    
    st.session_state.swap_requested = True

# Page setup
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; padding: 50px'>PyLinguist</h1>", unsafe_allow_html=True)

# Available languages
languages = ['English', 'Hindi', 'French', 'Spanish', 'Bengali', 'Mandarin', 'Greek']

# Language selection with swap button
col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    source_language = st.selectbox(
        'Select a language to translate from',
        languages,
        index=st.session_state.source_index,
        key='source_language'
    )
    source_language_code = source_language

# with col2:
#     st.write("")
#     st.write("")
#     if st.button('🔄 Swap Languages', on_click=request_swap):
#         st.rerun()

with col3:
    target_language = st.selectbox(
        'Select a language to translate to',
        languages,
        index=st.session_state.target_index,
        key='target_language'
    )
    target_language_code = target_language

# Update indices based on current selections
st.session_state.source_index = languages.index(source_language)
st.session_state.target_index = languages.index(target_language)

# Track language changes
if (st.session_state.previous_source_lang != source_language or 
    st.session_state.previous_target_lang != target_language):
    if not st.session_state.swap_requested:  # Only clear if not swapping
        st.session_state.translated_code = ""
    st.session_state.previous_source_lang = source_language
    st.session_state.previous_target_lang = target_language

# give padding below the language selection
st.write("")
st.write("")
st.write("")
# Code editors
col1, col2 = st.columns(2)

with col1:
    code_input = streamlit_ace.st_ace(
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
        value=st.session_state.source_code,
        key=f'code_input_{st.session_state.editor_key}'  # Dynamic key
    )
    
    # Update source code in session state when editor content changes
    if code_input != st.session_state.source_code:
        st.session_state.source_code = code_input
        st.session_state.translated_code = ""  # Clear previous translation
    
    def translate_code():
        translated_code = test_translation(st.session_state.source_code, 
                                        source_language_code, 
                                        target_language_code)
        st.session_state.translated_code = translated_code

    translate_button = st.button('Translate')
    if translate_button:
        with st.spinner("Translating..."):
            translate_code()
        st.success("Translation complete!")

with col2:
    if st.session_state.translated_code:
        translated_code_output = streamlit_ace.st_ace(
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
            value=st.session_state.translated_code,
            key=f'translated_code_output_{st.session_state.editor_key}',  # Dynamic key
            readonly=True
        )
    else:
        st.info("Waiting for translation...")

# Reset swap flag at the end of the script
if st.session_state.swap_requested:
    st.session_state.swap_requested = False