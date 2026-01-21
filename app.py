import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# --- PAGE SETUP ---
st.set_page_config(page_title="Universal AI Agent", page_icon="🤖")
st.title("🤖 YouTube Analyst (Universal Fix)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Settings")
    api_key = st.text_input("Gemini API Key", type="password")

# --- INPUT ---
url = st.text_input("Paste YouTube URL here:")
analyze = st.button("Analyze Video")

# --- LOGIC ---
def extract_video_id(url):
    # Fix the URL tracking issue
    if "?" in url:
        url = url.split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return url

if analyze:
    if not api_key:
        st.error("Please enter API Key in the sidebar.")
    elif not url:
        st.error("Please paste a URL.")
    else:
        video_id = extract_video_id(url)
        
        # 1. TRY TO GET TRANSCRIPT (The Old School Way)
        transcript = None
        try:
            # We ask for English, OR Bengali, OR Hindi explicitly
            # This method works on ALL versions of the library
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'bn', 'hi', 'en-US', 'en-GB'])
            
            # If we get here, we found one!
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_list)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.warning("If the error says 'TranscriptsDisabled', this video has no captions.")
            transcript_text = None

        # 2. SEND TO AI
        if transcript_text:
            with st.spinner("🧠 Analyzing..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""
                    Summarize this video.
                    1. **Summary**: 3-5 sentences.
                    2. **Key Points**: Bullet points.
                    
                    TRANSCRIPT:
                    {transcript_text}
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Error: {str(e)}")
