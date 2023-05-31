from logging import PlaceHolder
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

api_key = os.environ["OPENAI_API_KEY"]

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
# selected = pills("", ["Lifestyle", "Comparison", "Tech"], ["🎈", "🌈", "👨‍💻️"])

# prompt = st.text_input("Enter a topic for the blog post you want to generate")


# Templates
title_template = PromptTemplate(
        input_variables=["topic"], template="create a blog title for this TOPIC:{topic}."
)

content_template = PromptTemplate(
    input_variables=["title", "section_count", "special_instructions"],
    template="Create a blog outline template based on this title TITLE: {title} \
    include {section_count} sections and clearly define sections with the word SECTION and within each section include bullet points outlining the sections contenta. {special_instructions}",
)

content_intro = PromptTemplate(
    input_variables=["template"],
    template="Based on the following TEMPLATE: {template}  \
    Write me the blog introduction"
)

content_section1 = PromptTemplate(
    input_variables=["template"],
    template="Based on the following TEMPLATE: {template}  \
    Write me the blog content for the first 2 sections not including the introduction"
)


content_conclusion = PromptTemplate(
    input_variables=["template"],
    template="Based on the following TEMPLATE: {template}  \
    Write me the blog content for conclusion"
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

# sequential_chain = SequentialChain(
#     chains=[title_chain, template_chain],
#     input_variables=["topic"],
#     output_variables=["title", "template"],
#     verbose=True,
# )

# Show stuff to the screen if prompt

def main():
    st.write("how shall we make your blog post")
    with st.form('blog_form'):
        title_val = st.text_input("Title: Enter a title for the blog post you want to generate")
        topic_val = st.text_input("Topic: Only enter a topic if you have not entered a title")
        section_count = st.number_input("Sections: How many sections do you want in your blog post", min_value=1, max_value=10, value=5)
        special_instructions = st.text_input("Special Instructions: Any special instructions for the blog post", placeholder="include details of the origin")
        submitted = st.form_submit_button(label='Submit')

    if submitted:
        with get_openai_callback() as cb:
            if title_val:
                title = title_val
            else:
                with st.spinner("Generating Post Title"):
                    title = title_chain.run({"topic": topic_val})
            '### Template'
            display_title = title.replace('"', '')
            with st.spinner("Generating Post Template"):
                blog_template = template_chain.run({"title": title, "section_count": section_count, "special_instructions": special_instructions})
            st.write(blog_template)
            f'## {title}'
            sections = blog_template.split("SECTION")
            for i, section in enumerate(sections[1:]):
                section_title = section.split("\n")[0]
                section_template = PromptTemplate(
                    input_variables=["template"],
                    template="Based on the following TEMPLATE: {template}  \
                    Write me the blog content for section no" + str(i + 1),
                )
                chain = LLMChain(
                    llm=llm,
                    prompt=section_template,
                    verbose=True,
                    output_key="section",
                )
                with st.spinner(f"Generating section {i + 1}"):
                    response = chain.run({"template": blog_template})
                st.write(section_title)
                st.write(response.replace('SECTION', ''))
        '## Details of Generation'
        st.write(cb)

        # with st.spinner("Generating Content"):
        #     intro = intro_chain.run({"template": response["template"]})
        #     section1 = content1_chain.run({"template": response["template"]})
        #     section2 = content2_chain.run({"template": response["template"]})
        #     conclusion = conclusion_chain.run({"template": response["template"]})
        # st.write(intro)
        # st.write(section1)
        # st.write(section2)
        # st.write(conclusion)


if __name__ == "__main__":
        main()
