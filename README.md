# 🧠 VoiceVault

> **AI-Powered Voice Intelligence, Transcription, Evaluation & Content Management Platform**

VoiceVault is an AI-powered voice processing application designed to transform audio, video, and online media into useful, structured information.

The application can:

- Upload and validate audio files
- Process uploaded videos by extracting their audio
- Retrieve and process supported online media such as YouTube
- Convert media into speech-recognition-ready audio
- Transcribe speech using multiple AI/ML speech-recognition models
- Compare transcription quality using BLEU, WER, and CER
- Extract titles, summaries, key points, action items, and keywords
- Publish extracted organizational content
- Store published content and organization members in SQLite
- Implement member-based deletion confirmation
- Provide a Streamlit interface for the complete workflow

---

## 📌 Project Overview

VoiceVault combines media processing, automatic speech recognition, transcription evaluation, content extraction, and lightweight content management in one application.

### End-to-End Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                 AUDIO / VIDEO / ONLINE URL                  │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Media Detection   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Audio Extraction   │
                    │    / Conversion     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Audio Preprocessing │
                    │    16 kHz / Mono    │
                    └──────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────────┐
                 │    Speech Recognition      │
                 └────────────┬───────────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        ┌─────────┐     ┌──────────────┐   ┌──────────┐
        │ Whisper │     │Faster-Whisper│   │ Wav2Vec2 │
        └────┬────┘     └──────┬───────┘   └────┬─────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               ▼
                       ┌──────────────┐
                       │ Transcripts  │
                       └──────┬───────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Quality Evaluation │
                    └─────────┬──────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  BLEU       WER        CER
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                    ┌────────────────────┐
                    │ Content Extraction │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
           Summary        Key Points       Action Items
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                         Keywords
                              │
                              ▼
                    ┌────────────────────┐
                    │ Published Content  │
                    └─────────┬──────────┘
                              ▼
                     ┌────────────────┐
                     │ SQLite Database │
                     └────────────────┘
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎙️ Audio Processing | Upload, validate, inspect, and standardize audio |
| 🎬 Video Processing | Extract audio from uploaded video using FFmpeg |
| 🌐 Online Media | Detect and process supported online media URLs |
| ▶️ YouTube Support | Retrieve metadata and download audio with yt-dlp |
| 🔊 Audio Standardization | Convert speech input to 16 kHz mono WAV |
| 🤖 Multi-Model ASR | Compare Whisper, Faster-Whisper, and Wav2Vec2 |
| ⚡ Fast Transcription | Faster-Whisper-only path for quick transcription |
| 📊 Evaluation | Calculate BLEU, WER, and CER |
| 📝 Content Extraction | Generate title, summary, key points, action items, and keywords |
| 🗄️ SQLite Storage | Store published organizational content locally |
| 👥 Organization Members | Maintain organization member records |
| ✅ Deletion Confirmation | Require member confirmations before deletion |
| 🖥️ Streamlit UI | Interactive browser-based interface |
| 📥 Content Workflow | Media → transcript → structured content → publication |

---

## 🔄 Application Workflow

### 1. Input

VoiceVault supports:

- Uploaded audio
- Uploaded video
- Supported online media URLs
- YouTube URLs

### 2. Media Detection

The application identifies the input type before processing.

Supported URL categories include:

- YouTube
- Google Meet
- Direct media
- Unknown

A normal Google Meet meeting URL is not treated as a downloadable recording URL. The user must provide an accessible recording URL or upload the recording.

### 3. Audio Extraction

For video input, FFmpeg extracts the audio.

The speech-recognition audio is standardized to:

```text
Sample Rate : 16,000 Hz
Channels    : Mono
Format      : PCM WAV
```

### 4. Speech Recognition

The processed audio can be sent to one or more ASR models:

```text
Audio
  │
  ├──► Whisper
  ├──► Faster-Whisper
  └──► Wav2Vec2
```

### 5. Evaluation

When a reference transcription is available, the generated transcription can be evaluated using:

