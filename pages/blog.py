import os

import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain, SequentialChain, ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.utilities import WikipediaAPIWrapper
from langchain.callbacks import get_openai_callback
from streamlit_pills import pills
import tiktoken

api_key = st.secrets['api_secret']
os.environ["OPENAI_API_KEY"] = api_key

# Count Tokens function
def count_tokens(chain, query):
    with get_openai_callback() as cb:
        result = chain.run(query)
        print(f"Spent a total of {cb.total_tokens} tokens")
    return result

# App Framework
# Sidebar
# sidebar = st.sidebar.radio('Style of Post:', ['Lifestyle', "Comparison","Tech"])
st.title("Blog Post Generator")
selected = pills("", ["Lifestyle", "Comparison", "Tech"], ["🎈", "🌈", "👨‍💻️"])

prompt = st.text_input("Enter a topic for the blog post you want to generate")


# Templates
title_template = PromptTemplate(
        input_variables=["topic"], template="create a blog title for this TOPIC:{topic}."
)

content_template = PromptTemplate(
    input_variables=["title"],
    template="Create a blog outline template based on this title TITLE: {title} \
    Include possible sections and within each section include bullet points outlining the sections content",
)

content_content = PromptTemplate(
    input_variables=["template"],
    template="Based on the following TEMPLATE: {template}  \
    Write me the blog content in total the blog post should be around 2000 words.",
)
# Memory
title_memory = ConversationBufferMemory(input_key="topic", memory_key="title_history")
script_memory = ConversationBufferMemory(input_key="template", memory_key="chat_history")
template_memory = ConversationBufferMemory(input_key="title", memory_key="template_history")

# LLMS
llm = OpenAI(verbose=True, temperature=0.9, model="text-davinci-003")

title_chain = LLMChain(
    llm=llm,
    prompt=title_template,
    verbose=True,
    output_key="title",
    memory=title_memory,
)

template_chain = LLMChain(
    llm=llm,
    prompt=content_template,
    verbose=True,
    output_key="template",
    memory=template_memory,
)

content_chain = LLMChain(
    llm=llm,
    prompt=content_content,
    verbose=True,
    output_key="content",
    memory=script_memory,
)

sequential_chain = SequentialChain(
    chains=[title_chain, template_chain, content_chain],
    input_variables=["topic"],
    output_variables=["title", "template", "content"],
    verbose=True,
)

# Show stuff to the screen if prompt
if prompt:
    response = sequential_chain({"topic": prompt})
    st.write(response["title"])
    st.write(response["template"])
    st.write(response["content"])
    # st.write(response["template"])
    with st.expander("Message History"):
        st.info(script_memory.buffer)
