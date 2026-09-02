🧠 VoiceVault
AI-Powered Voice Intelligence, Transcription, Evaluation & Content Management Platform
VoiceVault is an AI-powered voice processing application designed to transform audio and video content into useful, searchable, and structured information.
The application supports audio/video uploads as well as online media sources such as YouTube. It can extract audio, transcribe speech using multiple AI speech-recognition models, compare transcription quality using objective evaluation metrics, and organize the resulting content into summaries, key points, action items, and keywords.
VoiceVault also provides organizational content publishing and deletion-confirmation functionality through a local SQLite database.
📌 Project Overview
VoiceVault combines multiple AI and data-processing technologies into a single application.
Audio / Video / Online Media
            │
            ▼
      Media Detection
            │
            ▼
      Audio Extraction
            │
            ▼
    Audio Preprocessing
            │
            ▼
   Speech Recognition Models
            │
      ┌─────┼─────────────┐
      ▼     ▼             ▼
   Whisper Faster-Whisper Wav2Vec2
      │     │             │
      └─────┼─────────────┘
            ▼
       Transcriptions
            │
            ▼
     Quality Evaluation
            │
     ┌──────┼─────────┐
     ▼      ▼         ▼
    BLEU    WER       CER
            │
            ▼
     Content Extraction
            │
      ┌─────┼──────────────┐
      ▼     ▼              ▼
    Title Summary     Key Points
      │     │              │
      └─────┼──────────────┘
            ▼
      Action Items
            │
            ▼
        Keywords
            │
            ▼
    Published Content
            │
            ▼
       SQLite Database
✨ Key Features
Feature	Description
Audio Processing	Upload, validate, inspect, and standardize supported audio files.
Video Processing	Extract audio from uploaded video using FFmpeg.
Online Media	Detect and process YouTube and compatible direct media URLs.
Media Metadata	Retrieve title, description, duration, uploader, channel, thumbnail, language, view count, categories, tags and stream availability.
Speech Recognition	Transcribe audio with Whisper, Faster-Whisper and Wav2Vec2.
Fast Transcription	Use Faster-Whisper alone for quicker transcription.
Model Comparison	Run multiple ASR architectures and compare their outputs.
Evaluation	Calculate BLEU, WER and CER against reference text.
Content Extraction	Generate title, summary, key points, action items and keywords.
Publishing	Store extracted organizational content in SQLite.
Deletion Confirmation	Require all registered organization members to confirm before permanent deletion.
Streamlit UI	Provide an interactive application interface.
🎙️ Audio Processing
•	Upload audio files directly.
•	Supported formats: WAV, MP3, M4A, FLAC and OGG.
•	Extract duration, sample rate, channel count and file name.
•	Convert uploaded audio into a standardized WAV format.
•	Standardize audio to 16 kHz, mono WAV.
🎬 Video Processing
VoiceVault can process video files by extracting their audio track.
The extracted audio is converted to 16 kHz, mono, PCM WAV, a format suitable for local speech-recognition models.
🌐 Online Media Processing
VoiceVault uses yt-dlp for online media processing.
•	YouTube
•	Direct media URLs
•	Other compatible online media sources
Source categories:
YouTube
Google Meet
Direct Media
Unknown
For YouTube processing, the implementation supports modern JavaScript challenge handling through Deno and yt-dlp EJS components.
Retrieved metadata can include:
•	Title
•	Description
•	Duration
•	Uploader
•	Channel
•	Channel ID
•	Upload date
•	Thumbnail
•	Language
•	View count
•	Categories
•	Tags
•	Audio availability
•	Video availability
A normal Google Meet URL is treated as a meeting page rather than a directly downloadable recording URL; the application asks for an accessible recording URL or an uploaded recording.
🗣️ Speech Recognition
1. OpenAI Whisper
Whisper is used as the baseline automatic speech-recognition model.
Architecture: Transformer Encoder-Decoder
The implementation supports different Whisper model sizes, including Whisper (base).
2. Faster-Whisper
Faster-Whisper provides a speed-optimized implementation of Whisper using CTranslate2.
Architecture: Whisper + CTranslate2
Device: CPU
Compute type: int8
Faster-Whisper is also used by the fast transcription option.
3. Wav2Vec2
Wav2Vec2 provides an independent speech-recognition architecture for comparison.
Model: facebook/wav2vec2-base-960h
Architecture: CTC-based Speech Recognition
The model is loaded through the Hugging Face Transformers pipeline.
🔬 Model Comparison
1. OpenAI Whisper
2. Faster-Whisper
3. Wav2Vec2
Each model produces transcription, architecture information, detected language, processing time, success/failure status, and error information when applicable.
Loaded models are cached during the application session to reduce repeated model-loading overhead.
⚡ Fast Transcription
Fast mode uses Faster-Whisper (base) only, allowing users to obtain a transcript without running every model.
📊 Transcription Evaluation
BLEU
BLEU measures similarity between a reference transcription and generated transcription. Higher values indicate greater similarity to the reference.
WER — Word Error Rate
WER measures transcription errors at the word level.
WER =
(Substitutions + Deletions + Insertions)
/
Number of Reference Words
The implementation calculates WER using edit distance. Lower WER indicates better transcription quality.
CER — Character Error Rate
CER evaluates transcription accuracy at the character level.
CER =
Character Edit Distance
/
Number of Reference Characters
CER is reported as a percentage. Lower CER indicates better transcription quality.
📈 Evaluation Workflow
Reference Transcription
          │
          ▼
    Normalize Text
          │
          ▼
   Model Transcription
          │
          ▼
      ┌───┼────┐
      ▼   ▼    ▼
    BLEU WER  CER
      │   │    │
      └───┼────┘
          ▼
   Evaluation Results
