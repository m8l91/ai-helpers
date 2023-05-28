from dotenv import load_dotenv
import os
import openai
import streamlit as st

def init():
    if "api_secret" not in st.secrets:
        st.error(
            "You need to set your OpenAI API key in the secrets management page."
        )
        st.stop()
    else:
        openai.api_key = st.secrets["api_secret"]
    st.set_page_config(page_title="AI PDF-Reader Assistant", page_icon="🤖", layout="wide")

def main():
    init()
    st.header("Ask your PDF")
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    

if __name__ == "__main__":
    main()
