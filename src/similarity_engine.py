from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the pre-trained model
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(topic, sentences):
    """
    Compare the semantic meaning of a topic with multiple sentences.

    Args:
        topic (str): The main topic selected by the user.
        sentences (list): List of sentences to compare with the topic.

    Returns:
        list: Semantic similarity scores for each sentence.
    """

    if not topic or not topic.strip():
        return []

    if not sentences:
        return []

    # Convert topic into a numerical embedding
    topic_embedding = model.encode([topic])

    # Convert all sentences into numerical embeddings
    sentence_embeddings = model.encode(sentences)

    # Calculate cosine similarity between topic and each sentence
    similarity_scores = cosine_similarity(
        topic_embedding,
        sentence_embeddings
    )[0]

    return similarity_scores.tolist()