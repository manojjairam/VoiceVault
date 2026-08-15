from similarity_engine import calculate_similarity


topic = "Artificial Intelligence in Healthcare"

sentences = [
    "Artificial intelligence helps doctors diagnose diseases.",
    "Machine learning can analyze medical images.",
    "Cricket is a popular sport in India.",
    "Hospitals can use AI to predict patient risks.",
    "The IPL season attracts millions of viewers."
]


scores = calculate_similarity(topic, sentences)


print("Topic:", topic)
print()

for index, (sentence, score) in enumerate(
    zip(sentences, scores),
    start=1
):
    print(f"Sentence {index}: {sentence}")
    print(f"Similarity Score: {score:.4f}")
    print()