- BLEU
- Word Error Rate (WER)
- Character Error Rate (CER)

### 6. Content Extraction

The transcription is converted into:

```text
Transcription
     │
     ├──► Title
     ├──► Summary
     ├──► Key Points
     ├──► Action Items
     └──► Keywords
```

### 7. Publishing

Extracted information can be stored as organizational content.

Published records contain:

- Title
- Summary
- Key points
- Action items
- Keywords
- Original transcription
- Creation timestamp
- Publisher
- Status

### 8. Deletion Confirmation

Published content can be permanently deleted only after all registered organization members have confirmed deletion.

---

## 🤖 Speech Recognition Models

VoiceVault currently implements three speech-recognition architectures.

### 1. OpenAI Whisper

| Property | Value |
|---|---|
| Architecture | Transformer Encoder-Decoder |
| Purpose | Baseline ASR model |
| Configuration | Configurable model size |

Whisper is retained as the baseline model for comparative evaluation.

Example:

```python
transcribe_whisper(audio_path, model_size="base")
```

### 2. Faster-Whisper

| Property | Value |
|---|---|
| Architecture | Whisper + CTranslate2 |
| Purpose | Speed-optimized Whisper transcription |
| Device | CPU |
| Compute Type | INT8 |
| Beam Size | 1 |
| VAD Filtering | Enabled |

Example:

```python
transcribe_faster_whisper(
    audio_path,
    model_size="base"
)
```

The fast transcription path uses Faster-Whisper only.

### 3. Wav2Vec2

| Property | Value |
|---|---|
| Architecture | CTC-based Speech Recognition |
| Model | `facebook/wav2vec2-base-960h` |
| Purpose | Independent ASR architecture for comparison |

Wav2Vec2 provides an independent CTC-based architecture for academic comparison. The configured model is primarily intended for English speech recognition.

---

## 📊 Model Comparison

### Standard Comparison

The standard comparison runs:

```text
1. Whisper
2. Faster-Whisper
3. Wav2Vec2
```

using the base model configuration.

```python
transcribe_standard_comparison(audio_path)
```

### Extended Comparison

The extended comparison currently executes the three implemented models:

```text
1. Whisper
2. Faster-Whisper
3. Wav2Vec2
```

The fourth model slot is reserved for future expansion.

```python
transcribe_extended_comparison(audio_path)
```

### Available Models

```python
get_available_models()
```

returns the models available to the application based on installed dependencies.

---

## 📈 Transcription Evaluation

VoiceVault evaluates model output against a reference transcription.

### BLEU

BLEU measures similarity between reference and hypothesis text using SacreBLEU.

```text
Higher BLEU → Greater similarity to the reference
```

### Word Error Rate (WER)

WER measures word-level transcription errors.

```text
WER =
(Substitutions + Deletions + Insertions)
/
Number of Reference Words
```

The application reports WER as a percentage.

```text
Lower WER → Better transcription
```

### Character Error Rate (CER)

CER measures character-level differences.

```text
CER =
Character Edit Distance
/
Number of Reference Characters
```

The application reports CER as a percentage.

```text
Lower CER → Better transcription
```

---

## 🧮 Evaluation Pipeline

```text
Reference Transcription
          │
          ▼
   Text Normalization
          │
          ▼
   Model Transcription
          │
          ▼
   Normalize Hypothesis
          │
          ▼
      Evaluation
          │
     ┌────┼────┐
     ▼    ▼    ▼
   BLEU  WER  CER
```

Text normalization:

- Converts text to lowercase
- Removes punctuation
- Normalizes whitespace
- Compares normalized reference and hypothesis text

---

## 📝 Content Extraction

The `content_extractor.py` module converts a transcription into basic organizational information.

### Title

A title is generated from the first several words of the transcription.

### Summary

For longer transcriptions, the opening sentences are used to create a lightweight summary.

### Key Points

The first several sentences are returned as key points.

### Action Items

Sentences containing action-oriented terms are identified.

Current action-related terms include:

```text
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
```

