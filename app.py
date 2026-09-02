import os
import re
import subprocess
import tempfile
from pathlib import Path

import librosa
import pandas as pd
import sacrebleu
import streamlit as st

from src.media_downloader import (
    download_online_media,
    extract_audio_from_video,
)

from src.speech_models import (
    transcribe_fast,
    transcribe_standard_comparison,
    transcribe_extended_comparison,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="VoiceVault",
    page_icon="🎙️",
    layout="wide"
)


# ============================================================
# LANGUAGE MAP
# ============================================================

LANGUAGE_NAMES = {

    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
}

 
def get_language_name(code):

    if not code:
        return "Unknown"

    code = str(code).lower().strip()

    return LANGUAGE_NAMES.get(
        code,
        code.upper()
    )


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {

    "audio_path": None,
    "audio_name": "",
    "source_url": "",
    "source_type": "",
    "source_title": "",
    "source_uploader": "",
    "source_duration": 0,
    "source_has_video": False,
    "source_has_audio": False,

    "results": [],

    "comparison_results": None,

    "domain": None,

    "reference_text": "",

    "media_loaded": False,
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# UTILITY
# ============================================================

def format_duration(seconds):

    try:

        seconds = int(seconds)

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        seconds = seconds % 60

        if hours:

            return (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        return (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    except Exception:

        return "Unknown"


def get_audio_information(audio_path):

    try:

        audio, sr = librosa.load(
            audio_path,
            sr=None,
            mono=True
        )

        duration = librosa.get_duration(
            y=audio,
            sr=sr
        )

        return round(duration, 2), sr

    except Exception:

        return 0, 0


# ============================================================
# FILE DETECTION
# ============================================================

def is_video_file(file_path):

    if not file_path:
        return False

    if isinstance(file_path, dict):

        for key in [
            "path",
            "file_path",
            "filepath",
            "downloaded_path",
            "output_path",
            "filename",
            "file"
        ]:

            value = file_path.get(key)

            if isinstance(value, str):

                if os.path.exists(value):

                    file_path = value
                    break

        else:

            return False

    if not isinstance(
        file_path,
        (str, os.PathLike)
    ):

        return False

    extension = Path(
        file_path
    ).suffix.lower()

    video_extensions = {

        ".mp4",
        ".mkv",
        ".webm",
        ".avi",
        ".mov",
        ".flv",
        ".wmv",
        ".m4v",
        ".3gp",
    }

    if extension in video_extensions:

        return True

    try:

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_type",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        return (
            "video"
            in result.stdout.lower()
        )

    except Exception:

        return False


# ============================================================
# DOWNLOADED PATH
# ============================================================

def get_downloaded_path(result):

    if isinstance(result, str):

        if os.path.exists(result):

            return result

        return None

    if isinstance(result, Path):

        if result.exists():

            return str(result)

        return None

    if isinstance(result, dict):

        keys = [

            "path",
            "file_path",
            "filepath",
            "downloaded_path",
            "output_path",
            "filename",
            "file",
            "audio_path",
        ]

        for key in keys:

            value = result.get(key)

            if isinstance(
                value,
                (str, Path)
            ):

                value = str(value)

                if os.path.exists(value):

                    return value

        for value in result.values():

            if isinstance(value, dict):

                nested = get_downloaded_path(
                    value
                )

                if nested:

                    return nested

            elif isinstance(
                value,
                (str, Path)
            ):

                value = str(value)

                if os.path.exists(value):

                    return value

    return None


# ============================================================
# PREPARE MEDIA
# ============================================================

def prepare_media(download_result):

    media_path = get_downloaded_path(
        download_result
    )

    if not media_path:

        raise ValueError(
            "The downloader did not return "
            "a valid media file."
        )

    if not is_video_file(media_path):

        return media_path, "audio"

    st.info(
        "🎬 Video detected. "
        "Extracting audio..."
    )

    extraction = extract_audio_from_video(
        media_path
    )

    audio_path = get_downloaded_path(
        extraction
    )

    if not audio_path:

        raise ValueError(
            "The video was downloaded, "
            "but audio extraction failed."
        )

    return audio_path, "video"


# ============================================================
# DOMAIN DETECTION
# ============================================================

DOMAIN_KEYWORDS = {

    "Science & Technology": [

        "science",
        "technology",
        "artificial intelligence",
        "machine learning",
        "computer",
        "software",
        "physics",
        "chemistry",
        "biology",
        "space",
        "nasa",
        "robot",
        "data",
        "algorithm",
    ],

    "Education": [

        "lecture",
        "lesson",
        "education",
        "student",
        "teacher",
        "class",
        "university",
        "college",
        "course",
        "tutorial",
        "exam",
    ],

    "Business & Finance": [

        "business",
        "company",
        "market",
        "finance",
        "investment",
        "stock",
        "revenue",
        "profit",
        "economy",
        "bank",
        "entrepreneur",
    ],

    "Politics & Government": [

        "government",
        "politics",
        "political",
        "election",
        "minister",
        "president",
        "parliament",
        "policy",
        "government",
    ],

    "Health & Medicine": [

        "health",
        "medicine",
        "doctor",
        "hospital",
        "disease",
        "medical",
        "patient",
        "treatment",
        "healthcare",
    ],

    "Entertainment": [

        "movie",
        "film",
        "actor",
        "actress",
        "music",
        "song",
        "celebrity",
        "cinema",
        "entertainment",
    ],

    "Sports": [

        "football",
        "cricket",
        "tennis",
        "basketball",
        "match",
        "player",
        "team",
        "goal",
        "score",
        "tournament",
    ],

    "News": [

        "news",
        "breaking",
        "report",
        "journalist",
        "headline",
        "latest",
        "incident",
        "according to",
    ],
}


def detect_domain(text):

    if not text:

        return {
            "domain": "General",
            "score": 0
        }

    text_lower = text.lower()

    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text_lower:

                score += 1

        scores[domain] = score

    best_domain = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_domain]

    if best_score == 0:

        return {
            "domain": "General",
            "score": 0
        }

    return {
        "domain": best_domain,
        "score": best_score
    }


# ============================================================
# METRICS
# ============================================================

def levenshtein_distance(
    reference,
    hypothesis
):

    reference = reference.lower()
    hypothesis = hypothesis.lower()

    rows = len(reference) + 1
    cols = len(hypothesis) + 1

    previous = list(
        range(cols)
    )

    for i in range(1, rows):

        current = [i]

        for j in range(1, cols):

            if (
                reference[i - 1]
                ==
                hypothesis[j - 1]
            ):

                cost = 0

            else:

                cost = 1

            current.append(
                min(

                    current[j - 1] + 1,

                    previous[j] + 1,

                    previous[j - 1] + cost,
                )
            )

        previous = current

    return previous[-1]


def calculate_wer(
    reference,
    hypothesis
):

    reference_words = (
        reference.lower().split()
    )

    hypothesis_words = (
        hypothesis.lower().split()
    )

    if not reference_words:

        return 0

    distance = levenshtein_distance(
        " ".join(reference_words),
        " ".join(hypothesis_words)
    )

    return round(
        distance
        /
        max(
            1,
            len(reference_words)
        )
        * 100,
        2
    )


def calculate_cer(
    reference,
    hypothesis
):

    if not reference:

        return 0

    distance = levenshtein_distance(
        reference,
        hypothesis
    )

    return round(
        distance
        /
        max(
            1,
            len(reference)
        )
        * 100,
        2
    )


def calculate_bleu(
    reference,
    hypothesis
):

    if not reference.strip():

        return 0

    return round(
        sacrebleu.sentence_bleu(
            hypothesis,
            [reference]
        ).score,
        2
    )


def calculate_word_accuracy(
    wer
):

    return round(
        max(
            0,
            100 - wer
        ),
        2
    )


# ============================================================
# EVALUATION
# ============================================================

def evaluate_result(
    reference,
    hypothesis
):

    wer = calculate_wer(
        reference,
        hypothesis
    )

    cer = calculate_cer(
        reference,
        hypothesis
    )

    bleu = calculate_bleu(
        reference,
        hypothesis
    )

    edit_distance = levenshtein_distance(
        reference,
        hypothesis
    )

    return {

        "WER (%)": wer,

        "CER (%)": cer,

        "Word Accuracy (%)":
            calculate_word_accuracy(
                wer
            ),

        "BLEU":
            bleu,

        "Edit Distance":
            edit_distance,
    }


# ============================================================
# TITLE
# ============================================================

st.title(
    "🎙️ VoiceVault"
)

st.write(
    "A multi-model speech transcription and "
    "performance evaluation system."
)


st.caption(
    "VoiceVault separates fast transcription from "
    "detailed evaluation so that experiments can be "
    "performed efficiently without repeatedly "
    "running expensive models."
)


# ============================================================
# SOURCE
# ============================================================

st.header(
    "1️⃣ Select Input"
)

source = st.radio(
    "Choose your source:",
    [
        "📁 Upload Audio / Video",
        "🌐 Online Media URL",
    ],
    horizontal=True
)


# ============================================================
# ONLINE URL
# ============================================================

if source == "🌐 Online Media URL":

    url = st.text_input(
        "Paste YouTube / Media URL",
        placeholder=(
            "https://www.youtube.com/watch?v=..."
        )
    )

    if st.button(
        "🔗 Load Media",
        type="primary",
        use_container_width=True
    ):

        if not url.strip():

            st.warning(
                "Please enter a URL."
            )

        else:

            with st.spinner(
                "Retrieving media..."
            ):

                result = download_online_media(
                    url.strip()
                )

            if not result.get(
                "success",
                False
            ):

                st.error(
                    result.get(
                        "error",
                        "Unable to download media."
                    )
                )

            else:

                try:

                    media_path, media_type = (
                        prepare_media(result)
                    )

                    st.session_state.audio_path = (
                        media_path
                    )

                    st.session_state.audio_name = (
                        os.path.basename(
                            media_path
                        )
                    )

                    st.session_state.source_url = (
                        url.strip()
                    )

                    st.session_state.source_type = (
                        media_type
                    )

                    st.session_state.source_title = (
                        result.get(
                            "title",
                            "Unknown"
                        )
                    )

                    st.session_state.source_uploader = (
                        result.get(
                            "uploader",
                            "Unknown"
                        )
                    )

                    st.session_state.source_duration = (
                        result.get(
                            "duration",
                            0
                        )
                    )

                    st.session_state.source_has_video = (
                        result.get(
                            "has_video",
                            False
                        )
                    )

                    st.session_state.source_has_audio = (
                        result.get(
                            "has_audio",
                            True
                        )
                    )

                    st.session_state.results = []

                    st.session_state.comparison_results = None

                    st.session_state.domain = None

                    st.session_state.media_loaded = True

                    st.success(
                        "✅ Media loaded successfully."
                    )

                except Exception as e:

                    st.error(
                        "❌ Unable to prepare the media."
                    )

                    st.exception(e)


# ============================================================
# FILE UPLOAD
# ============================================================

else:

    uploaded_file = st.file_uploader(
        "Upload Audio or Video",
        type=[
            "wav",
            "mp3",
            "m4a",
            "ogg",
            "flac",
            "aac",
            "mp4",
            "mkv",
            "webm",
            "avi",
            "mov",
            "m4v",
        ]
    )

    if uploaded_file:

        if (
            st.session_state.audio_name
            != uploaded_file.name
        ):

            suffix = Path(
                uploaded_file.name
            ).suffix

            temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            )

            temp.write(
                uploaded_file.getbuffer()
            )

            temp.close()

            uploaded_path = temp.name

            try:

                if is_video_file(
                    uploaded_path
                ):

                    st.info(
                        "🎬 Video detected. "
                        "Extracting audio..."
                    )

                    extraction = (
                        extract_audio_from_video(
                            uploaded_path
                        )
                    )

                    audio_path = (
                        get_downloaded_path(
                            extraction
                        )
                    )

                    if not audio_path:

                        raise ValueError(
                            "Audio extraction failed."
                        )

                    media_type = "video"

                else:

                    audio_path = uploaded_path

                    media_type = "audio"

                st.session_state.audio_path = (
                    audio_path
                )

                st.session_state.audio_name = (
                    uploaded_file.name
                )

                st.session_state.source_type = (
                    media_type
                )

                st.session_state.source_url = ""

                st.session_state.source_title = (
                    uploaded_file.name
                )

                st.session_state.source_uploader = (
                    "Uploaded file"
                )

                duration, _ = (
                    get_audio_information(
                        audio_path
                    )
                )

                st.session_state.source_duration = (
                    duration
                )

                st.session_state.results = []

                st.session_state.comparison_results = None

                st.session_state.domain = None

                st.session_state.media_loaded = True

            except Exception as e:

                st.error(
                    "Unable to process uploaded file."
                )

                st.exception(e)


