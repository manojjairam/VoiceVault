import time
from pathlib import Path

import whisper
from faster_whisper import WhisperModel


# ============================================================
# OPTIONAL TRANSFORMERS
# ============================================================
#
# IMPORTANT:
# Do NOT import transformers at application startup.
#
# Transformers is loaded only when Wav2Vec2 is actually used.
# This prevents Streamlit from scanning all Transformers
# vision modules and producing torchvision-related errors.
# ============================================================

_transformers_pipeline = None
_transformers_available = None


def get_transformers_pipeline():
    """
    Lazily import Hugging Face Transformers.

    Transformers is loaded only when Wav2Vec2 is requested.
    """

    global _transformers_pipeline
    global _transformers_available

    if _transformers_pipeline is not None:
        return _transformers_pipeline

    if _transformers_available is False:
        return None

    try:

        from transformers import pipeline

        _transformers_pipeline = pipeline
        _transformers_available = True

        return pipeline

    except Exception:

        _transformers_available = False

        return None


# ============================================================
# MODEL CACHE
# ============================================================

_whisper_models = {}

_faster_whisper_models = {}

_wav2vec_pipelines = {}


# ============================================================
# MODEL INFORMATION
# ============================================================

MODEL_INFORMATION = {

    "Whisper": {
        "type": "Transformer Encoder-Decoder",
        "architecture": "Whisper",
        "purpose": "Baseline ASR model",
    },

    "Faster-Whisper": {
        "type": "Transformer Encoder-Decoder",
        "architecture": "Whisper + CTranslate2",
        "purpose": "Speed-optimized Whisper transcription",
    },

    "Wav2Vec2": {
        "type": "CTC-based Speech Recognition",
        "architecture": "Wav2Vec2",
        "purpose": "Independent CTC-based ASR architecture",
    },
}


# ============================================================
# COMMON RESULT BUILDER
# ============================================================

def build_error_result(
    model_name,
    architecture,
    error,
    language="unknown",
):
    """
    Create a consistent failed-result structure.
    """

    return {

        "model": model_name,

        "architecture": architecture,

        "text": "",

        "language": language,

        "processing_time": 0,

        "success": False,

        "error": str(error),
    }


# ============================================================
# OPENAI WHISPER
# ============================================================

def transcribe_whisper(
    audio_path,
    model_size="base",
):
    """
    Transcribe audio using OpenAI Whisper.

    The model is loaded once and then cached.

    Recommended:
        base = better quality
        tiny = faster comparison
    """

    start_time = time.perf_counter()

    model_name = f"Whisper ({model_size})"

    try:

        # ----------------------------------------------------
        # Load model only once
        # ----------------------------------------------------

        if model_size not in _whisper_models:

            _whisper_models[model_size] = (
                whisper.load_model(model_size)
            )

        model = _whisper_models[model_size]

        # ----------------------------------------------------
        # Transcription
        # ----------------------------------------------------

        result = model.transcribe(

            audio_path,

            fp16=False,

            # Do not waste time trying to translate.
            task="transcribe",

            # Faster decoding.
            beam_size=1,

            best_of=1,

            temperature=0,

            condition_on_previous_text=False,
        )

        text = result.get(
            "text",
            "",
        ).strip()

        language = result.get(
            "language",
            "unknown",
        )

        processing_time = (
            time.perf_counter()
            - start_time
        )

        return {

            "model": model_name,

            "architecture":
                "Transformer Encoder-Decoder",

            "text": text,

            "language": language,

            "processing_time":
                round(
                    processing_time,
                    2,
                ),

            "success": True,
        }

    except Exception as e:

        return build_error_result(

            model_name,

            "Transformer Encoder-Decoder",

            e,
        )


# ============================================================
# FASTER-WHISPER
# ============================================================

def transcribe_faster_whisper(
    audio_path,
    model_size="base",
):
    """
    Transcribe audio using Faster-Whisper.

    Uses CTranslate2 with CPU INT8 quantization.

    This is the main fast ASR engine used by VoiceVault.
    """

    start_time = time.perf_counter()

    model_name = (
        f"Faster-Whisper ({model_size})"
    )

    try:

        # ----------------------------------------------------
        # Load model once
        # ----------------------------------------------------

        if model_size not in _faster_whisper_models:

            _faster_whisper_models[
                model_size
            ] = WhisperModel(

                model_size,

                device="cpu",

                compute_type="int8",

            )

        model = _faster_whisper_models[
            model_size
        ]

        # ----------------------------------------------------
        # Transcription
        # ----------------------------------------------------

        segments, info = model.transcribe(

            audio_path,

            beam_size=1,

            best_of=1,

            temperature=0,

            vad_filter=True,

            # Prevent unnecessarily long silence processing.
            vad_parameters={
                "min_silence_duration_ms": 500,
            },
        )

        text_parts = []

        for segment in segments:

            segment_text = (
                segment.text.strip()
            )

            if segment_text:

                text_parts.append(
                    segment_text
                )

        text = " ".join(
            text_parts
        ).strip()

        language = getattr(
            info,
            "language",
            "unknown",
        )

        processing_time = (
            time.perf_counter()
            - start_time
        )

        return {

            "model": model_name,

            "architecture":
                "Whisper + CTranslate2",

            "text": text,

            "language": language,

            "processing_time":
                round(
                    processing_time,
                    2,
                ),

            "success": True,
        }

    except Exception as e:

        return build_error_result(

            model_name,

            "Whisper + CTranslate2",

            e,
        )