### Keywords

Keywords are extracted using word-frequency analysis after removing common stop words.

The current implementation returns up to ten keywords.

---

## 🗄️ Database & Content Management

VoiceVault uses SQLite for local content management.

Configured database path:

```text
data/VoiceVault.db
```

The database is initialized through the application.

### Database Schema

#### `published_content`

Stores organizational content.

```text
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
```

#### `organization_members`

Stores organization members.

```text
id
name
```

Member names are unique.

#### `deletion_confirmations`

Stores member deletion confirmations.

```text
id
content_id
member_name
confirmed_at
```

A unique constraint prevents the same member from confirming the same content more than once.

### Database Workflow

```text
Content Extracted
       │
       ▼
Publish Content
       │
       ▼
SQLite: published_content
       │
       ├── Organization Members
       │
       └── Deletion Confirmations
```

---

## 🔐 Deletion Control

VoiceVault implements a collective-confirmation deletion workflow.

```text
Published Content
       │
       ▼
Deletion Requested
       │
       ▼
Organization Members
       │
       ├── Member A ──► Confirmed
       ├── Member B ──► Confirmed
       ├── Member C ──► Confirmed
       └── Member D ──► Confirmed
                       │
                       ▼
              All Members Confirmed
                       │
                       ▼
                Delete Content
```

If there are no organization members, deletion is not permitted by the current implementation.

When deletion succeeds, both the content record and its deletion confirmations are removed.

---

## 🌐 Online Media Processing

VoiceVault uses `yt-dlp` for supported online media processing.

### YouTube Processing

For a YouTube URL, VoiceVault:

1. Detects the URL
2. Checks for Deno
3. Retrieves media metadata
4. Downloads the best available audio
5. Converts the audio to WAV
6. Standardizes it to 16 kHz mono
7. Returns the audio path and media metadata

Metadata can include:

- Title
- Description
- Duration
- Uploader
- Channel
- Channel ID
- Upload date
- Webpage URL
- Thumbnail
- Language
- View count
- Categories
- Tags

### Deno Requirement

The current YouTube integration configures yt-dlp with Deno for modern JavaScript challenge handling.

Verify Deno with:

```powershell
deno --version
```

### Google Meet

A normal Google Meet URL represents a meeting page and cannot be directly treated as a downloadable recording by the current implementation.

Use:

- An accessible recording URL, or
- An uploaded recording

---

## 🎵 Supported Audio Formats

Uploaded audio validation currently accepts:

```text
.wav
.mp3
.m4a
.flac
.ogg
```

---

## 🎬 Recognized Media Extensions

The online-media detection logic recognizes:

```text
.mp3
.wav
.m4a
.aac
.ogg
.flac
.opus
.mp4
.mkv
.webm
.mov
.avi
.flv
.wmv
.m4v
.3gp
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application language |
| Streamlit | Interactive web interface |
| OpenAI Whisper | Baseline speech recognition |
| Faster-Whisper | Efficient Whisper inference |
| Wav2Vec2 | Independent CTC-based ASR comparison |
| Transformers | Wav2Vec2 pipeline |
| PyTorch | Deep-learning model execution |
| Torchaudio | Audio/deep-learning ecosystem |
| Librosa | Audio loading and preprocessing |
| SoundFile | WAV audio writing |
| FFmpeg | Audio extraction and media conversion |
| yt-dlp | Online media retrieval |
| SacreBLEU | BLEU evaluation |
| JiWER | Transcription evaluation dependency |
| ROUGE Score | Text evaluation dependency |
| BERTScore | Semantic text evaluation dependency |
| Scikit-learn | Machine-learning utilities |
| Pandas | Data processing |
| NLTK | NLP dependency |
| SQLite | Local database |

---

## 📁 Project Structure

The current project structure is:

```text
VoiceVault/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── evaluation_dataset.csv
│   └── evaluation_results.csv
│
└── src/
    ├── __init__.py
    ├── audio_processor.py
    ├── content_extractor.py
    ├── database.py
    ├── media_downloader.py
    ├── metrics.py
    └── speech_models.py
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | Main Streamlit application and user interface |
| `audio_processor.py` | Audio validation, inspection, temporary storage, and WAV conversion |
| `content_extractor.py` | Title, summary, key-point, action-item, and keyword extraction |
| `database.py` | SQLite initialization and content/member/deletion management |
| `media_downloader.py` | URL detection, media metadata, downloading, and video-to-audio conversion |
| `metrics.py` | BLEU, WER, CER, and transcription evaluation |
| `speech_models.py` | Whisper, Faster-Whisper, and Wav2Vec2 transcription |

