import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix


def main():

    # Load evaluation results
    data = pd.read_csv("data/evaluation_results.csv")

    expected = data["expected_label"]
    predicted = data["predicted_label"]

    labels = [
        "Highly Relevant",
        "Partially Relevant",
        "Off Topic"
    ]

    matrix = confusion_matrix(
        expected,
        predicted,
        labels=labels
    )


    # Create figure
    plt.figure(figsize=(8, 6))

    plt.imshow(matrix)

    plt.title("DriftClean Confusion Matrix")

    plt.colorbar()

    plt.xticks(
        range(len(labels)),
        labels,
        rotation=25
    )

    plt.yticks(
        range(len(labels)),
        labels
    )

    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")


    # Add values to matrix
    for row in range(len(labels)):
        for column in range(len(labels)):

            plt.text(
                column,
                row,
                matrix[row, column],
                ha="center",
                va="center"
            )


    plt.tight_layout()

    plt.savefig(
        "data/confusion_matrix.png",
        dpi=300
    )

    plt.show()

    print(
        "\nConfusion matrix saved successfully:"
    )

    print(
        "data/confusion_matrix.png"
    )


if __name__ == "__main__":
    main()