import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from src.similarity_engine import calculate_similarity
from src.drift_detector import detect_topic_drift


def main():

    print("\nLoading evaluation dataset...")

    data = pd.read_csv("data/evaluation_dataset.csv")

    predicted_labels = []
    expected_labels = []
    similarity_scores = []

    print(f"Total evaluation examples: {len(data)}")
    print("Analyzing sentences...\n")


    # -------------------------------------------------
    # ANALYZE DATASET
    # -------------------------------------------------

    for _, row in data.iterrows():

        topic = row["topic"]
        sentence = row["sentence"]
        expected_label = row["expected_label"]

        scores = calculate_similarity(
            topic,
            [sentence]
        )

        results = detect_topic_drift(
            [sentence],
            scores,
            high_threshold=0.50,
            partial_threshold=0.30
        )

        predicted_label = results[0]["classification"]
        similarity_score = results[0]["similarity_score"]

        predicted_labels.append(predicted_label)
        expected_labels.append(expected_label)
        similarity_scores.append(similarity_score)

        print(f"Topic: {topic}")
        print(f"Sentence: {sentence}")
        print(f"Similarity Score: {similarity_score:.4f}")
        print(f"Expected: {expected_label}")
        print(f"Predicted: {predicted_label}")
        print("-" * 60)


    # -------------------------------------------------
    # ADD RESULTS TO DATASET
    # -------------------------------------------------

    data["similarity_score"] = similarity_scores
    data["predicted_label"] = predicted_labels

    data["correct_prediction"] = (
        data["expected_label"] == data["predicted_label"]
    )

    data.to_csv(
        "data/evaluation_results.csv",
        index=False
    )

    print("\nEvaluation predictions saved successfully.")
    print("File: data/evaluation_results.csv")


    # -------------------------------------------------
    # CALCULATE METRICS
    # -------------------------------------------------

    accuracy = accuracy_score(
        expected_labels,
        predicted_labels
    )

    precision = precision_score(
        expected_labels,
        predicted_labels,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        expected_labels,
        predicted_labels,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        expected_labels,
        predicted_labels,
        average="weighted",
        zero_division=0
    )


    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    print("\n")
    print("=" * 60)
    print("DRIFTCLEAN MODEL EVALUATION RESULTS")
    print("=" * 60)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")


    # -------------------------------------------------
    # CLASSIFICATION REPORT
    # -------------------------------------------------

    print("\nCLASSIFICATION REPORT")
    print("=" * 60)

    print(
        classification_report(
            expected_labels,
            predicted_labels,
            zero_division=0
        )
    )


    # -------------------------------------------------
    # CONFUSION MATRIX
    # -------------------------------------------------

    labels = [
        "Highly Relevant",
        "Partially Relevant",
        "Off Topic"
    ]

    matrix = confusion_matrix(
        expected_labels,
        predicted_labels,
        labels=labels
    )

    print("\nCONFUSION MATRIX")
    print("=" * 60)

    print("Labels:")
    print(labels)
    print()

    print(matrix)


if __name__ == "__main__":
    main()