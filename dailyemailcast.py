import streamlit as st
import email
from email import policy
from email.parser import BytesParser
from openai import OpenAI  
import requests
from decouple import config
from pathlib import Path  
import os

def get_email_text(email_docs):
    print("Extracting text from emails...")
    text = ""
    for email_file in email_docs:
        msg = BytesParser(policy=policy.default).parsebytes(email_file.getvalue())
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    text += part.get_payload(decode=True).decode()
        else:
            text += msg.get_payload(decode=True).decode()
    return text


def query_openai_with_context(prompt, context):
    print("Querying OpenAI with context and prompt...")
    combined_input = f"{context}\n\n{prompt}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config('OPENAI_API_KEY')}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": combined_input}
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("API-call failed, status code:", response.status_code)
        print("Respons:", response.text)
        return None

def get_audio_tts(text, voice):
    client = OpenAI()

    # Path to audiofile
    speech_file_path = Path(__file__).parent / "speech.mp3"

    # Call to OpenAI with selected voice.
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice.lower(), 
        input=text
    )

    # safe audio to file
    response.stream_to_file(speech_file_path)

    # return path to audiofile
    return speech_file_path

def get_prompts():
    # Reed every prompt in the prompts folder and return prompts
    prompts_dir = Path(__file__).parent / "prompts"
    prompts = {}
    for file in os.listdir(prompts_dir):
        if file.endswith(".txt"):
            with open(prompts_dir / file, 'r') as f:
                prompts[file.replace('.txt', '')] = f.read()
    return prompts


def run():
    st.title("email podcast creator")
    st.markdown("""
        upload your emails (as .eml) and click on process.
    """)

    # voice selector
    voice = st.selectbox("Kies een stem", ["Alloy", "Echo", "Fable", "Onyx", "Nova", "Shimmer"])

    # Podcast style selector
    prompts = get_prompts()
    style = st.selectbox("Choose a podcast style", list(prompts.keys()))

    email_docs = st.file_uploader("Choose email files", accept_multiple_files=True)

    if st.button("Process"):
        with st.spinner("Processing..."):
            raw_text = get_email_text(email_docs)
            if style in prompts:
                prompt = prompts[style]  # Use selecteed prompt
                ai_output = query_openai_with_context(prompt, raw_text)
                mp3_audio_path = get_audio_tts(ai_output, voice)  # Use selected voice
                if mp3_audio_path:
                    with open(mp3_audio_path, 'rb') as audio_file:
                        st.audio(audio_file.read(), format="audio/mpeg")
                else:
                    st.write("Error while generating audio.")
            else:
                st.write("Please select a style and voice to proceed.")
            print("Processing complete.")

if __name__ == "__main__":
    run()
