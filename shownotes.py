import streamlit as st
from pydub import AudioSegment
from io import BytesIO
import os
import requests
from dotenv import load_dotenv

# Laad de OpenAI API key uit .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verzeker dat de podcast_parts map bestaat
podcast_parts_dir = "podcast_parts"
os.makedirs(podcast_parts_dir, exist_ok=True)

def split_and_save_audio(audio_file, chunk_length_ms=300000):  # 300000ms = 5 minuten
    audio = AudioSegment.from_file(audio_file)
    original_filename = os.path.splitext(os.path.basename(audio_file.name))[0]
    
    chunk_paths = []
    for i, start in enumerate(range(0, len(audio), chunk_length_ms), start=1):
        end = start + chunk_length_ms if start + chunk_length_ms < len(audio) else len(audio)
        chunk = audio[start:end]
        
        part_filename = f"{original_filename}_part_{i}.mp3"
        part_path = os.path.join(podcast_parts_dir, part_filename)
        chunk.export(part_path, format="mp3")
        
        chunk_paths.append(part_path)
    return chunk_paths

def get_transcript(audio_file_path, language):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {
        "model": "whisper-1",
        "language": language,
        "response_format": "verbose_json",
        "timestamp_granularities[]": "segment",
    }
    
    with open(audio_file_path, 'rb') as audio_file:
        files = {"file": (os.path.basename(audio_file_path), audio_file, "audio/mp3")}
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Kon de transcriptie niet ophalen, status code: " + str(response.status_code)}

def generate_shownotes(transcript_json, time_range):
    segments = transcript_json.get('segments', [])
    segments_str = '\n'.join([f"Start: {seg['start']}s, Einde: {seg['end']}s, Tekst: {seg['text']}" for seg in segments])

    context = "Je bent een redacteur die helpt bij het genereren van shownotes voor podcast afleveringen. Focus op de belangrijkste punten en onderwerp wisselingen. Produceer de output in een specifieke opmaak: eerst een lijst van topics en bijbehorende timecodes in hele seconden, gevolgd door een opsomming van artikelen of nieuwsfeiten waarnaar in de segmenten gerefereerd wordt."
    prompt = (f"Het volgende segment, van {time_range}, bevat de volgende segmentinformatie:\n{segments_str}\n\n"
              "Op basis van deze informatie, genereer een geordende lijst van topics en timecodes. "
              "Vervolgens, mochten in het artikel specifieke nieuwsartikelen, producten of websites worden besproken, noteer deze dan per onderwerp. Verzin nooit wat zelf maar kijk alleen in het transcript."
              "Zorg ervoor dat de output gestructureerd en duidelijk georganiseerd is volgens de aangegeven opmaak.")

    combined_input = f"{context}\n\n{prompt}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4",
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
        return None
    
def consolidate_shownotes(all_shownotes):
    context = "Je bent eindredacteur voor een podcast. Bijgevoegd zie je de gegenereerde shownotes voor een podcast aflevering, deze shownotes zijn per 5 minuten gegenereerd. Voeg alle shownotes samen en maak er 1 chronologische lijst van shownotes van. Indien nodig, voeg onderwerpen samen, zorg dat de tijdsaanduidingen overeenkomen met de totale aflevering. Hou het format van de shownotes hetzelfde."

    # Combineer alle shownotes tot één enkele string
    shownotes_str = "\n\n".join(all_shownotes)

    prompt = f"{context}\n\nHier zijn de shownotes:\n{shownotes_str}\n\nKun je deze samenvoegen tot één chronologische lijst, alsjeblieft?"

    combined_input = prompt

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4",
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
        return None

def run_streamlit_app():
    st.title('Podcast Splitter en Transcriptie')

    # Tabbladen aanmaken
    tab1, tab2 = st.tabs(["Shownotes Genereren", "Redactie"])

    # Variabele om alle shownotes op te slaan voor het "Redactie" tabblad
    all_shownotes = []

    with tab1:
        uploaded_file = st.file_uploader("Upload je podcast", type=['mp3', 'wav'])

        if uploaded_file is not None:
            chunk_paths = split_and_save_audio(uploaded_file)
            language = st.selectbox("Kies de taal van de audio", ["nl", "en", "de", "fr"], index=0)

            for i, chunk_path in enumerate(chunk_paths, start=1):
                transcript_response = get_transcript(chunk_path, language)
                if "error" in transcript_response:
                    st.error(transcript_response["error"])
                    continue

                time_range = f"{5*(i-1)} tot {5*i} minuten"
                shownotes = generate_shownotes(transcript_response, time_range)
                if shownotes:
                    st.markdown(f"### Shownotes voor segment {time_range}")
                    st.write(shownotes)
                    all_shownotes.append(shownotes)
                else:
                    st.error("Er is een fout opgetreden bij het genereren van de shownotes.")

    with tab2:
        st.markdown("## Alle Shownotes Consolideren")
        if st.button("Consolideer Shownotes"):
            if all_shownotes:
                consolidated_shownotes = consolidate_shownotes(all_shownotes)
                if consolidated_shownotes:
                    st.markdown("### Geconsolideerde Shownotes")
                    st.write(consolidated_shownotes)
                else:
                    st.error("Er is een fout opgetreden bij het consolideren van de shownotes.")
            else:
                st.error("Geen shownotes beschikbaar om te consolideren. Voer eerst de transcriptie uit in Tabblad 1.")


if __name__ == "__main__":
    run_streamlit_app()
