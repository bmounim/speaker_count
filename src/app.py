import os
import tempfile
import logging
from numpy.linalg import LinAlgError
from yt_dlp import YoutubeDL
import soundfile as sf
from simple_diarizer.diarizer import Diarizer
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)

# Download and convert a YouTube video to a .wav audio file using yt_dlp
def download_youtube_audio(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
            # Add headers to mimic a browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Referer': 'https://www.youtube.com/'
            },
            # Add additional parameters to bypass restrictions
            'ignoreerrors': True,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)

            # Check if download was successful
            if not info_dict or 'requested_downloads' not in info_dict:
                st.error("Failed to download video. It might be restricted or unavailable.")
                return None

            # Extract file path
            file_path = ydl.prepare_filename(info_dict).replace('.webm', '.wav').replace('.m4a', '.wav')

            return file_path

    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        st.error(f"An error occurred: {e}")
        return None


# Count the number of speakers in a .wav file
def count_speakers(wav_file):
    diarizer = Diarizer(embed_model='xvec', cluster_method='sc', window=1.5, period=0.75)
    try:
        segments = diarizer.diarize(wav_file, threshold=0.1, num_speakers=None)
        unique_labels = {entry['label'] for entry in segments}
        return len(unique_labels)
    except LinAlgError:
        st.error("Linear algebra error during speaker diarization.")
        return 0
    except AssertionError as error:
        if "Couldn't find any speech during VAD" in str(error):
            st.error("No speech detected in the audio file.")
            return 0
        else:
            logging.error(f"Assertion error: {error}")
            raise
    except Exception as error:
        logging.error(f"Unexpected error: {error}")
        st.error(f"An unexpected error occurred: {error}")
        return None

# Validate uploaded audio file
def is_valid_audio(file):
    try:
        sf.read(file)
        return True
    except Exception:
        return False

# Apply custom CSS to the Streamlit app
def local_css(file_name, theme_color):
    try:
        with open(file_name, "r") as f:
            css = f.read().replace("{{theme_color}}", theme_color)
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        logging.warning("CSS file not found, skipping custom styles.")

# Streamlit Web App
def main():
    st.title('Speaker Count Application')
    st.markdown("This app counts the number of speakers in an audio file.")

    # Sidebar settings
    with st.sidebar:
        st.header('Settings')
        theme_color = st.color_picker('Choose a Theme Color')

    # Input for YouTube URL and audio file upload
    youtube_url = st.text_input('Enter a YouTube URL')
    uploaded_file = st.file_uploader("Or upload an audio file", type=['wav', 'mp3', 'ogg', 'flac', 'aac'])

    # Processing uploaded file or YouTube URL
    if youtube_url or uploaded_file:
        with st.spinner("Processing..."):
            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_file_path = temp_file.name
                if is_valid_audio(temp_file_path):
                    speakers_count = count_speakers(temp_file_path)
                    if speakers_count is not None:
                        st.success(f'Number of Speakers Detected: {speakers_count}')
                else:
                    st.error("Invalid audio file.")
                os.unlink(temp_file_path)
            else:
                wav_file = download_youtube_audio(youtube_url)
                if wav_file:
                    speakers_count = count_speakers(wav_file)
                    if speakers_count is not None:
                        st.success(f'Number of Speakers Detected: {speakers_count}')
                    os.remove(wav_file)

    local_css("static/style.css", theme_color)

if __name__ == "__main__":
    main()
