import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 1. PAGE SETUP
st.set_page_config(page_title="My AI Agent", page_icon="🕵️")
st.title("🕵️ YouTube Video Analyst")

# 2. SIDEBAR FOR API KEY
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Paste your Gemini API Key:", type="password")
    st.caption("Get a free key from Google AI Studio")

# 3. INPUT AREA
url = st.text_input("Paste YouTube URL here:", placeholder="https://youtube.com/...")
analyze_button = st.button("Analyze Video")

# 4. HELPER FUNCTIONS
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript_list)
    except Exception as e:
        return None

def extract_video_id(url):
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
            transcript_text = get_transcript(video_id)

        if not transcript_text:
            st.error("Could not find captions for this video. Try a different one!")
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
