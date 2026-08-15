def clean_text(results):
    """
    Create a cleaned version of the text by removing
    sentences classified as Off Topic.

    Args:
        results (list): Results produced by the topic drift detector.

    Returns:
        str: Cleaned text containing relevant sentences.
    """

    cleaned_sentences = []

    for result in results:
        if result["classification"] != "Off Topic":
            cleaned_sentences.append(result["sentence"])

    return " ".join(cleaned_sentences)