•	Convert text to lowercase.
•	Remove punctuation.
•	Normalize whitespace.
•	Compare normalized reference and generated text.
🧠 Content Extraction
The content extraction module organizes transcription into useful information:
Title
Summary
Key Points
Action Items
Keywords
Title
Generated from the first few words of the transcription.
Summary
Generated from the initial sentences of the transcription.
Key Points
The first several meaningful sentences are extracted as key points.
Action Items
Sentences containing action-oriented keywords are identified.
need to
should
must
please
complete
finish
submit
review
prepare
schedule
send
update
create
Keywords
Frequently occurring meaningful words are extracted after removing common stop words. The most frequent keywords are returned.
🗄️ SQLite Database
VoiceVault includes a local SQLite database for managing published organizational content.
data/VoiceVault.db
published_content
Stores published organizational content.
id
title
summary
key_points
action_items
keywords
original_transcription
created_at
published_by
status
organization_members
Stores organization members.
id
name
Member names are unique.
deletion_confirmations
Stores confirmation records when organization members approve deletion of published content.
id
content_id
member_name
confirmed_at
The database prevents duplicate confirmation records for the same content and member.
🔐 Collaborative Deletion System
Content is not permanently deleted until every registered organization member has confirmed the deletion.
Published Content
       │
       ▼
Deletion Requested
       │
       ▼
Members Confirm
       │
       ▼
All Members Confirmed?
       │
    ┌──┴──┐
    │     │
   No    Yes
    │     │
    ▼     ▼
