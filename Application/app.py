import streamlit as st
import pandas as pd
import streamlit_ace
import time
import os
import sys
from Backend.server import test_translation
# Import the service module
import Frontend.service as serv

# Initialize session state
if 'swap_requested' not in st.session_state:
    st.session_state.swap_requested = False
if 'source_index' not in st.session_state:
    st.session_state.source_index = 0  # Default to English
if 'target_index' not in st.session_state:
    st.session_state.target_index = 1  # Default to Hindi
if 'translated_code' not in st.session_state:
    st.session_state.translated_code = ""

def request_swap():
    """Request languages to be swapped"""
    # Store current indices
    temp_source = st.session_state.source_index
    st.session_state.source_index = st.session_state.target_index
    st.session_state.target_index = temp_source
    st.session_state.swap_requested = True

# Page setup
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; padding: 50px'>PyLinguist</h1>", unsafe_allow_html=True)

# Available languages
languages = ['English', 'Hindi', 'French', 'Spanish', 'Kurdish', 'Bengali', 'Mandarin', 'Greek']

# Language selection with swap button
col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    source_language = st.selectbox(
        'Select a language to translate from',
        languages,
        index=st.session_state.source_index,
        key='source_language'
    )
    source_language_code = serv.get_language_code(source_language)

with col2:
    st.write("")
    st.write("")
    if st.button('🔄 Swap Languages', on_click=request_swap):
        st.rerun()

with col3:
    target_language = st.selectbox(
        'Select a language to translate to',
        languages,
        index=st.session_state.target_index,
        key='target_language'
    )
    target_language_code = serv.get_language_code(target_language)

# Update indices based on current selections
st.session_state.source_index = languages.index(source_language)
st.session_state.target_index = languages.index(target_language)

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
        value="print('Hello, World!')",
        key='code_input'
    )
    
    def translate_code():
        translated_code = test_translation(code_input,source_language_code, target_language_code)
        st.session_state.translated_code = translated_code

    translate_button = st.button('Translate')
    if translate_button:
        with st.spinner("Translating..."):
            translate_code()
        st.success("Translation complete!")

with col2:
    if translate_button:
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
            key='translated_code_output',
            readonly=True
        )
    else:
        st.info("Waiting for translation...")