---

## ⚙️ Requirements

### Software

- Python
- pip
- FFmpeg

### Additional Requirement for YouTube

- Deno

### Python Dependencies

The project uses:

```text
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
```

Install them from:

```text
requirements.txt
```

---

## 🚀 Installation

### 1. Clone the Repository

```powershell
git clone https://github.com/manojjairam/VoiceVault.git
```

### 2. Enter the Project Directory

```powershell
cd VoiceVault
```

### 3. Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

### 4. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 6. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 🔧 Verify External Tools

### FFmpeg

FFmpeg is required for video/audio conversion.

```powershell
ffmpeg -version
```

### Deno

Deno is required for the current YouTube processing configuration.

```powershell
deno --version
```

Both commands should be available from the terminal.

---

## ▶️ Run the Application

After activating the virtual environment:

```powershell
streamlit run app.py
```

The application will start locally and Streamlit will provide the browser address.

---

## ⚡ Fast Transcription

For a quick transcript, VoiceVault can use Faster-Whisper only:

```python
from src.speech_models import transcribe_fast

result = transcribe_fast(audio_path)
```

This avoids running the complete three-model comparison.

---

## 🧪 Three-Model Transcription

To run the standard comparison:

```python
from src.speech_models import transcribe_standard_comparison

results = transcribe_standard_comparison(
    audio_path
)
```

Each successful result can contain:

```text
model
architecture
text
language
processing_time
success
```

Failed model executions return an error field.

---

## 🧩 Example Module Usage

### Audio Validation

```python
from src.audio_processor import validate_audio_file

valid, message = validate_audio_file(
    uploaded_file
)
```

### Convert Audio

```python
from src.audio_processor import convert_to_wav

audio_path = convert_to_wav(
    uploaded_file
)
```

### Extract Content

```python
from src.content_extractor import extract_content

content = extract_content(
    transcription
)
```

### Transcribe with Faster-Whisper

```python
from src.speech_models import transcribe_faster_whisper

result = transcribe_faster_whisper(
    audio_path,
    model_size="base"
)
```

### Evaluate Transcription

```python
from src.metrics import evaluate_transcription

metrics = evaluate_transcription(
    reference,
    hypothesis
)
```

### Initialize Database

```python
from src.database import initialize_database

initialize_database()
```

---

## 🧹 Temporary File Processing

Uploaded and downloaded media may be stored temporarily during processing.

Online media downloads use temporary directories.

If an online-media download fails, the temporary directory created for that operation is cleaned up automatically.

---

## 🧯 Error Handling

The application handles common processing failures including:

- Unsupported audio formats
- Invalid URLs
- Missing FFmpeg
- Missing Deno
- Inaccessible media
- Restricted/private online content
- Failed downloads
- Missing downloaded media
- Empty generated audio
- FFmpeg conversion errors
- Model loading failures
- Transcription failures
- Missing reference text

Processing modules return structured success/error information so the Streamlit interface can present useful feedback.

---

## 🔒 Data & Privacy

VoiceVault uses local SQLite storage for its content-management functionality.

The configured database is:

```text
data/VoiceVault.db
```

Temporary files can be created during media processing.

When deploying VoiceVault beyond a local environment, review the data-handling requirements for uploaded recordings, downloaded media, transcripts, and database contents.

Do not process sensitive or confidential recordings through an environment unless its security, access control, storage, and retention policies are appropriate for that data.