# ============================================================
# WAV2VEC2
# ============================================================

def transcribe_wav2vec2(
    audio_path,
):
    """
    Transcribe using Wav2Vec2.

    Transformers is imported lazily only when this function
    is called.

    Model:
        facebook/wav2vec2-base-960h
    """

    start_time = time.perf_counter()

    model_name = "Wav2Vec2"

    try:

        # ----------------------------------------------------
        # Lazy Transformers import
        # ----------------------------------------------------

        pipeline = (
            get_transformers_pipeline()
        )

        if pipeline is None:

            return build_error_result(

                model_name,

                "CTC-based Speech Recognition",

                (
                    "Transformers could not be loaded. "
                    "Install compatible torch, torchvision "
                    "and transformers packages."
                ),

                language="English",
            )

        # ----------------------------------------------------
        # Model
        # ----------------------------------------------------

        model_name_hf = (
            "facebook/wav2vec2-base-960h"
        )

        # ----------------------------------------------------
        # Load model only once
        # ----------------------------------------------------

        if model_name_hf not in _wav2vec_pipelines:

            _wav2vec_pipelines[
                model_name_hf
            ] = pipeline(

                "automatic-speech-recognition",

                model=model_name_hf,

            )

        asr = _wav2vec_pipelines[
            model_name_hf
        ]

        # ----------------------------------------------------
        # Transcribe
        # ----------------------------------------------------

        result = asr(

            audio_path,

            chunk_length_s=20,

            stride_length_s=3,

        )

        text = result.get(
            "text",
            "",
        ).strip()

        processing_time = (
            time.perf_counter()
            - start_time
        )

        return {

            "model": model_name,

            "architecture":
                "CTC-based Speech Recognition",

            "text": text,

            "language": "English",

            "processing_time":
                round(
                    processing_time,
                    2,
                ),

            "success": True,
        }

    except Exception as e:

        return build_error_result(

            model_name,

            "CTC-based Speech Recognition",

            e,

            language="English",
        )


# ============================================================
# FAST TRANSCRIPTION
# ============================================================

def transcribe_fast(
    audio_path,
):
    """
    Fast transcription mode.

    Uses Faster-Whisper Tiny instead of Base.

    This is intentionally separate from the academic
    comparison.

    Tiny is significantly faster and is suitable for
    quickly obtaining a transcript.
    """

    return [

        transcribe_faster_whisper(

            audio_path,

            model_size="tiny",

        )

    ]


# ============================================================
# STANDARD COMPARISON
# ============================================================

def transcribe_standard_comparison(
    audio_path,
):
    """
    Standard 3-model comparison.

    Models:

        1. Whisper
        2. Faster-Whisper
        3. Wav2Vec2

    The Whisper models use BASE because the comparison
    should remain meaningful for academic evaluation.
    """

    return transcribe_with_all_models(

        audio_path,

        model_size="base",

        selected_models=[

            "Whisper",

            "Faster-Whisper",

            "Wav2Vec2",

        ],

    )


# ============================================================
# EXTENDED COMPARISON
# ============================================================

def transcribe_extended_comparison(
    audio_path,
):
    """
    Extended comparison.

    At present VoiceVault implements three models.

    Therefore the extended mode currently runs the same
    three available models rather than falsely reporting
    a fourth model.
    """

    return transcribe_with_all_models(

        audio_path,

        model_size="base",

        selected_models=[

            "Whisper",

            "Faster-Whisper",

            "Wav2Vec2",

        ],

    )


# ============================================================
# ALL MODEL TRANSCRIPTION
# ============================================================

def transcribe_with_all_models(
    audio_path,
    model_size="base",
    selected_models=None,
):
    """
    Run selected ASR models.

    IMPORTANT:
    Models are executed sequentially.

    This is intentional on CPU because launching all three
    models simultaneously can cause CPU contention and often
    makes the total execution time worse.
    """

    if selected_models is None:

        selected_models = [

            "Whisper",

            "Faster-Whisper",

            "Wav2Vec2",

        ]

    results = []

    # ========================================================
    # WHISPER
    # ========================================================

    if "Whisper" in selected_models:

        results.append(

            transcribe_whisper(

                audio_path,

                model_size=model_size,

            )

        )

    # ========================================================
    # FASTER-WHISPER
    # ========================================================

    if "Faster-Whisper" in selected_models:

        results.append(

            transcribe_faster_whisper(

                audio_path,

                model_size=model_size,

            )

        )

    # ========================================================
    # WAV2VEC2
    # ========================================================

    if "Wav2Vec2" in selected_models:

        results.append(

            transcribe_wav2vec2(

                audio_path,

            )

        )

    return results


# ============================================================
# AVAILABLE MODELS
# ============================================================

def get_available_models():
    """
    Return models available to VoiceVault.

    Wav2Vec2 is listed only if Transformers can be loaded.
    """

    models = [

        "Whisper",

        "Faster-Whisper",

    ]

    # Do not import Transformers here.
    # Only report it if it has already been successfully loaded.

    if _transformers_available is True:

        models.append(
            "Wav2Vec2"
        )

    return models


# ============================================================
# MODEL CACHE CONTROL
# ============================================================

def clear_model_cache():
    """
    Clear all locally cached model objects.

    Useful for development/testing if model versions
    or settings are changed.
    """

    _whisper_models.clear()

    _faster_whisper_models.clear()

    _wav2vec_pipelines.clear()

    global _transformers_pipeline
    global _transformers_available

    _transformers_pipeline = None

    _transformers_available = None