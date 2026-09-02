import re
import sacrebleu


def normalize_text(text):
    """
    Normalizes text before evaluation.
    """

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_bleu(reference, hypothesis):
    """
    Calculates BLEU score between the reference
    transcription and model transcription.
    """

    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    if not reference or not hypothesis:
        return 0.0

    score = sacrebleu.sentence_bleu(
        hypothesis,
        [reference]
    ).score

    return round(score, 2)


def calculate_wer(reference, hypothesis):
    """
    Calculates Word Error Rate manually.

    WER = (Substitutions + Deletions + Insertions)
          / Number of words in reference
    """

    reference_words = normalize_text(reference).split()
    hypothesis_words = normalize_text(hypothesis).split()

    if not reference_words:
        return 0.0

    rows = len(reference_words) + 1
    columns = len(hypothesis_words) + 1

    distance = [
        [0 for _ in range(columns)]
        for _ in range(rows)
    ]

    for i in range(rows):
        distance[i][0] = i

    for j in range(columns):
        distance[0][j] = j

    for i in range(1, rows):
        for j in range(1, columns):

            if reference_words[i - 1] == hypothesis_words[j - 1]:
                cost = 0
            else:
                cost = 1

            distance[i][j] = min(
                distance[i - 1][j] + 1,
                distance[i][j - 1] + 1,
                distance[i - 1][j - 1] + cost
            )

    wer = distance[-1][-1] / len(reference_words)

    return round(wer * 100, 2)


def calculate_cer(reference, hypothesis):
    """
    Calculates Character Error Rate.
    """

    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    if not reference:
        return 0.0

    rows = len(reference) + 1
    columns = len(hypothesis) + 1

    distance = [
        [0 for _ in range(columns)]
        for _ in range(rows)
    ]

    for i in range(rows):
        distance[i][0] = i

    for j in range(columns):
        distance[0][j] = j

    for i in range(1, rows):
        for j in range(1, columns):

            if reference[i - 1] == hypothesis[j - 1]:
                cost = 0
            else:
                cost = 1

            distance[i][j] = min(
                distance[i - 1][j] + 1,
                distance[i][j - 1] + 1,
                distance[i - 1][j - 1] + cost
            )

    cer = distance[-1][-1] / len(reference)

    return round(cer * 100, 2)


def evaluate_transcription(reference, hypothesis):
    """
    Calculates all evaluation metrics for one transcription.
    """

    return {
        "bleu_score": calculate_bleu(reference, hypothesis),
        "wer": calculate_wer(reference, hypothesis),
        "cer": calculate_cer(reference, hypothesis)
    }


def evaluate_all_models(reference, transcription_results):
    """
    Evaluates transcription results from multiple models.
    """

    evaluated_results = []

    for result in transcription_results:

        if result.get("success"):

            metrics = evaluate_transcription(
                reference,
                result.get("text", "")
            )

            evaluated_results.append({
                **result,
                **metrics
            })

        else:

            evaluated_results.append({
                **result,
                "bleu_score": 0.0,
                "wer": 0.0,
                "cer": 0.0
            })

    return evaluated_results

