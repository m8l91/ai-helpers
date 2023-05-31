# Ai assistant

A collection of bots using Open AI llms to make tasks easier.

Each page has a specific specialised task All will be billed to the account of the api key provided
## Usage
### Python
create .env file with OPENAI_API_KEY
pip install -r requirements.txt

streamlit run home.py
### Docker
docker run -e OPENAI_API_KEY="" -p 8501:8501 devcose/ai-helpers
## Included Pages
### Home
Basic AI assistant with the option of streaming text

### Blog post Generator
Generate a full blog post from just a title or a topic. You can add some customisations in the special requests field.
### Ask Your Document
Takes your documents accepts PDF Docx or txt and converts them into vectors and is then able to answer questions on the specifics this has two options either temporarily store the file and ask questions based on just one file

or Connect to a pinecone index and upload as many as you like. For this to work additional env variables must be provided `PINECONE_API_KEY` `PINECONE_ENV`
Takes your documents converts them into vectors and is then able to answer questions on the specifics

### Chat Bot With Memory