Remain   Delete
Published Content
This provides an additional organizational approval layer before permanent deletion.
🏗️ Project Architecture
VoiceVault/
│
├── app.py
│
├── data/
│   ├── evaluation_dataset.csv
│   ├── evaluation_results.csv
│   └── VoiceVault.db
│
├── src/
│   ├── __init__.py
│   ├── audio_processor.py
│   ├── content_extractor.py
│   ├── database.py
│   ├── media_downloader.py
│   ├── metrics.py
│   └── speech_models.py
│
├── requirements.txt
├── README.md
└── .gitignore
📂 Module Description
File	Purpose
app.py	Main Streamlit application
audio_processor.py	Audio validation, conversion, metadata extraction and temporary file handling
content_extractor.py	Extracts titles, summaries, key points, action items and keywords
database.py	SQLite database management and organizational content operations
media_downloader.py	Online media detection, metadata retrieval, downloading and audio extraction
metrics.py	BLEU, WER and CER transcription evaluation
speech_models.py	Whisper, Faster-Whisper and Wav2Vec2 transcription
evaluation_dataset.csv	Reference evaluation dataset
evaluation_results.csv	Stored transcription evaluation results
requirements.txt	Python dependencies
README.md	Project documentation
🛠️ Technologies Used
Technology	Purpose
Python	Core programming language
Streamlit	Interactive web application
OpenAI Whisper	Baseline speech recognition
Faster-Whisper	Optimized speech recognition
Wav2Vec2	Independent CTC-based speech recognition
Hugging Face Transformers	Wav2Vec2 model pipeline
PyTorch	Deep learning framework
TorchAudio	Audio/deep-learning support
Librosa	Audio processing
SoundFile	WAV/audio file handling
yt-dlp	Online media downloading
FFmpeg	Audio/video conversion
Deno	JavaScript runtime for modern YouTube processing
Pandas	Dataset processing
Scikit-learn	Machine-learning utilities
SacreBLEU	BLEU evaluation
jiwer	Speech-recognition evaluation dependency
ROUGE Score	Text evaluation support
BERTScore	Semantic text evaluation support
SQLite	Local database
📦 Python Requirements
streamlit
pandas
librosa
openai-whisper
faster-whisper
transformers
torch
torchaudio
sacrebleu
nltk
scikit-learn
yt-dlp
rouge-score
jiwer
bert-score
FFmpeg is also required for audio/video conversion. Deno is required for the current YouTube processing implementation.
🚀 Installation
1. Clone the Repository
git clone https://github.com/manojjairam/VoiceVault.git
2. Open the Project Folder
cd VoiceVault
3. Create a Virtual Environment
py -3.12 -m venv .venv
4. Activate the Virtual Environment
.\.venv\Scripts\Activate.ps1
5. Upgrade pip
python -m pip install --upgrade pip
6. Install Dependencies
pip install -r requirements.txt
🎬 FFmpeg Setup
FFmpeg is required for audio extraction, video-to-audio conversion, WAV conversion and online media processing.
ffmpeg -version
The application checks FFmpeg availability before processing online media.
🦕 Deno Setup
The current YouTube processing implementation uses Deno for modern JavaScript challenge handling.
deno --version
If Deno is unavailable, YouTube processing displays an appropriate error message.
▶️ Running the Application
streamlit run app.py
The Streamlit application will start locally and open in the browser.
🎯 Complete Application Workflow
                START
                  │
                  ▼
       Select Input Source
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Audio     Video     Online URL
        │         │         │
        │         ▼         ▼
        │    Extract Audio  Download
        │         │         │
        └─────────┼─────────┘
                  ▼
          Validate Audio
                  │
                  ▼
        Convert / Normalize
                  │
                  ▼
        Select ASR Models
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     Whisper Faster-W   Wav2Vec2
        │         │         │
        └─────────┼─────────┘
                  ▼
           Transcriptions
                  │
                  ▼
         Compare Transcripts
                  │
                  ▼
          BLEU / WER / CER
                  │
                  ▼
        Extract Useful Content
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Title    Summary   Key Points
                  │
                  ▼
            Action Items
                  │
                  ▼
              Keywords
                  │
                  ▼
         Publish if Required
                  │
                  ▼
           SQLite Database
🔍 Input Sources
Local Audio
Users can upload supported audio files directly: WAV, MP3, M4A, FLAC and OGG.
Local Video
Video files can be processed by extracting their audio track using FFmpeg.
Online Media
Users can provide supported online media URLs. The application detects YouTube, Google Meet, Direct Media and Unknown Source.
📋 Media Metadata
•	Title
•	Description
•	Duration
•	Uploader
•	Channel
•	Channel ID
•	Upload Date
•	Thumbnail
•	Language
•	View Count
•	Categories
•	Tags
•	Audio Availability
•	Video Availability
🧪 Error Handling
•	Unsupported audio formats
•	Missing FFmpeg
•	Missing Deno
•	Invalid URLs
•	Empty audio files
•	Failed media downloads
•	Restricted/private media
•	Failed audio conversion
•	Missing model dependencies
•	Model loading failures
•	Transcription failures
•	Database integrity errors
Processing modules return structured success/error information.
💾 Temporary File Handling
Uploaded and downloaded media files are handled using temporary directories/files where appropriate.
Online media downloads use temporary directories with the VoiceVault-specific prefix:
voicevault_media_
Failed downloads are cleaned up automatically.
🔄 Model Caching
VoiceVault caches loaded speech-recognition models in memory.
Whisper
Faster-Whisper
Wav2Vec2
This reduces repeated model-loading overhead during the same application session.
📊 Evaluation Dataset
The repository contains:
data/evaluation_dataset.csv
Evaluation results are stored in:
data/evaluation_results.csv
The evaluation system compares multiple transcription outputs against a reference transcription.
📈 Evaluation Metrics
Metric	Purpose	Better Result
BLEU	Measures similarity with reference text	Higher
WER	Measures word-level transcription errors	Lower
CER	Measures character-level transcription errors	Lower
🔬 Example Model Comparison
from src.speech_models import transcribe_standard_comparison

results = transcribe_standard_comparison(
    "audio.wav"
)
This executes Whisper, Faster-Whisper and Wav2Vec2.
⚡ Example Fast Transcription
from src.speech_models import transcribe_fast

results = transcribe_fast(
    "audio.wav"
)
The fast mode uses Faster-Whisper.
🧮 Example Evaluation
from src.metrics import evaluate_transcription

result = evaluate_transcription(
    reference_text,
    generated_text
)

print(result)
The result contains BLEU Score, WER and CER.
📝 Example Content Extraction
from src.content_extractor import extract_content

content = extract_content(
    transcription
)

