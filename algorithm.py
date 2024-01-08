import os
import streamlit as st
from numpy.linalg import LinAlgError
#from diarizer import Diarizer

from simple_diarizer.diarizer import Diarizer
from simple_diarizer.utils import (check_wav_16khz_mono, convert_wavfile,
                                   waveplot, combined_waveplot, waveplot_perspeaker)

from pytube import YouTube


import os
import tempfile
from pprint import pprint

import matplotlib.pyplot as plt
import soundfile as sf

from IPython.display import Audio, display, HTML
from tqdm.autonotebook import tqdm


def download_youtube_audio(youtube_url):
    yt = YouTube(youtube_url)
    video = yt.streams.filter(only_audio=True).first()

    # Downloading the file
    out_file = video.download(output_path="")

    # Save the file as .wav
    base, ext = os.path.splitext(out_file)
    new_file = base + '.wav'
    os.rename(out_file, new_file)
    print("Downloaded and converted to", new_file)
    return new_file



# Function to count the number of speakers in a .wav file
def count_speakers(wav_file):
    embed_model = 'xvec'
    diar = Diarizer(
        embed_model=embed_model,
        cluster_method='sc',
        window=1.5,
        period=0.75
    )

    try:
        print(wav_file)
        segments = diar.diarize(wav_file, threshold=0.1, num_speakers=None)
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

# Function to style the app with custom CSS
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize the app with a title and a brief description
st.title('Speaker Count Application')
st.markdown("""
    This application uses **speaker diarization** technology to analyze audio and determine the number of distinct speakers. 
    Speaker diarization is the process of partitioning an audio stream into homogeneous segments according to the speaker identity. 
    It enables the identification of who spoke when in a multi-speaker environment. Simply input a YouTube URL or upload an audio file, 
    and the app will process it to display the number of speakers.
""")

# Sidebar for aesthetic settings (optional)
with st.sidebar:
    st.header('Settings')
    theme_color = st.color_picker('Choose a Theme Color')

# Input section for YouTube URL and audio file upload
youtube_url = st.text_input('Enter a YouTube URL')
uploaded_file = st.file_uploader("Or upload an audio file", type=['wav', 'mp3', 'ogg', 'flac', 'aac'])

# Displaying results
if youtube_url or uploaded_file:
    if uploaded_file is not None:
        # Save uploaded file to temporary file
        temp_file = f"temp_{uploaded_file.name}"
        with open(temp_file, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Process audio file
        speakers_count = count_speakers(temp_file)
        if speakers_count is not None:
            st.success(f'Number of Speakers Detected: {speakers_count}')

        # Clean up temporary file
        os.remove(temp_file)
    else:
        wav_file = download_youtube_audio(youtube_url)

        # Define the original file path
        original_path = wav_file

        # Define the new file name
        new_file_name = "youtube.wav"

        # Split the original path into directory and file name
        dir_path, old_file_name = os.path.split(original_path)

        # Create the new file path
        new_path = os.path.join(dir_path, new_file_name)

        # Rename the file
        os.rename(original_path, new_path)

        print(f'Renamed "{old_file_name}" to "{new_file_name}"')


        new_file_name_without_extension = new_file_name.rstrip('.wav')
        output_wav_file = new_file_name_without_extension + "_converted.wav"
        input_wav_file = new_file_name

        wav_file = convert_wavfile(input_wav_file,output_wav_file)

        print("ZZ")
        print(wav_file)
        speakers_count = count_speakers(wav_file)
        if speakers_count is not None:
            st.success(f'Number of Speakers Detected: {speakers_count}')
        os.remove(wav_file)  # Clean up downloaded file

        # Handle YouTube URL (implementation not shown)
        pass

# Use the local CSS file for additional styling
local_css("style.css")  # Make sure to create a style.css file with your desired styles
