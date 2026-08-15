def classify_sentence(score, high_threshold=0.50, partial_threshold=0.30):
    """
    Classify a sentence based on its semantic similarity score.

    Args:
        score (float): Similarity score between topic and sentence.
        high_threshold (float): Minimum score for Highly Relevant.
        partial_threshold (float): Minimum score for Partially Relevant.

    Returns:
        str: Relevance classification.
    """

    if score >= high_threshold:
        return "Highly Relevant"

    elif score >= partial_threshold:
        return "Partially Relevant"

    else:
        return "Off Topic"


def detect_topic_drift(
    sentences,
    scores,
    high_threshold=0.50,
    partial_threshold=0.30
):
    """
    Analyze sentences and detect topic drift using customizable thresholds.

    Args:
        sentences (list): List of input sentences.
        scores (list): Semantic similarity scores.
        high_threshold (float): Threshold for Highly Relevant.
        partial_threshold (float): Threshold for Partially Relevant.

    Returns:
        list: Analysis results for every sentence.
    """

    results = []

    for sentence, score in zip(sentences, scores):

        classification = classify_sentence(
            score,
            high_threshold,
            partial_threshold
        )

        results.append({
            "sentence": sentence,
            "similarity_score": round(score, 4),
            "classification": classification
        })

    return results