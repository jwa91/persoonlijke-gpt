import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from langchain_community.embeddings.huggingface import HuggingFaceInstructEmbeddings

# Lijst van Huggingface modellen
HUGGINGFACE_MODELS = {
    "google/flan-t5-xxl": "Flan-T5-XXL door Google - Geoptimaliseerd voor veelzijdige tekstgeneratie taken",
    "databricks/dolly-v2-3b": "Dolly V2-3B door Databricks - Gericht op beeldbeschrijving en creatieve inhoud",
    "Writer/camel-5b-hf": "Camel-5B door Writer - Geschikt voor content creatie en tekstbewerking",
    "Salesforce/xgen-7b-8k-base": "XGen-7B door Salesforce - Geavanceerd voor diverse tekstgeneratie taken",
    "tiiuae/falcon-40b": "Falcon-40B door Technology Innovation Institute - Geoptimaliseerd voor kennisintensieve taken",
    "internlm/internlm-chat-7b": "InternLM-Chat-7B door Shanghai AI Laboratory - Specifiek ontworpen voor conversatiedoeleinden",
    "Qwen/Qwen-7B": "Qwen-7B door Alibaba Cloud - Veelzijdig groot taalmodel, geschikt voor diverse taken",
    "01-ai/Yi-34B": "Yi-34B door 01.ai - Groot taalmodel voor Engelstalige en Chinese tekstgeneratie"
}



def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    # embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore, model_name):
    llm = HuggingFaceHub(repo_id=model_name, model_kwargs={"temperature":0.5, "max_length":512})
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)



def run():
    load_dotenv()
    st.title("WillemGPT🍺")
    st.write(css, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Documenten Uploaden en instellingen", "Chat"])

    with tab1:
        st.subheader("Upload je PDFs")
        # Markdown uitleg
        st.markdown("""
            Voeg 1 of meerdere pdf bestanden toe door ze te slepen of te selecteren. Voor de keuze van het [embeddings](https://en.wikipedia.org/wiki/Word_embedding) 
            model kun je de `get_vectorstore` functie gebruiken. Voor de keuze van het [LLM](https://en.wikipedia.org/wiki/Large_language_model) 
            gebruik je de `LLM` kies je een LLM uit deze lijst. Hou er rekening mee dat het lokaal uitvoeren van de Vector Embeddings een enorm zware operatie is.
            gebruik het [Huggingface leaderboard](https://huggingface.co/spaces/mteb/leaderboard) om een goede keuze te maken.
        """)
        pdf_docs = st.file_uploader("Kies bestanden", accept_multiple_files=True, key="pdf_uploader")
        
        # Dropdown voor het kiezen van een LLM-model
        model_choice = st.selectbox("Kies een LLM-model voor antwoorden:", HUGGINGFACE_MODELS, key="llm_model_choice")

        if st.button("Verwerken PDF", key="pdf_verwerken"):
            with st.spinner("Verwerken..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vectorstore, model_choice)    

    with tab2:
        if "conversation" not in st.session_state:
            st.session_state.conversation = None
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None

        user_question = st.text_input("Stel een vraag over je documenten:")
        if user_question:
            handle_userinput(user_question)

if __name__ == "__main__":
    run()