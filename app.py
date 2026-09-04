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
    "domain_score": 0,

    "reference_text": "",

    "media_loaded": False,

    # IMPORTANT:
    # Comparison is now explicitly controlled.
    # It will NOT appear until the button is clicked.
    "comparison_run": False,

    # Keeps the evaluation button enabled after
    # the reference text is entered.
    "reference_ready": False,
}


for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# UTILITY
# ============================================================

def format_duration(seconds):

    try:
        seconds = int(float(seconds))

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
        "programming",
        "python",
        "cloud",
        "database",
        "engineering",
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
        "assignment",
        "school",
        "learning",
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
        "sales",
        "customer",
        "management",
        "financial",
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
        "democracy",
        "government",
        "campaign",
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
        "symptom",
        "diagnosis",
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
        "series",
        "television",
        "netflix",
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
        "championship",
        "league",
        "coach",
        "batting",
        "bowling",
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
        "announcement",
        "press",
        "statement",
    ],
}


def detect_domain(text):

    if not text:

        return {
            "domain": "General",
            "score": 0
        }

    text_lower = str(text).lower()

    scores = {}

    for domain, keywords in DOMAIN_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if re.search(
                r"\b"
                + re.escape(keyword)
                + r"\b",
                text_lower
            ):
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
# CONSISTENT DOMAIN
# ============================================================
#
# IMPORTANT FIX:
#
# Previously domain was calculated separately for every model.
# Therefore Whisper could say Entertainment while another
# model said Sports.
#
# Now VoiceVault chooses ONE primary transcript:
#
# 1. Fast transcription if available
# 2. Otherwise the longest successful comparison transcript
#
# The domain is calculated ONCE from that primary transcript.
#
# Therefore every model will use the same domain.
# ============================================================

def update_global_domain():

    primary_text = ""

    # Prefer the fast transcription result if it exists.
    if st.session_state.results:

        fast_candidates = []

        for result in st.session_state.results:

            if not result.get(
                "success",
                False
            ):
                continue

            model_name = str(
                result.get(
                    "model",
                    ""
                )
            ).lower()

            if (
                "faster-whisper" in model_name
                or "fast" in model_name
            ):

                fast_candidates.append(
                    result
                )

        if fast_candidates:

            primary_text = max(
                fast_candidates,
                key=lambda x: len(
                    x.get("text", "")
                )
            ).get(
                "text",
                ""
            )

    # Otherwise use the longest successful transcript.
    if not primary_text:

        successful = [
            r
            for r in st.session_state.results
            if r.get("success", False)
        ]

        if successful:

            primary_text = max(
                successful,
                key=lambda x: len(
                    x.get("text", "")
                )
            ).get(
                "text",
                ""
            )

    domain_result = detect_domain(
        primary_text
    )

    st.session_state.domain = (
        domain_result["domain"]
    )

    st.session_state.domain_score = (
        domain_result["score"]
    )

    return domain_result


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


