import streamlit as st
import requests
import base64
from gtts import gTTS
from googletrans import Translator
import os
import asyncio

# Function to translate text to Hindi using googletrans.
def translate_to_hindi(text):
    translator = Translator()
    try:
        # Use asyncio.run to await the translation coroutine.
        translation = asyncio.run(translator.translate(text, dest='hi'))
        return translation.text
    except Exception as e:
        st.error("Translation error: " + str(e))
        return text

# Function to generate Hindi TTS audio using gTTS.
def generate_tts(text):
    try:
        if not text:
            raise ValueError("Empty text provided for TTS generation.")
        tts = gTTS(text=text, lang='hi')
        audio_file = "temp_audio.mp3"
        tts.save(audio_file)
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        os.remove(audio_file)
        return audio_bytes
    except Exception as e:
        st.error("TTS generation error: " + str(e))
        return None

st.title("News Summarization and Hindi TTS Application")

# Input for company name
company = st.text_input("Enter Company Name", placeholder="e.g., Tesla")

if st.button("Analyze") and company:
    try:
        # Call the backend API (ensure your API backend is running on localhost:5000)
        response = requests.post("http://localhost:5000/analyze", json={"company": company})
        if response.status_code == 200:
            data = response.json()
            st.header(f"Company: {data.get('Company', '')}")
            
            st.subheader("Articles")
            for art in data.get("Articles", []):
                st.markdown(f"**Title:** {art.get('Title', '')}")
                st.markdown(f"**Summary:** {art.get('Summary', '')}")
                st.markdown(f"**Sentiment:** {art.get('Sentiment', '')}")
                st.markdown(f"**Topics:** {', '.join(art.get('Topics', []))}")
                st.markdown("---")
            
            st.subheader("Comparative Sentiment Score")
            st.json(data.get("Comparative Sentiment Score", {}))
            
            st.subheader("Final Sentiment Analysis")
            final_sent = data.get("Final Sentiment Analysis", "")
            st.write(final_sent)
            
            # Generate Hindi TTS for the final sentiment analysis.
            hindi_text = translate_to_hindi(final_sent)
            st.write("Hindi Summary: ", hindi_text)
            audio_bytes = generate_tts(hindi_text)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
            else:
                st.write("Hindi TTS generation failed.")
        else:
            st.error("Error: " + response.json().get('error', 'Unknown error'))
    except Exception as e:
        st.error("An error occurred: " + str(e))
elif st.button("Analyze") and not company:
    st.warning("Please enter a company name.")