---

## ⚠️ Current Limitations

1. Wav2Vec2 currently uses an English-oriented model.
2. YouTube processing depends on Deno, yt-dlp, network connectivity, and media accessibility.
3. Normal Google Meet meeting URLs cannot be downloaded as recordings by the current implementation.
4. Local ASR models can require substantial CPU, RAM, disk space, and model-download time.
5. Current content extraction is lightweight and rule/frequency based rather than LLM-generated summarization.
6. The deletion workflow requires every registered organization member to confirm deletion.
7. The database is local SQLite rather than a centralized production database.
8. The extended comparison currently runs the same three implemented ASR models; a fourth model can be added later.
9. Transcription quality depends on audio quality, language, accent, noise, hardware, and model configuration.

---

## 🔮 Future Enhancements

Potential improvements include:

- Add additional ASR models
- Add multilingual ASR
- Add speaker diarization
- Improve automatic language detection
- Add advanced noise reduction
- Add GPU acceleration
- Add LLM-powered summarization
- Add semantic search
- Add vector database integration
- Add authentication
- Add role-based access control
- Add cloud database support
- Add production-grade audit logging
- Add richer dashboards
- Add model latency benchmarking
- Add larger evaluation datasets
- Add automated evaluation reports
- Add PDF/DOCX export
- Add timestamped transcripts
- Add meeting-specific action-item extraction
- Add topic and entity extraction

---

## 🎯 Use Cases

### 🎓 Education

- Lecture transcription
- Recorded lesson processing
- Study-note generation
- Course-content extraction

### 💼 Business & Meetings

- Meeting transcription
- Meeting summaries
- Action-item identification
- Organizational content publishing

### 🎙️ Interviews

- Interview transcription
- Transcript comparison
- Structured information extraction

### 📺 Online Media

- YouTube audio extraction
- Video-to-text workflows
- Online media transcription

### 🔬 Research

- ASR model comparison
- Speech-recognition benchmarking
- BLEU/WER/CER evaluation

---

## 🧠 Why Multiple ASR Models?

VoiceVault allows different speech-recognition approaches to process the same audio.

```text
                    Same Audio
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Whisper    Faster-Whisper   Wav2Vec2
          │             │             │
          ▼             ▼             ▼
      Transcript    Transcript    Transcript
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 Reference Text
                        │
                        ▼
                 ┌────────────┐
                 │ Evaluation │
                 └─────┬──────┘
                       │
                 ┌─────┼─────┐
                 ▼     ▼     ▼
               BLEU   WER   CER
```

This makes VoiceVault useful as both:

- An end-user transcription application
- An experimental platform for comparing ASR models

---

## 📌 Project Status

VoiceVault currently provides an integrated foundation for:

```text
Media Input
     ↓
Audio Processing
     ↓
Speech Recognition
     ↓
Multi-Model Comparison
     ↓
Transcription Evaluation
     ↓
Content Extraction
     ↓
Organizational Publishing
     ↓
SQLite Storage
```

The architecture is modular so that ASR models, evaluation metrics, media sources, content extraction techniques, and database implementations can be expanded independently.

---

## 👨‍💻 Author

**Manoj Jairam**

VoiceVault combines:

- Speech Recognition
- Natural Language Processing
- Machine Learning
- Audio Processing
- Model Evaluation
- Data Processing
- Application Development
- Database Management

---

## 📄 License

No license file is currently specified in the repository.

If the project is intended for public open-source distribution, add an appropriate `LICENSE` file and update this section.

---

## ⭐ Project Summary

VoiceVault transforms unstructured voice and media into measurable and structured information through a single modular platform.

```text
🎙️ Speech Recognition
        +
🎬 Media Processing
        +
🤖 Multiple AI/ML Models
        +
📊 Objective Evaluation
        +
📝 Content Intelligence
        +
🗄️ Database Management
        +
🖥️ Interactive Application
```

**VoiceVault — From Voice to Valuable Information.**
