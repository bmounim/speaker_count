import os
import tempfile
from numpy.linalg import LinAlgError
from pytube import YouTube
import soundfile as sf
from simple_diarizer.diarizer import Diarizer

import streamlit as st  # For building the web app

# Download and convert a YouTube video to a .wav audio file
def download_youtube_audio(youtube_url):
    yt = YouTube(youtube_url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path="")
    base, ext = os.path.splitext(out_file)
    new_file = base + '.wav'
    os.rename(out_file, new_file)
    print("Downloaded and converted to", new_file)
    return new_file

# Count the number of speakers in a .wav file
def count_speakers(wav_file):
    embed_model = 'xvec'
    diarizer = Diarizer(embed_model=embed_model, cluster_method='sc', window=1.5, period=0.75)
    try:
        segments = diarizer.diarize(wav_file, threshold=0.1, num_speakers=None)
        unique_labels = {entry['label'] for entry in segments}
        return len(unique_labels)
    except LinAlgError:
        return 0
    except AssertionError as error:
        if "Couldn't find any speech during VAD" in str(error):
            return 0
        else:
            raise
    except Exception as error:
        st.error(f"Unexpected error encountered: {error}")
        return None

# Apply custom CSS to the Streamlit app
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Streamlit Web App
def main():
    st.title('Speaker Count Application')
    st.markdown("""...""")  # Brief description of the app

    # Sidebar settings
    with st.sidebar:
        st.header('Settings')
        theme_color = st.color_picker('Choose a Theme Color')

    # Input for YouTube URL and audio file upload
    youtube_url = st.text_input('Enter a YouTube URL')
    uploaded_file = st.file_uploader("Or upload an audio file", type=['wav', 'mp3', 'ogg', 'flac', 'aac'])

    # Processing uploaded file or YouTube URL
    if youtube_url or uploaded_file:
        if uploaded_file is not None:
            temp_file = f"temp_{uploaded_file.name}"
            with open(temp_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            speakers_count = count_speakers(temp_file)
            if speakers_count is not None:
                st.success(f'Number of Speakers Detected: {speakers_count}')
            os.remove(temp_file)
        else:
            wav_file = download_youtube_audio(youtube_url)
            speakers_count = count_speakers(wav_file)
            if speakers_count is not None:
                st.success(f'Number of Speakers Detected: {speakers_count}')
            os.remove(wav_file)

    local_css("static/style.css")

if __name__ == "__main__":
    main()
