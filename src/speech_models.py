import time

import whisper
from faster_whisper import WhisperModel


# ============================================================
# OPTIONAL TRANSFORMERS / WAV2VEC2
# ============================================================

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True

except ImportError:
    TRANSFORMERS_AVAILABLE = False


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
        "purpose": "Independent ASR architecture for comparison",
    },
}


# ============================================================
# OPENAI WHISPER
# ============================================================

def transcribe_whisper(audio_path, model_size="base"):
    """
    Transcribe audio using OpenAI Whisper.

    This model is retained as the baseline model
    for comparative evaluation.
    """

    start_time = time.time()

    try:

        if model_size not in _whisper_models:

            _whisper_models[model_size] = (
                whisper.load_model(model_size)
            )

        model = _whisper_models[model_size]

        result = model.transcribe(
            audio_path,
            fp16=False,
        )

        processing_time = time.time() - start_time

        text = result.get(
            "text",
            ""
        ).strip()

        language = result.get(
            "language",
            "unknown"
        )

        return {
            "model": f"Whisper ({model_size})",
            "architecture": "Transformer Encoder-Decoder",
            "text": text,
            "language": language,
            "processing_time": round(
                processing_time,
                2
            ),
            "success": True,
        }

    except Exception as e:

        return {
            "model": f"Whisper ({model_size})",
            "architecture": "Transformer Encoder-Decoder",
            "text": "",
            "language": "unknown",
            "processing_time": 0,
            "success": False,
            "error": str(e),
        }


# ============================================================
# FASTER-WHISPER
# ============================================================

def transcribe_faster_whisper(
    audio_path,
    model_size="base"
):
    """
    Transcribe audio using Faster-Whisper.

    Faster-Whisper uses CTranslate2 and is optimized
    for efficient CPU inference.
    """

    start_time = time.time()

    try:

        if model_size not in _faster_whisper_models:

            _faster_whisper_models[model_size] = (
                WhisperModel(
                    model_size,
                    device="cpu",
                    compute_type="int8",
                )
            )

        model = _faster_whisper_models[
            model_size
        ]

        segments, info = model.transcribe(
            audio_path,
            beam_size=1,
            vad_filter=True,
        )

        text_parts = []

        for segment in segments:

            segment_text = segment.text.strip()

            if segment_text:

                text_parts.append(
                    segment_text
                )

        text = " ".join(
            text_parts
        ).strip()

        processing_time = (
            time.time() - start_time
        )

        language = getattr(
            info,
            "language",
            "unknown"
        )

        return {
            "model": f"Faster-Whisper ({model_size})",
            "architecture": "Whisper + CTranslate2",
            "text": text,
            "language": language,
            "processing_time": round(
                processing_time,
                2
            ),
            "success": True,
        }

    except Exception as e:

        return {
            "model": f"Faster-Whisper ({model_size})",
            "architecture": "Whisper + CTranslate2",
            "text": "",
            "language": "unknown",
            "processing_time": 0,
            "success": False,
            "error": str(e),
        }


# ============================================================
# WAV2VEC2
# ============================================================

def transcribe_wav2vec2(audio_path):
    """
    Transcribe audio using Wav2Vec2.

    Wav2Vec2 provides an independent CTC-based
    ASR architecture for academic comparison.

    Model:
        facebook/wav2vec2-base-960h

    The model is downloaded automatically the first
    time it is used.
    """

    if not TRANSFORMERS_AVAILABLE:

        return {
            "model": "Wav2Vec2",
            "architecture": "CTC-based Speech Recognition",
            "text": "",
            "language": "English",
            "processing_time": 0,
            "success": False,
            "error": (
                "Transformers is not installed. "
                "Run: pip install transformers torch"
            ),
        }

    start_time = time.time()

    model_name = (
        "facebook/wav2vec2-base-960h"
    )

    try:

        if model_name not in _wav2vec_pipelines:

            _wav2vec_pipelines[
                model_name
            ] = pipeline(
                "automatic-speech-recognition",
                model=model_name,
            )

        asr = _wav2vec_pipelines[
            model_name
        ]

        result = asr(
            audio_path,
            chunk_length_s=20,
            stride_length_s=3,
        )

        text = result.get(
            "text",
            ""
        ).strip()

        processing_time = (
            time.time() - start_time
        )

        return {
            "model": "Wav2Vec2",
            "architecture": "CTC-based Speech Recognition",
            "text": text,
            "language": "English",
            "processing_time": round(
                processing_time,
                2
            ),
            "success": True,
        }

    except Exception as e:

        return {
            "model": "Wav2Vec2",
            "architecture": "CTC-based Speech Recognition",
            "text": "",
            "language": "English",
            "processing_time": 0,
            "success": False,
            "error": str(e),
        }


# ============================================================
# QUICK / FAST TRANSCRIPTION
# ============================================================

def transcribe_fast(audio_path):
    """
    Fast transcription mode.

    Uses Faster-Whisper only so the user can quickly
    obtain a transcript without running every model.
    """

    return [
        transcribe_faster_whisper(
            audio_path,
            model_size="base"
        )
    ]


# ============================================================
# ALL MODEL TRANSCRIPTION
# ============================================================

def transcribe_with_all_models(
    audio_path,
    model_size="base",
    selected_models=None,
):
    """
    Run selected ASR models for comparative evaluation.

    Available models:

        Whisper
        Faster-Whisper
        Wav2Vec2
    """

    if selected_models is None:

        selected_models = [
            "Whisper",
            "Faster-Whisper",
            "Wav2Vec2",
        ]

    results = []

    # --------------------------------------------------------
    # Whisper
    # --------------------------------------------------------

    if "Whisper" in selected_models:

        results.append(
            transcribe_whisper(
                audio_path,
                model_size
            )
        )

    # --------------------------------------------------------
    # Faster-Whisper
    # --------------------------------------------------------

    if "Faster-Whisper" in selected_models:

        results.append(
            transcribe_faster_whisper(
                audio_path,
                model_size
            )
        )

    # --------------------------------------------------------
    # Wav2Vec2
    # --------------------------------------------------------

    if "Wav2Vec2" in selected_models:

        results.append(
            transcribe_wav2vec2(
                audio_path
            )
        )

    return results


# ============================================================
# STANDARD 3-MODEL COMPARISON
# ============================================================

def transcribe_standard_comparison(audio_path):
    """
    Run the standard 3-model ASR comparison.

    Models:
        1. OpenAI Whisper
        2. Faster-Whisper
        3. Wav2Vec2
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
# EXTENDED 4-MODEL COMPARISON
# ============================================================

def transcribe_extended_comparison(audio_path):
    """
    Run the extended ASR comparison.

    The current project contains three implemented
    ASR architectures. The fourth comparison slot is
    reserved for future model expansion.

    For the current implementation, the function
    executes the available three models.
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
# AVAILABLE MODELS
# ============================================================

def get_available_models():
    """
    Return the models available to VoiceVault.
    """

    models = [
        "Whisper",
        "Faster-Whisper",
    ]

    if TRANSFORMERS_AVAILABLE:

        models.append(
            "Wav2Vec2"
        )

    return models