from similarity_engine import calculate_similarity
from drift_detector import detect_topic_drift


topic = "Artificial Intelligence in Healthcare"

sentences = [
    "Artificial intelligence helps doctors diagnose diseases.",
    "Machine learning can analyze medical images.",
    "Cricket is a popular sport in India.",
    "Hospitals can use AI to predict patient risks.",
    "The IPL season attracts millions of viewers."
]


scores = calculate_similarity(topic, sentences)

results = detect_topic_drift(sentences, scores)


print("TOPIC:", topic)
print("=" * 60)

for index, result in enumerate(results, start=1):
    print(f"\nSentence {index}: {result['sentence']}")
    print(f"Similarity Score: {result['similarity_score']}")
    print(f"Classification: {result['classification']}")