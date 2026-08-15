from text_processor import download_nltk_resources, split_into_sentences


download_nltk_resources()

sample_text = """
Artificial intelligence helps doctors diagnose diseases.
Machine learning can analyze medical images.
Cricket is a popular sport in India.
Hospitals can use AI to predict patient risks.
The IPL season attracts millions of viewers.
"""

sentences = split_into_sentences(sample_text)

print("Total sentences:", len(sentences))
print()

for index, sentence in enumerate(sentences, start=1):
    print(f"Sentence {index}: {sentence}")