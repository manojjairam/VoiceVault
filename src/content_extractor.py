import re


def extract_content(transcription):
    """
    Extract useful organizational information from a transcription.
    Returns a dictionary containing title, summary, key points,
    action items, and keywords.
    """

    if not transcription or not transcription.strip():
        return {
            "title": "No Content Available",
            "summary": "",
            "key_points": [],
            "action_items": [],
            "keywords": []
        }

    text = transcription.strip()

    # Split transcription into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    # Generate title from the first few words
    words = text.split()
    title_words = words[:8]
    title = " ".join(title_words)

    if len(words) > 8:
        title += "..."

    # Create a simple summary
    if len(sentences) <= 2:
        summary = " ".join(sentences)
    else:
        summary = " ".join(sentences[:2])

    # Extract key points
    key_points = sentences[:5]

    # Identify possible action items
    action_keywords = [
        "need to",
        "should",
        "must",
        "please",
        "complete",
        "finish",
        "submit",
        "review",
        "prepare",
        "schedule",
        "send",
        "update",
        "create"
    ]

    action_items = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(keyword in sentence_lower for keyword in action_keywords):
            action_items.append(sentence)

    # Extract basic keywords
    stop_words = {
        "the", "is", "a", "an", "and", "or", "to", "of",
        "in", "on", "for", "with", "that", "this", "it",
        "are", "was", "were", "be", "as", "at", "by",
        "from", "we", "you", "they", "i"
    }

    clean_words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())

    keyword_frequency = {}

    for word in clean_words:
        if word not in stop_words:
            keyword_frequency[word] = keyword_frequency.get(word, 0) + 1

    sorted_keywords = sorted(
        keyword_frequency,
        key=keyword_frequency.get,
        reverse=True
    )

    keywords = sorted_keywords[:10]

    return {
        "title": title,
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
        "keywords": keywords
    }

