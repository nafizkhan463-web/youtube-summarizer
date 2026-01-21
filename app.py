import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 1. PAGE SETUP
st.set_page_config(page_title="My AI Agent", page_icon="🕵️")
st.title("🕵️ YouTube Video Analyst")

# 2. SIDEBAR
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Paste your Gemini API Key:", type="password")
    st.caption("Get a free key from Google AI Studio")

# 3. INPUT
url = st.text_input("Paste YouTube URL here:", placeholder="https://youtube.com/...")
analyze_button = st.button("Analyze Video")

# 4. HELPER FUNCTIONS
def get_transcript(video_id):
    try:
        # Tries to fetch transcript in English, Bengali, or Hindi (and auto-generated ones)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'bn', 'hi', 'en-US', 'en-GB'])
        formatter = TextFormatter()
        return formatter.format_transcript(transcript_list)
    except Exception as e:
        # If specific languages fail, try to list all and get the first available
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            # Just get the first available transcript (even if auto-generated)
            first_transcript = transcript_list.find_transcript(['en', 'bn', 'hi', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko']) 
            return first_transcript.fetch()
        except Exception as inner_e:
            return None

def extract_video_id(url):
    # Remove the extra tracking part (?si=...) if it exists
    if "?" in url:
        url = url.split("?")[0]
    
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return url

# 5. MAIN LOGIC
if analyze_button:
    if not api_key:
        st.error("Please enter your API Key in the sidebar first! 👈")
    elif not url:
        st.warning("Please paste a URL.")
    else:
        with st.spinner("🎧 Watching the video for you..."):
            video_id = extract_video_id(url)
            # We now format the transcript manually if the helper returns a raw list
            raw_transcript = get_transcript(video_id)
            
            # Convert list to text if needed
            if isinstance(raw_transcript, list):
                formatter = TextFormatter()
                transcript_text = formatter.format_transcript(raw_transcript)
            else:
                transcript_text = raw_transcript

        if not transcript_text:
            st.error("Could not find captions for this video. Note: This tool works on videos that have CC (Closed Captions) available.")
        else:
            with st.spinner("🧠 Thinking..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                You are a helpful assistant. Summarize this YouTube video.
                1. **Executive Summary**: 3 sentences max.
                2. **Key Learning Points**: A detailed bulleted list.
                
                TRANSCRIPT:
                {transcript_text}
                """
                
                response = model.generate_content(prompt)
                st.markdown("### 📝 Analysis Result")
                st.write(response.text)
