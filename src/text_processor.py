import nltk
from nltk.tokenize import sent_tokenize


def download_nltk_resources():
    """Download the NLTK resources required for sentence tokenization."""
    nltk.download("punkt")
    nltk.download("punkt_tab")


def split_into_sentences(text):
    """
    Split the given text into individual sentences.

    Args:
        text (str): The input paragraph or document.

    Returns:
        list: A list containing individual sentences.
    """
    if not text or not text.strip():
        return []

    sentences = sent_tokenize(text)

    return sentences