print(content)
The returned dictionary contains title, summary, key_points, action_items and keywords.
🗃️ Example Database Initialization
from src.database import initialize_database

initialize_database()
This creates the required SQLite tables if they do not already exist.
🧑‍🤝‍🧑 Organization Members
from src.database import add_member

add_member("Member Name")
Members can be retrieved using:
from src.database import get_members

members = get_members()
📢 Publishing Content
Extracted content can be stored as published organizational content. The database stores title, summary, key points, action items, keywords, original transcription, created time, publisher and status.
🗑️ Deletion Confirmation
Before permanent deletion, every organization member must confirm.
from src.database import confirm_deletion

confirm_deletion(
    content_id,
    member_name
)
The system checks whether all registered members have confirmed:
from src.database import can_delete_content

can_delete_content(
    content_id
)
Only when the result is True should the content be deleted.
🔒 Data Considerations
VoiceVault currently uses a local SQLite database:
data/VoiceVault.db
The database contains published content, transcriptions and organization-member information.
For production deployments, additional security controls should be considered:
•	Authentication
•	Authorization
•	Encryption
•	Secure database hosting
•	Access logging
•	Backup policies
•	Data retention policies
•	Secure secret management
⚠️ Current Limitations
Speech Recognition
•	Wav2Vec2 currently uses an English-specific model.
•	Recognition accuracy depends on audio quality.
•	Background noise can affect transcription quality.
•	Different models may produce different results for the same recording.
Online Media
•	Some media may be private or restricted.
•	Authentication may be required for protected content.
•	YouTube processing requires Deno in the current implementation.
•	Online availability can change independently of VoiceVault.
Content Extraction
The current content extraction system uses rule-based processing. It does not currently use a large language model to generate summaries or semantic action-item extraction.
Database
The application currently uses a local SQLite database rather than a centralized production database.
🔮 Future Enhancements
•	LLM-powered summarization
•	Automatic topic extraction
•	Topic classification
•	Topic drift detection
•	Speaker diarization
•	Speaker identification
•	Timestamped transcripts
•	Word-level timestamps
•	Multilingual transcription improvements
•	Larger speech evaluation datasets
•	Additional ASR models
•	GPU acceleration
•	Cloud storage
•	Production database integration
•	User authentication
•	Role-based access control
•	Audit logging
•	Advanced search
•	Semantic search
•	Vector database integration
•	Voice analytics dashboards
•	Emotion and sentiment analysis
•	Automatic meeting minutes
•	Calendar/task integration
•	API support
•	REST API deployment
•	Docker deployment
•	Cloud deployment
🧩 Design Philosophy
VoiceVault is designed as a modular system.
Audio Processing
        │
        ▼
Media Processing
        │
        ▼
Speech Recognition
        │
        ▼
Evaluation
        │
        ▼
Content Extraction
        │
        ▼
Database Management
•	Test individual components
•	Replace speech models
•	Add new evaluation metrics
•	Add additional media sources
•	Extend database functionality
•	Introduce new AI capabilities
📁 Git Repository
https://github.com/manojjairam/VoiceVault.git
Clone using:
git clone https://github.com/manojjairam/VoiceVault.git
🧑‍💻 Development
Check repository status
git status
Add changes
git add .
Commit changes
git commit -m "Update VoiceVault"
Push changes
git push origin main
📜 License
Add the project's preferred open-source license here if the repository is intended for public distribution.
👨‍💻 Author
Manoj Jairam
VoiceVault is developed as an AI/NLP project combining speech recognition, transcription evaluation, media processing, content extraction and organizational content management.
⭐ Project Summary
VoiceVault brings together speech recognition, media processing, transcription evaluation and content management into one platform.
INPUT
  │
  ├── Audio
  ├── Video
  └── Online Media
        │
        ▼
MEDIA PROCESSING
        │
        ▼
AUDIO EXTRACTION
        │
        ▼
SPEECH RECOGNITION
        │
        ├── Whisper
        ├── Faster-Whisper
        └── Wav2Vec2
        │
        ▼
TRANSCRIPTION
        │
        ▼
QUALITY EVALUATION
        │
        ├── BLEU
        ├── WER
        └── CER
        │
        ▼
CONTENT EXTRACTION
        │
        ├── Title
        ├── Summary
        ├── Key Points
        ├── Action Items
        └── Keywords
        │
        ▼
CONTENT MANAGEMENT
        │
        ├── Publish
        ├── Organization Members
        ├── Deletion Confirmation
        └── SQLite Storage
        │
        ▼
VOICEVAULT
VoiceVault demonstrates how modern speech-recognition and AI technologies can be combined with traditional software engineering and data-management techniques to create a complete voice-intelligence application.
