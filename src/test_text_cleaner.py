from similarity_engine import calculate_similarity
from drift_detector import detect_topic_drift
from text_cleaner import clean_text


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

cleaned_text = clean_text(results)


print("ORIGINAL TEXT")
print("=" * 60)
print(" ".join(sentences))

print("\n" + "=" * 60)
print("CLEANED TEXT")
print("=" * 60)
print(cleaned_text)