# ============================================================
# MEDIA DETAILS
# ============================================================

if (
    st.session_state.media_loaded
    and st.session_state.audio_path
):

    st.divider()

    st.header(
        "2️⃣ Source Information"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Media Type",
            st.session_state.source_type.title()
        )

    with col2:

        st.metric(
            "Duration",
            format_duration(
                st.session_state.source_duration
            )
        )

    with col3:

        st.metric(
            "Audio",
            "Available"
            if st.session_state.source_has_audio
            or st.session_state.source_type == "audio"
            else "No"
        )

    with col4:

        st.metric(
            "Video",
            "Available"
            if st.session_state.source_has_video
            or st.session_state.source_type == "video"
            else "No"
        )

    st.write(
        f"**Title:** "
        f"{st.session_state.source_title}"
    )

    st.write(
        f"**Source / Uploader:** "
        f"{st.session_state.source_uploader}"
    )

    if st.session_state.source_url:

        st.write(
            f"**Source URL:** "
            f"{st.session_state.source_url}"
        )

    duration, sample_rate = (
        get_audio_information(
            st.session_state.audio_path
        )
    )

    st.write(
        f"**Audio Duration:** "
        f"{duration} seconds"
    )

    st.write(
        f"**Sample Rate:** "
        f"{sample_rate} Hz"
    )

    st.audio(
        st.session_state.audio_path
    )


