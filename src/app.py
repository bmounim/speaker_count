import os
import tempfile
import logging
import subprocess
import numpy as np
from numpy.linalg import LinAlgError
from yt_dlp import YoutubeDL
import soundfile as sf
import torchaudio
from simple_diarizer.diarizer import Diarizer
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)

# Download and convert a YouTube video to a .wav audio file using yt-dlp
def download_youtube_audio(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',  # Save file with the video title as the name
            'quiet': True,  # Suppress yt-dlp output
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            'retries': 10,
            'fragment_retries': 10,
            'ignoreerrors': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['hls', 'dash', 'translated_subs']
                }
            }
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            audio_file = ydl.prepare_filename(info_dict)
            base, _ = os.path.splitext(audio_file)
            new_file = base + '.wav'
            if os.path.exists(new_file) and os.path.getsize(new_file) > 0:
                st.success(f"Downloaded and converted to {new_file}")
                return new_file
            else:
                st.error("Failed to convert the video to a valid WAV file.")
                return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"Download error: {e}")
        return None

# Convert audio to 16kHz mono WAV format using FFmpeg
def convert_to_mono_wav(input_path, output_path):
    try:
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-i', input_path,
            '-acodec', 'pcm_s16le',  # 16-bit PCM codec
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',  # Mono channel
            output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"FFmpeg conversion failed: {e}")
        logging.error(f"FFmpeg error: {e}")
        return False

# Count the number of speakers in a .wav file
def count_speakers(wav_file):
    try:
        # Convert to compatible format first
        converted_file = "converted_audio.wav"
        if not convert_to_mono_wav(wav_file, converted_file):
            return None

        # Initialize diarizer
        diarizer = Diarizer(
            embed_model='xvec',
            cluster_method='sc',
            window=1.5,
            period=0.75,
        )

        # Perform diarization
        segments = diarizer.diarize(converted_file, threshold=0.1, num_speakers=None)
        unique_labels = {entry['label'] for entry in segments}

        # Clean up temporary file
        os.remove(converted_file)

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
        info = sf.info(file)
        if info.samplerate < 16000 or info.channels > 2:
            st.warning("Audio file should be mono or stereo with a sample rate of at least 16kHz.")
            return False
        return True
    except Exception as e:
        st.error(f"Invalid audio file: {e}")
        return False

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
            try:
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
            except Exception as e:
                st.error(f"""
                Processing failed: {str(e)}
                Common solutions:
                1. Try a different YouTube video
                2. Check audio file format (WAV/PCM preferred)
                3. Shorten the audio duration (<10 minutes)
                """)
                logging.exception("Processing error:")

if __name__ == "__main__":
    main()