def normalize_text(text):

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def calculate_wer(
    reference,
    hypothesis
):

    reference_words = normalize_text(
        reference
    ).split()

    hypothesis_words = normalize_text(
        hypothesis
    ).split()

    if not reference_words:
        return 0

    # Word-level Levenshtein distance.
    rows = len(reference_words) + 1
    cols = len(hypothesis_words) + 1

    previous = list(range(cols))

    for i in range(1, rows):

        current = [i]

        for j in range(1, cols):

            if (
                reference_words[i - 1]
                ==
                hypothesis_words[j - 1]
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

    distance = previous[-1]

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

    reference = normalize_text(
        reference
    )

    hypothesis = normalize_text(
        hypothesis
    )

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

    reference = normalize_text(
        reference
    )

    hypothesis = normalize_text(
        hypothesis
    )

    if not reference:
        return 0

    if not hypothesis:
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
        normalize_text(reference),
        normalize_text(hypothesis)
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

                    # RESET ALL PROCESSING STATE
                    st.session_state.results = []

                    st.session_state.comparison_results = None

                    st.session_state.domain = None

                    st.session_state.domain_score = 0

                    st.session_state.reference_text = ""

                    st.session_state.comparison_run = False

                    st.session_state.reference_ready = False

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

                # RESET PROCESSING STATE
                st.session_state.results = []

                st.session_state.comparison_results = None

                st.session_state.domain = None

                st.session_state.domain_score = 0

                st.session_state.reference_text = ""

                st.session_state.comparison_run = False

                st.session_state.reference_ready = False

                st.session_state.media_loaded = True

            except Exception as e:

                st.error(
                    "Unable to process uploaded file."
                )

                st.exception(e)


# ============================================================
# SOURCE INFORMATION
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
            if (
                st.session_state.source_has_audio
                or
                st.session_state.source_type
                == "audio"
            )
            else "No"
        )

    with col4:

        st.metric(
            "Video",
            "Available"
            if (
                st.session_state.source_has_video
                or
                st.session_state.source_type
                == "video"
            )
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

    # --------------------------------------------------------
    # DOMAIN NOW APPEARS INSIDE SOURCE INFORMATION
    # --------------------------------------------------------

    if st.session_state.domain:

        st.write(
            f"**Detected Domain:** "
            f"🏷️ **{st.session_state.domain}**"
        )

        if st.session_state.domain_score:

            st.caption(
                f"Domain confidence indicator: "
                f"{st.session_state.domain_score} "
                f"keyword matches"
            )

    else:

        st.write(
            "**Detected Domain:** "
            "Will be identified after transcription"
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
        "Use Faster-Whisper for a quick transcript. "
        "This is the recommended option when you want "
        "a result quickly."
    )

    if st.button(
        "⚡ Fast Transcribe",
        type="primary",
        use_container_width=True,
        key="fast_transcribe_button"
    ):

        with st.spinner(
            "Transcribing with Faster-Whisper..."
        ):

            results = transcribe_fast(
                st.session_state.audio_path
            )

        st.session_state.results = results

        # A fast transcription is NOT a comparison.
        st.session_state.comparison_run = False

        # Clear old evaluation.
        st.session_state.comparison_results = None

        # Determine ONE domain.
        update_global_domain()

        st.success(
            "✅ Fast transcription completed."
        )


# ============================================================
# FAST TRANSCRIPTION DISPLAY
# ============================================================

if (
    st.session_state.results
    and not st.session_state.comparison_run
):

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
            result.get(
                "model",
                "Speech Recognition Model"
            )
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
                "fast_transcript_"
                + str(
                    result.get(
                        "model",
                        "model"
                    )
                )
            )
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
        "This stage runs multiple ASR models on the "
        "same audio so their transcription quality "
        "and processing speed can be compared."
    )

    comparison_type = st.radio(
        "Comparison level",
        [
            "Standard – 3 ASR Models",
            "Extended – 4 ASR Models"
        ],
        horizontal=True,
        key="comparison_level"
    )

    st.info(
        "💡 For the fastest experiment, use "
        "**Standard – 3 ASR Models**."
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # There is NO automatic comparison result rendering here.
    #
    # Results appear ONLY after this button is clicked.
    # --------------------------------------------------------

    run_comparison = st.button(
        "🔬 Run Model Comparison",
        use_container_width=True,
        key="run_model_comparison"
    )

    if run_comparison:

        # Clear previous evaluation results.
        st.session_state.comparison_results = None

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

        # This flag controls whether comparison results
        # should be displayed.
        st.session_state.comparison_run = True

        # Calculate domain ONCE from all comparison output.
        update_global_domain()

        st.success(
            "✅ Model comparison transcription completed."
        )


# ============================================================
# MODEL COMPARISON RESULTS
# ============================================================

if (
    st.session_state.comparison_run
    and st.session_state.results
):

    st.divider()

    st.header(
        "🔬 Model Comparison Results"
    )

    comparison_rows = []

    for result in st.session_state.results:

        if not result.get(
            "success",
            False
        ):
            continue

        comparison_rows.append({

            "Model":
                result.get(
                    "model",
                    "Unknown"
                ),

            "Language":
                get_language_name(
                    result.get(
                        "language"
                    )
                ),

            "Processing Time (sec)":
                round(
                    float(
                        result.get(
                            "processing_time",
                            0
                        )
                    ),
                    2
                ),

            "Transcript Length":
                len(
                    result.get(
                        "text",
                        ""
                    )
                ),

            # IMPORTANT:
            # SAME DOMAIN FOR EVERY MODEL
            "Domain":
                st.session_state.domain
                or "General",
        })

    if comparison_rows:

        comparison_df = pd.DataFrame(
            comparison_rows
        )

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "The domain is determined once from the "
            "primary transcription and applied consistently "
            "across all models."
        )

        # ----------------------------------------------------
        # INDIVIDUAL TRANSCRIPTS
        # ----------------------------------------------------

        st.subheader(
            "📝 Model Transcriptions"
        )

        for index, result in enumerate(
            st.session_state.results
        ):

            if not result.get(
                "success",
                False
            ):
                continue

            model_name = result.get(
                "model",
                f"Model {index + 1}"
            )

            with st.expander(
                f"🎙️ {model_name}"
            ):

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Language",
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

                st.write(
                    f"**Domain:** "
                    f"{st.session_state.domain or 'General'}"
                )

                st.text_area(
                    "Transcript",
                    result.get(
                        "text",
                        ""
                    ),
                    height=220,
                    key=(
                        "comparison_transcript_"
                        + str(index)
                        + "_"
                        + re.sub(
                            r"\W+",
                            "_",
                            str(model_name)
                        )
                    )
                )

    else:

        st.warning(
            "No successful model results were returned."
        )


