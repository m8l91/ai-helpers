import os

# Streamlit
import streamlit as st
from streamlit_pills import pills
from streamlit_chat import message

# Langchain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from langchain.chains import (
    LLMChain,
    SimpleSequentialChain,
    SequentialChain,
    ConversationChain,
)
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.utilities import WikipediaAPIWrapper
from langchain.callbacks import get_openai_callback
import tiktoken

api_key = st.secrets["api_secret"]
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
st.title("conversation")
with st.sidebar:
    user_input = st.text_input("User Input", key="user_input")

placeholder = st.empty()
prompt = st.text_input("Enter your query")

# LLMS
# llm = OpenAI(verbose=True, temperature=0.9, model="text-davinci-003")
chat = ChatOpenAI(verbose=True, temperature=0.9) 
# Memory
# conversation_memory = ConversationSummaryMemory(llm=llm)
conversation_memory = ConversationBufferMemory()


# conversation = ConversationChain(
#     llm=llm,
#     verbose=True,
#     output_key="conversation",
#     memory=conversation_memory,
# )
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="Hello, how can I help you?")
    ]
# Show stuff to the screen if prompt
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.session_state.messages.append(AIMessage(content="thinking"))
    response = chat(st.session_state.messages)
    st.session_state.messages.pop()
    st.session_state.messages.append(AIMessage(content=response.content))

messages = st.session_state.get('messages', [])
with placeholder.container():
    for i, msg in enumerate(messages[1:]):
        if i % 2 == 0:
            message(msg.content, is_user=True, key=str(i) + '_user')
        else:
            message(msg.content, is_user=False, key=str(i) + '_AI')
    # st.write(response["template"])
    # st.write(response["content"])
    # st.write(response["template"]) 
    # with st.expander("Message History"):
    #     st.info(conversation_memory.buffer)
