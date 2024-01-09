import streamlit as st
from dotenv import load_dotenv
import requests  # Voor API-aanroepen
import os

# Importeer de benodigde onderdelen van langchain
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI  # Voor het taalmodel
from langchain.memory import ConversationBufferMemory  # Voor het geheugen van de conversatie
from langchain.chains import ConversationalRetrievalChain  # Voor de retrieval chain


# Functie om tekst uit e-mailbestanden te extraheren
def get_email_text(email_docs):
    text = ""
    for email in email_docs:
        text += email.getvalue().decode("utf-8")
    return text

# Functie om tekst in kleinere stukken op te splitsen
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Functie om een vectoropslagplaats te maken van tekstfragmenten
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Functie om tekst naar spraak te converteren met ElevenLabs API
def text_to_speech(text, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"text": text}
    response = requests.post("https://api.elevenlabs.io/synthesize", headers=headers, json=data)
    if response.status_code == 200:
        # Bewaar het gegenereerde MP3-bestand
        with open("generated_audio.mp3", "wb") as audio_file:
            audio_file.write(response.content)
        return "generated_audio.mp3"
    else:
        st.error("Fout bij het genereren van de spraak")
        return None
    
# Functie om podcast scripts te genereren
def generate_podcast_script(vectorstore, prompt):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    generated_script = conversation_chain.generate(prompt)
    return generated_script


#Functie om het script om te zetten in speech
def text_to_speech(text, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"text": text}
    response = requests.post("https://api.elevenlabs.io/synthesize", headers=headers, json=data)
    if response.status_code == 200:
        audio_file_path = 'generated_audio.mp3'
        with open(audio_file_path, 'wb') as file:
            file.write(response.content)
        return audio_file_path
    else:
        st.error("Fout bij het genereren van de spraak")
        return None



def run():
    load_dotenv()
    st.title("WillemGPT🍺")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")  # Haal de ElevenLabs API-sleutel op

    tab1, tab2 = st.tabs(["E-mails Uploaden", "Luister naar Audio"])

    with tab1:
        st.subheader("Upload je e-mails")
        email_docs = st.file_uploader("Kies bestanden", accept_multiple_files=True, type=["txt", "eml"])
        prompt = st.text_area("Voer de prompt in voor het genereren van het script")
        if st.button("Verwerken"):
            with st.spinner("Verwerken..."):
                raw_text = get_email_text(email_docs)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                podcast_script = generate_podcast_script(vectorstore, prompt)
                audio_file_path = text_to_speech(podcast_script, elevenlabs_api_key)
                if audio_file_path:
                    st.session_state.audio_file_path = audio_file_path

    with tab2:
        st.subheader("AI gegenereerde audio")
        if "audio_file_path" in st.session_state:
            st.audio(st.session_state.audio_file_path, format='audio/mp3')
        else:
            st.write("Upload en verwerk eerst e-mails om de audio te genereren.")

if __name__ == "__main__":
    run()
