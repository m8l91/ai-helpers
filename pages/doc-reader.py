from dotenv import load_dotenv
import os
import openai
import streamlit as st
from streamlit_pills import pills
from io import StringIO
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Pinecone
from langchain.callbacks import get_openai_callback
import pdftotext
import pinecone
import docx



llm = OpenAI(temperature=0.5)
sidebar = None

def init():
    load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        st.error(
            "You need to set your OpenAI API key in environment variable OPENAI_API_KEY."
        )
        print("OPENAI_API_KEY not set in env")
    st.set_page_config(
        page_title="AI PDF-Reader Assistant", page_icon="🤖", layout="wide"
    )
    global sidebar
    sidebar = st.sidebar.radio('Source of Data:', ["Upload", "Database"])
    '# Document Helper'
    print(sidebar)
    if sidebar == "Database":
        print("using Database for documents")
        if "PINECONE_API_KEY" not in os.environ:
            st.write(
            "You need to set your PINECONEAPI key in environment variable PINECONE_API_KEY "
                    )
            st.stop()
        else:
            PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
            PINECONE_ENV = os.environ["PINECONE_ENV"]
            pinecone.init(
                    api_key=os.environ['PINECONE_API_KEY'],  # find at app.pinecone.io
                    environment=os.environ['PINECONE_ENV']  # next to api key in console
                    )
    return sidebar

def doc_to_text(uploaded_file):
    print(uploaded_file.type)

    if uploaded_file.type == "application/pdf":
        pdf = pdftotext.PDF(uploaded_file)
        st.write("PDF Loaded")

        # pdf_reader = PdfReader(uploaded_file)
        string_data = ""
        for page in pdf:
            string_data += page
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        full_text= [] 
        for para in doc.paragraphs:
            full_text.append(para.text)
        string_data = "\n".join(full_text)
        st.write("Docx Loaded")
    else:
        bytes_data = uploaded_file.getvalue()
        # Convert to string
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        # st.write(stringio)
        #
        # Read string
        string_data = stringio.read()
        # st.write(string_data)
    return string_data


    

  
def make_chunks(string_data, seperator="\n", chunk_size=1000, chunk_overlap=200, length_function=len):
    
    splitter = CharacterTextSplitter(
        separator=seperator,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    chunks = splitter.split_text(string_data)
    return chunks

def query_answer(user_input, docs):
    chain = load_qa_chain(llm, chain_type="stuff")
    with get_openai_callback() as cb:
        answer = chain.run(input_documents=docs, question=user_input)
        print(cb)
    return answer

def single_file():
    # Upload File
    uploaded_file = st.file_uploader("Upload your PDF")
    if uploaded_file is not None:
        st.write("File Uploaded")
        # Convert file to string
        string_data = doc_to_text(uploaded_file)
        # Split text
        chunks = make_chunks(string_data)

        # Create Embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        user_input = st.text_input("Ask a question")
        if user_input:
            docs = knowledge_base.similarity_search(user_input)
            # st.write(docs)
            # get answer
            answer = query_answer(user_input, docs)
            st.write(answer)


### DB Specific Funtions
# Create Embeddings and upload to pinecone
@st.cache_data
def get_namespaces_of_index(index):
    index= pinecone.Index(index)
    index_stats = index.describe_index_stats()
    namespaces = list(index_stats['namespaces'].keys())
    return namespaces
    # return active_namespaces

def create_namespace(index_name, namespace):
    index= pinecone.Index(index_name)
    # index.upsert(vectors=[('id-1', [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])],
    #          namespace=namespace)
    create_vectors(["first-entry"], index_name, namespace)

def create_vectors(chunks, index_name, namespace):
    embeddings = OpenAIEmbeddings()
    try:
        Pinecone.from_texts(chunks, embeddings, index_name=index_name, namespace=namespace)
    except Exception as e:
        print(e)
        st.write(f"File Not Uploaded Error: {e}")
    else:
        st.write("File Uploaded successfully")
        print('vectors uploaded')


# Upload vectors to index Not needed with Langchain Pinecone class
def upload_vectors(vectors, index, namepsace='default'):
     index = pinecone.Index(index)
     upsert_response = index.upsert(
             vectors=vectors,
             namespace=namepsace
             )
     print(upsert_response)
     return upsert_response

def query_index():
    active_indexes = pinecone.list_indexes()
    index = pinecone.Index("novel")
    embeddings = OpenAIEmbeddings()
    docsearch = Pinecone.from_existing_index(active_indexes[0], embeddings)
    return docsearch


@st.cache_data(show_spinner="Fetching Data from Database")
def get_indexes():
    active_indexes = pinecone.list_indexes()
    return active_indexes


def db_fun():
    active_indexes = get_indexes()
    if active_indexes != []:
        st.write("Indexes Found")
        selected_index = pills("Choose index", active_indexes)
        active_namespaces = get_namespaces_of_index(selected_index)
        active_namespaces.append('create-new-namespace')
        selected_namespace, new_namespace = st.columns([.5,1])
        with selected_namespace:
            selected_namespace = pills("Choose space", active_namespaces)
        if selected_namespace == 'create-new-namespace':
            with new_namespace:
                new_namespace = st.text_input("Create new space")
            if new_namespace:
                create_namespace(selected_index, new_namespace)
                st.cache_data.clear()

        uploaded_file = st.file_uploader("Add Data to your index")
        if uploaded_file is not None:
            # Upload File to Index
            string_data = doc_to_text(uploaded_file)
            # Vectorize
            chunks = make_chunks(string_data)
            create_vectors(chunks, index_name=selected_index, namespace=selected_namespace)
            # clear uploaded file
            uploaded_file = None
            

        knowledge_base = query_index()
        user_input = st.text_input("Ask a question")
        if user_input:
            docs = knowledge_base.similarity_search(user_input)
            # st.write(docs)
            # get answer
            answer = query_answer(user_input, docs)
            st.write(answer)
    else:
        st.write("No Indexes Found")


def main():
    init()
    if sidebar == "Database":
        st.header("Ask your Index")
        db_fun()
    else:
        st.header("Ask your Document")
        single_file()


if __name__ == "__main__":
    main()
