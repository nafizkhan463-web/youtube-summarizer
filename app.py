import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

st.set_page_config(page_title="Debug Mode Agent", page_icon="🛠️")
st.title("🛠️ YouTube Analyst (Debug Mode)")

# Sidebar
with st.sidebar:
    api_key = st.text_input("Gemini API Key", type="password")

# Input
url = st.text_input("YouTube URL")
analyze = st.button("Analyze")

def extract_video_id(url):
    # 1. Clean the URL of tracking extras
    if "?" in url:
        url = url.split("?")[0]
    # 2. Extract ID
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return url

if analyze:
    if not api_key:
        st.error("Please enter API Key.")
    elif not url:
        st.error("Please enter URL.")
    else:
        video_id = extract_video_id(url)
        st.info(f"Detected Video ID: {video_id}") # Debug print
        
        try:
            # Try to get ANY transcript directly
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Just grab the first available one (English, Bengali, Auto-generated, anything)
            transcript = None
            for t in transcript_list:
                st.write(f"Found transcript language: {t.language} ({t.language_code})")
                transcript = t.fetch()
                break # Stop after finding the first one

            if transcript:
                # Format text
                formatter = TextFormatter()
                text = formatter.format_transcript(transcript)
                
                # Send to Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Summarize this: {text}")
                
                st.success("Success!")
                st.write(response.text)
            else:
                st.error("No transcript found in the list.")

        except Exception as e:
            # THIS IS THE IMPORTANT PART: Print the exact error
            st.error(f"❌ A Technical Error Occurred:")
            st.code(str(e))
            st.warning("If the error says 'VideoUnavailable', check the link. If it says 'Sign in required', YouTube is blocking the server.")
