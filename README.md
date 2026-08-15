# DriftClean

**NLP-Based Topic Drift Detection and Context-Aware Text Filtering**

DriftClean is an NLP-based application designed to detect topic drift in text. Given a main topic and a collection of sentences, the system analyzes the semantic relationship between the topic and each sentence, identifies irrelevant content, and generates a cleaned topic-focused version of the text.

---

## Problem Statement

Large text documents can contain sentences that gradually move away from the intended topic. Traditional keyword-based filtering may fail because two sentences can use different words while having similar meanings.

DriftClean addresses this problem using semantic sentence embeddings and similarity-based classification. Instead of relying only on exact keyword matching, it compares the meaning of a sentence with the meaning of the user-defined topic.

---

## Objectives

- Detect whether sentences remain relevant to a main topic
- Identify topic drift within text
- Use semantic similarity instead of simple keyword matching
- Classify sentences into relevance categories
- Remove off-topic content automatically
- Generate cleaned, topic-focused text
- Provide multiple sensitivity levels
- Evaluate classification performance using standard machine learning metrics

---

## Features

- Sentence Tokenization
- Semantic Text Embeddings
- Cosine Similarity Analysis
- Topic Drift Detection
- Highly Relevant Classification
- Partially Relevant Classification
- Off Topic Detection
- Automatic Text Cleaning
- Strict, Balanced and Lenient Sensitivity Modes
- Topic Drift Percentage
- Drift Severity Classification
- Sentence Similarity Visualization
- Download Cleaned Text
- Model Evaluation
- Accuracy, Precision, Recall and F1-Score
- Confusion Matrix Visualization
- Streamlit Web Interface

---

## How It Works

```text
Input: Topic + User Text
        │
        ▼
Sentence Tokenization
        │
        ▼
Sentence Transformer Model
        │
        ▼
Semantic Embeddings
        │
        ▼
Cosine Similarity Calculation
        │
        ▼
Threshold-Based Classification
   ┌────────────┼─────────────┐
   ▼            ▼             ▼
Highly       Partially      Off Topic
Relevant     Relevant
                              │
                              ▼
                    Topic Drift Detected
                              │
                              ▼
                 Remove Off-Topic Sentences
                              │
                              ▼
                  Cleaned Topic-Focused Text

Technologies Used
Technology	Purpose
Python	Core programming language
NLTK	Sentence tokenization
Sentence Transformers	Semantic sentence embeddings
Scikit-learn	Cosine similarity and evaluation metrics
Pandas	Dataset processing
Matplotlib	Confusion matrix visualization
Streamlit	Interactive web application
Classification Logic

The system uses semantic similarity scores and configurable thresholds.

Balanced Mode

Classification	Similarity Score
Highly Relevant	≥ 0.50
Partially Relevant	≥ 0.30 and < 0.50
Off Topic	< 0.30

Strict Mode

Classification	Similarity Score
Highly Relevant	≥ 0.70
Partially Relevant	≥ 0.45 and < 0.70
Off Topic	< 0.45

Lenient Mode

Classification	Similarity Score
Highly Relevant	≥ 0.40
Partially Relevant	≥ 0.20 and < 0.40
Off Topic	< 0.20
Topic Drift Severity

Topic drift is calculated as:

Topic Drift Percentage =
(Number of Off-Topic Sentences / Total Number of Sentences) × 100
Drift Percentage	Severity
0%–20%	Low Drift
>20%–50%	Moderate Drift
>50%	High Drift
Model Evaluation

The model was evaluated using an 18-example labelled dataset containing three domains:

Artificial Intelligence in Healthcare
Climate Change and Global Warming
Cybersecurity and Data Protection

Evaluation Results

Metric	Score
Accuracy	83.33%
Precision	86.90%
Recall	83.33%
F1 Score	84.04%

The evaluation showed strong performance in identifying clearly off-topic sentences. The partially relevant category was more challenging because these sentences lie close to the semantic boundary between relevant and irrelevant content.

Project Structure
DriftClean/
│
├── data/
│   ├── evaluation_dataset.csv
│   ├── evaluation_results.csv
│   └── confusion_matrix.png
│
├── src/
│   ├── __init__.py
│   ├── text_processor.py
│   ├── similarity_engine.py
│   ├── drift_detector.py
│   ├── text_cleaner.py
│   ├── evaluate_model.py
│   ├── plot_evaluation.py
│   └── test files...
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
Installation

Clone the repository:

git clone YOUR_REPOSITORY_URL

Move into the project directory:

cd DriftClean

Create a virtual environment:

py -3.12 -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py
Model Evaluation

Run:

python -m src.evaluate_model

This generates:

data/evaluation_results.csv
Confusion Matrix

Run:

python -m src.plot_evaluation

This generates:

data/confusion_matrix.png
Future Enhancements
Automatic topic extraction
Multi-topic detection
Paragraph-level drift detection
Custom threshold selection
Larger evaluation datasets
Multilingual topic drift detection
Improved classification of partially relevant sentences
Project

DriftClean was developed as an NLP project demonstrating semantic similarity, sentence embeddings, topic drift detection, context-aware text filtering, and model evaluation.