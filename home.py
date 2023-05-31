import openai
import streamlit as st
from streamlit_pills import pills
import os
from dotenv import load_dotenv




def init():
    load_dotenv()
    if "OPENAI_API_KEY" not in os.environ:
        st.error(
            "You need to set your OpenAI API key in environment variable OPENAI_API_KEY."
        )
        print("OPENAI_API_KEY not set in env")
        st.stop()
    st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")


def main():
    init()
    st.subheader("AI Assistant : Streamlit + OpenAI: `stream` *argument*")
    selected = pills("", ["NO Streaming", "Streaming"], ["🎈", "🌈"])
    user_input = st.text_input("You: ", placeholder="Ask me anything ...", key="input")


    if user_input:
        st.markdown("----")
        res_box = st.empty()
        if selected == "Streaming":
            report = []
            for resp in openai.Completion.create(
                model="text-davinci-003",
                prompt=user_input,
                max_tokens=120,
                temperature=0.5,
                stream=True,
            ):
                # join method to concatenate the elements of the list
                # into a single string,
                # then strip out any empty strings
                report.append(resp.choices[0].text)
                result = "".join(report).strip()
                result = result.replace("\n", "")
                res_box.markdown(f"*{result}*")

        else:
            completions = openai.Completion.create(
                model="text-davinci-003",
                prompt=user_input,
                max_tokens=120,
                temperature=0.5,
                stream=False,
            )
            result = completions.choices[0].text

            res_box.write(result)
    st.markdown("----")

if __name__ == "__main__":
    main()
