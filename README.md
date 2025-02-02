
# Speaker Count AI

## Demo

!<img
  src="image.png"
  alt="Alt text"
  title="Optional title"
  style="display: inline-block; margin: 0 auto; max-width: 300px">


## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)


## Overview

The Speaker Count Web Application is an Artificial Intelligence tool that performs speaker diarization on audio files and provides a web interface for users to upload audio files or YouTube URLs to determine the number of unique speakers in the audio. It uses advanced audio processing techniques to analyze and count speakers, making it useful for a variety of applications such as transcription services, content analysis, and more.

## Features

- Upload audio files or provide YouTube URLs for analysis.
- Accurate speaker diarization to count the number of unique speakers.
- User-friendly web interface.
- Support for a wide range of audio formats.
- Real-time or batch processing options.





## Getting Started

### Prerequisites

Before running the application, make sure you have the following prerequisites installed:

- Python 3.x
- Dependencies (specified in `requirements.txt`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/speaker-count-web-app.git
   cd speaker-count-web-app
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the web application:

go to 'src' folder
   ```bash
   streamlit run app.py
   ```

2. Access the web application by opening a web browser and navigating to `http://localhost:8501`.

3. Upload an audio file or provide a YouTube URL for speaker diarization.

4. The application will process the audio and display the number of unique speakers.

## Technologies Used

- Python
- Streamlit / CSS styling
- Speaker Diarization pre_trained models



## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test them.
4. Create a pull request with a clear description of your changes.
