import os
import tempfile
import librosa
import soundfile as sf


def get_audio_info(audio_path):
    """
    Returns basic information about an audio file.
    """

    try:
        audio, sample_rate = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=audio, sr=sample_rate)

        return {
            "duration_seconds": round(duration, 2),
            "sample_rate": sample_rate,
            "channels": 1 if audio.ndim == 1 else audio.shape[1],
            "file_name": os.path.basename(audio_path)
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def convert_to_wav(uploaded_file):
    """
    Saves an uploaded audio file temporarily and converts it to WAV.
    """

    suffix = os.path.splitext(uploaded_file.name)[1]

    temp_input = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    )
    temp_input.write(uploaded_file.getbuffer())
    temp_input.close()

    audio, sample_rate = librosa.load(temp_input.name, sr=16000)

    temp_output = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )
    temp_output.close()

    sf.write(temp_output.name, audio, sample_rate)

    return temp_output.name


def save_uploaded_audio(uploaded_file):
    """
    Saves the uploaded file temporarily and returns its path.
    """

    suffix = os.path.splitext(uploaded_file.name)[1]

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    )

    temp_file.write(uploaded_file.getbuffer())
    temp_file.close()

    return temp_file.name


def validate_audio_file(uploaded_file):
    """
    Validates whether the uploaded file is an audio file.
    """

    allowed_extensions = [
        ".wav",
        ".mp3",
        ".m4a",
        ".flac",
        ".ogg"
    ]

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    if extension not in allowed_extensions:
        return False, (
            "Unsupported audio format. "
            "Please upload WAV, MP3, M4A, FLAC, or OGG."
        )

    return True, "Valid audio file."