# ============================================================
# REFERENCE TEXT
# ============================================================

if (
    st.session_state.comparison_run
    and st.session_state.results
):

    st.divider()

    st.header(
        "5️⃣ Reference Transcript & Evaluation"
    )

    st.write(
        "Paste a manually verified reference transcript "
        "to calculate objective transcription accuracy."
    )

    st.info(
        "📌 Required for WER, CER, Word Accuracy and BLEU. "
        "If no reference transcript is available, you can "
        "still use the model speed and transcription comparison."
    )

    # --------------------------------------------------------
    # Use a KEY so Streamlit reliably stores the text.
    # --------------------------------------------------------

    reference_text = st.text_area(
        "Reference Transcript",
        value=st.session_state.reference_text,
        height=220,
        placeholder=(
            "Paste the manually verified transcript here..."
        ),
        key="reference_transcript_input"
    )

    # IMPORTANT:
    # Store the value every rerun.
    st.session_state.reference_text = reference_text

    st.session_state.reference_ready = bool(
        reference_text.strip()
    )

    # --------------------------------------------------------
    # BUTTON IS ALWAYS RENDERED.
    #
    # It is enabled when reference text exists.
    # This fixes the issue where the button disappeared.
    # --------------------------------------------------------

    evaluate_button = st.button(
        "📊 Evaluate Accuracy",
        type="primary",
        use_container_width=True,
        key="evaluate_accuracy_button",
        disabled=not st.session_state.reference_ready
    )

    if not st.session_state.reference_ready:

        st.caption(
            "⬆️ Paste the reference transcript above "
            "to enable the Evaluate Accuracy button."
        )

    # --------------------------------------------------------
    # RUN EVALUATION
    # --------------------------------------------------------

    if evaluate_button:

        reference = (
            st.session_state.reference_text.strip()
        )

        if not reference:

            st.warning(
                "Please paste a reference transcript first."
            )

        else:

            evaluation_rows = []

            for result in st.session_state.results:

                if not result.get(
                    "success",
                    False
                ):
                    continue

                hypothesis = result.get(
                    "text",
                    ""
                )

                if not hypothesis.strip():
                    continue

                metrics = evaluate_result(
                    reference,
                    hypothesis
                )

                evaluation_rows.append({

                    "Model":
                        result.get(
                            "model",
                            "Unknown"
                        ),

                    "Language":
                        get_language_name(
                            result.get(
                                "language"
                            )
                        ),

                    "WER (%)":
                        metrics[
                            "WER (%)"
                        ],

                    "CER (%)":
                        metrics[
                            "CER (%)"
                        ],

                    "Word Accuracy (%)":
                        metrics[
                            "Word Accuracy (%)"
                        ],

                    "BLEU":
                        metrics[
                            "BLEU"
                        ],

                    "Edit Distance":
                        metrics[
                            "Edit Distance"
                        ],

                    "Processing Time (sec)":
                        round(
                            float(
                                result.get(
                                    "processing_time",
                                    0
                                )
                            ),
                            2
                        ),

                    # SAME DOMAIN
                    "Domain":
                        st.session_state.domain
                        or "General",
                })

            if evaluation_rows:

                st.session_state.comparison_results = (
                    pd.DataFrame(
                        evaluation_rows
                    )
                )

                st.success(
                    "✅ Accuracy evaluation completed."
                )

            else:

                st.warning(
                    "No successful model transcripts "
                    "were available for evaluation."
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

    # --------------------------------------------------------
    # FULL RESULTS
    # --------------------------------------------------------

    st.subheader(
        "Complete Evaluation Results"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # ACCURACY COMPARISON
    # --------------------------------------------------------

    st.subheader(
        "🎯 Accuracy Comparison"
    )

    accuracy_columns = [
        "Model",
        "WER (%)",
        "CER (%)",
        "Word Accuracy (%)",
        "BLEU",
    ]

    available_accuracy_columns = [
        column
        for column in accuracy_columns
        if column in df.columns
    ]

    st.dataframe(
        df[
            available_accuracy_columns
        ],
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # PROCESSING SPEED
    # --------------------------------------------------------

    st.subheader(
        "⚡ Processing Speed"
    )

    if (
        "Processing Time (sec)"
        in df.columns
    ):

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

    if len(df) > 0:

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

        best_accuracy = df.loc[
            df[
                "Word Accuracy (%)"
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

            st.success(
                f"📝 Lowest CER: "
                f"**{best_cer['Model']}**"
            )

        with col2:

            st.success(
                f"🏅 Highest BLEU: "
                f"**{best_bleu['Model']}**"
            )

            st.success(
                f"⭐ Highest Word Accuracy: "
                f"**{best_accuracy['Model']}**"
            )

        # ----------------------------------------------------
        # DOMAIN
        # ----------------------------------------------------

        st.info(
            f"🏷️ **Detected Domain:** "
            f"**{st.session_state.domain or 'General'}**"
        )


# ============================================================
# NO REFERENCE ANALYSIS
# ============================================================

if (
    st.session_state.comparison_run
    and st.session_state.results
    and not st.session_state.reference_text.strip()
):

    st.divider()

    st.header(
        "📋 Analysis Without Reference Transcript"
    )

    st.write(
        "Since no manually verified reference transcript "
        "was provided, objective accuracy metrics cannot "
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
                    result.get(
                        "model",
                        "Unknown"
                    ),

                "Language":
                    get_language_name(
                        result.get(
                            "language"
                        )
                    ),

                "Processing Time (sec)":
                    round(
                        float(
                            result.get(
                                "processing_time",
                                0
                            )
                        ),
                        2
                    ),

                "Transcript Length":
                    len(
                        result.get(
                            "text",
                            ""
                        )
                    ),

                # SAME DOMAIN
                "Domain":
                    st.session_state.domain
                    or "General",
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
# PERFORMANCE NOTE
# ============================================================

if st.session_state.comparison_run:

    st.divider()

    st.caption(
        "⚡ Performance note: VoiceVault keeps the "
        "comparison separate from fast transcription. "
        "For the quickest demonstration, use Fast "
        "Transcription first. The standard comparison "
        "runs the configured Whisper, Faster-Whisper "
        "and Wav2Vec2 models. Model loading is cached "
        "by the speech-model module when supported."
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