# ============================================================
# FAST TRANSCRIPTION
# ============================================================

if (
    st.session_state.media_loaded
    and st.session_state.audio_path
):

    st.divider()

    st.header(
        "3️⃣ Fast Transcription"
    )

    st.write(
        "Start with Faster-Whisper Tiny for rapid "
        "transcription. The result is cached so "
        "re-running the page does not automatically "
        "transcribe the same media again."
    )

    if st.button(
        "⚡ Fast Transcribe",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Transcribing with Faster-Whisper Tiny..."
        ):

            results = transcribe_fast(
                st.session_state.audio_path
            )

        st.session_state.results = results

        st.success(
            "✅ Fast transcription completed."
        )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.results:

    st.divider()

    st.header(
        "📝 Transcription"
    )

    for result in st.session_state.results:

        if not result.get(
            "success",
            False
        ):

            st.error(
                result.get(
                    "error",
                    "Transcription failed."
                )
            )

            continue

        st.subheader(
            result["model"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Detected Language",
                get_language_name(
                    result.get(
                        "language"
                    )
                )
            )

        with col2:

            st.metric(
                "Processing Time",
                f"{result.get('processing_time', 0)} sec"
            )

        with col3:

            st.metric(
                "Source",
                "Cache"
                if result.get(
                    "from_cache"
                )
                else "New Run"
            )

        st.text_area(
            "Transcript",
            result.get(
                "text",
                ""
            ),
            height=250,
            key=(
                "transcript_"
                + result["model"]
            )
        )

        domain_result = detect_domain(
            result.get(
                "text",
                ""
            )
        )

        st.info(
            f"🏷️ Detected Domain: "
            f"**{domain_result['domain']}**"
        )

        if domain_result["score"]:

            st.caption(
                f"Domain confidence indicator: "
                f"{domain_result['score']} keyword matches"
            )


# ============================================================
# MODEL COMPARISON
# ============================================================

if (
    st.session_state.media_loaded
    and st.session_state.audio_path
):

    st.divider()

    st.header(
        "4️⃣ ASR Model Comparison"
    )

    st.write(
        "This stage is separate from fast transcription. "
        "Run it only when you want to perform the "
        "comparative experiment."
    )

    comparison_type = st.radio(
        "Comparison level",
        [
            "Standard – 3 ASR Models",
            "Extended – 4 ASR Models"
        ],
        horizontal=True
    )

    if st.button(
        "🔬 Run Model Comparison",
        use_container_width=True
    ):

        if comparison_type.startswith(
            "Standard"
        ):

            with st.spinner(
                "Running 3-model ASR comparison..."
            ):

                comparison = (
                    transcribe_standard_comparison(
                        st.session_state.audio_path
                    )
                )

        else:

            with st.spinner(
                "Running extended 4-model ASR comparison..."
            ):

                comparison = (
                    transcribe_extended_comparison(
                        st.session_state.audio_path
                    )
                )

        st.session_state.results = comparison

        st.success(
            "✅ Model comparison transcription completed."
        )


# ============================================================
# REFERENCE TEXT
# ============================================================

if st.session_state.results:

    st.divider()

    st.header(
        "5️⃣ Reference Transcript & Evaluation"
    )

    st.write(
        "A reference transcript is required for objective "
        "accuracy metrics such as WER, CER and BLEU."
    )

    st.info(
        "Don't have a reference transcript? You can still "
        "use VoiceVault for transcription, model speed "
        "comparison and qualitative analysis. Accuracy "
        "metrics will simply be skipped."
    )

    reference_text = st.text_area(
        "Reference Transcript (Optional)",
        value=st.session_state.reference_text,
        height=180,
        placeholder=(
            "Paste the manually verified transcript here "
            "if you have one..."
        )
    )

    st.session_state.reference_text = reference_text


# ============================================================
# EVALUATION
# ============================================================

if (
    st.session_state.results
    and st.session_state.reference_text.strip()
):

    if st.button(
        "📊 Evaluate Accuracy",
        type="primary",
        use_container_width=True
    ):

        evaluation_rows = []

        for result in st.session_state.results:

            if not result.get(
                "success",
                False
            ):

                continue

            metrics = evaluate_result(
                st.session_state.reference_text,
                result.get(
                    "text",
                    ""
                )
            )

            evaluation_rows.append({

                "Model":
                    result["model"],

                "Language":
                    get_language_name(
                        result.get(
                            "language"
                        )
                    ),

                "WER (%)":
                    metrics["WER (%)"],

                "CER (%)":
                    metrics["CER (%)"],

                "Word Accuracy (%)":
                    metrics[
                        "Word Accuracy (%)"
                    ],

                "BLEU":
                    metrics["BLEU"],

                "Edit Distance":
                    metrics[
                        "Edit Distance"
                    ],

                "Processing Time (sec)":
                    result[
                        "processing_time"
                    ],
            })

        if evaluation_rows:

            evaluation_df = pd.DataFrame(
                evaluation_rows
            )

            st.session_state.comparison_results = (
                evaluation_df
            )


# ============================================================
# DISPLAY EVALUATION
# ============================================================

if (
    st.session_state.comparison_results
    is not None
):

    st.divider()

    st.header(
        "📊 Experimental Results"
    )

    df = (
        st.session_state.comparison_results
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Accuracy Comparison"
    )

    accuracy_columns = [

        "Model",
        "WER (%)",
        "CER (%)",
        "Word Accuracy (%)",
        "BLEU",
    ]

    st.dataframe(
        df[accuracy_columns],
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Processing Speed"
    )

    speed_df = df[
        [
            "Model",
            "Processing Time (sec)"
        ]
    ].set_index(
        "Model"
    )

    st.bar_chart(
        speed_df
    )

    # --------------------------------------------------------
    # BEST MODELS
    # --------------------------------------------------------

    fastest = df.loc[
        df[
            "Processing Time (sec)"
        ].idxmin()
    ]

    best_wer = df.loc[
        df[
            "WER (%)"
        ].idxmin()
    ]

    best_cer = df.loc[
        df[
            "CER (%)"
        ].idxmin()
    ]

    best_bleu = df.loc[
        df[
            "BLEU"
        ].idxmax()
    ]

    st.subheader(
        "🏆 Experimental Summary"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"⚡ Fastest Model: "
            f"**{fastest['Model']}**"
        )

        st.success(
            f"🎯 Lowest WER: "
            f"**{best_wer['Model']}**"
        )

    with col2:

        st.success(
            f"📝 Lowest CER: "
            f"**{best_cer['Model']}**"
        )

        st.success(
            f"🏅 Highest BLEU: "
            f"**{best_bleu['Model']}**"
        )


# ============================================================
# NO REFERENCE ANALYSIS
# ============================================================

if (
    st.session_state.results
    and not st.session_state.reference_text.strip()
):

    st.divider()

    st.header(
        "📋 Analysis Without Reference Transcript"
    )

    st.write(
        "Since no manually verified transcript was "
        "provided, objective accuracy metrics cannot "
        "be calculated."
    )

    speed_rows = []

    for result in st.session_state.results:

        if result.get(
            "success",
            False
        ):

            speed_rows.append({

                "Model":
                    result["model"],

                "Language":
                    get_language_name(
                        result.get(
                            "language"
                        )
                    ),

                "Processing Time (sec)":
                    result[
                        "processing_time"
                    ],

                "Transcript Length":
                    len(
                        result.get(
                            "text",
                            ""
                        )
                    ),

                "Domain":
                    detect_domain(
                        result.get(
                            "text",
                            ""
                        )
                    )["domain"],
            })

    if speed_rows:

        no_reference_df = pd.DataFrame(
            speed_rows
        )

        st.dataframe(
            no_reference_df,
            use_container_width=True,
            hide_index=True
        )

        fastest = no_reference_df.loc[
            no_reference_df[
                "Processing Time (sec)"
            ].idxmin()
        ]

        st.info(
            f"⚡ Based on processing speed, "
            f"**{fastest['Model']}** was fastest "
            f"for this sample."
        )


# ============================================================
# PROFESSOR REQUIREMENT NOTE
# ============================================================

st.divider()

st.caption(
    "VoiceVault supports multi-model speech recognition, "
    "experimental comparison, WER, CER, Word Accuracy, "
    "BLEU, Edit Distance, processing-time analysis, "
    "language identification and domain classification."
)