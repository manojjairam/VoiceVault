# 🧠 VoiceVault

> **NLP-Based Topic Drift Detection and Context-Aware Text Filtering**

VoiceVault is an NLP-based application that detects when text moves away from its intended topic. Given a **main topic** and **user-provided text**, the system analyzes each sentence using semantic similarity, identifies topic drift, classifies relevance, and generates a cleaned topic-focused version of the text.

---

## 📌 Problem Statement

Large documents can contain sentences that gradually move away from the intended subject. Traditional keyword-based filtering may fail because two sentences can use different words while expressing similar meanings.

VoiceVault addresses this problem using **semantic sentence embeddings**. Instead of relying only on exact keyword matching, it compares the meaning of each sentence with the meaning of the user-defined topic.

---

## 🎯 Objectives

- Detect whether sentences remain relevant to a main topic
- Identify topic drift within text
- Use semantic similarity instead of simple keyword matching
- Classify sentences into relevance categories
- Remove off-topic content automatically
- Generate cleaned, topic-focused text
- Provide multiple sensitivity levels
- Evaluate classification performance using standard machine learning metrics

---

## ✨ Key Features

| Feature | Description |
|---|---|
| Sentence Tokenization | Splits input text into individual sentences |
| Semantic Embeddings | Converts topics and sentences into semantic vector representations |
| Cosine Similarity | Measures semantic similarity between the topic and each sentence |
| Topic Drift Detection | Identifies sentences that move away from the main topic |
| Relevance Classification | Classifies sentences as Highly Relevant, Partially Relevant, or Off Topic |
| Automatic Text Cleaning | Removes off-topic sentences automatically |
| Sensitivity Modes | Supports Strict, Balanced, and Lenient modes |
| Drift Percentage | Calculates the percentage of off-topic content |
| Drift Severity | Categorizes drift as Low, Moderate, or High |
| Download Cleaned Text | Allows the cleaned result to be downloaded |
| Model Evaluation | Calculates Accuracy, Precision, Recall, and F1 Score |
| Confusion Matrix | Visualizes classification performance |
| Streamlit Interface | Provides an interactive web application |

---

## ⚙️ How It Works

```text
Topic + User Text
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
Cosine Similarity
        │
        ▼
Threshold-Based Classification
   ┌───────┼────────┐
   ▼       ▼        ▼
Highly   Partially  Off
Relevant Relevant   Topic
                    │
                    ▼
          Topic Drift Detected
                    │
                    ▼
       Remove Off-Topic Sentences
                    │
                    ▼
       Cleaned Topic-Focused Text
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| NLTK | Sentence tokenization |
| Sentence Transformers | Semantic sentence embeddings |
| Scikit-learn | Cosine similarity and evaluation metrics |
| Pandas | Dataset processing |
| Matplotlib | Confusion matrix visualization |
| Streamlit | Interactive web application |

---

## 🧠 Classification Logic

VoiceVault compares the semantic similarity between the **main topic** and each **individual sentence**. Classification thresholds can be adjusted using three sensitivity modes.

### Balanced Mode

| Classification | Similarity Score |
|---|---:|
| 🟢 Highly Relevant | ≥ 0.50 |
| 🟡 Partially Relevant | ≥ 0.30 and < 0.50 |
| 🔴 Off Topic | < 0.30 |

### Strict Mode

| Classification | Similarity Score |
|---|---:|
| 🟢 Highly Relevant | ≥ 0.70 |
| 🟡 Partially Relevant | ≥ 0.45 and < 0.70 |
| 🔴 Off Topic | < 0.45 |

### Lenient Mode

| Classification | Similarity Score |
|---|---:|
| 🟢 Highly Relevant | ≥ 0.40 |
| 🟡 Partially Relevant | ≥ 0.20 and < 0.40 |
| 🔴 Off Topic | < 0.20 |

---

## 📊 Topic Drift Severity

**Formula**

```text
Topic Drift Percentage =
(Number of Off-Topic Sentences / Total Number of Sentences) × 100
```

| Drift Percentage | Severity |
|---|---|
| 0% – 20% | 🟢 Low Drift |
| >20% – 50% | 🟡 Moderate Drift |
| >50% | 🔴 High Drift |

---

## 🧪 Model Evaluation

The model was evaluated using an **18-example labelled dataset** across three domains:

- Artificial Intelligence in Healthcare
- Climate Change and Global Warming
- Cybersecurity and Data Protection

### Results

| Metric | Score |
|---|---:|
| **Accuracy** | **83.33%** |
| **Precision** | **86.90%** |
| **Recall** | **83.33%** |
| **F1 Score** | **84.04%** |

The evaluation showed strong performance in identifying clearly off-topic sentences. The **Partially Relevant** category was more challenging because these sentences lie close to the semantic boundary between relevant and irrelevant content.

---

## 📁 Project Structure

```text
VoiceVault/
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
```

---

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd VoiceVault
```

### 3. Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

### 4. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 6. Run the Application

```powershell
streamlit run app.py
```

The application will open in your browser.

---

## 🧪 Run Model Evaluation

```powershell
python -m src.evaluate_model
```

This generates:

```text
data/evaluation_results.csv
```

---

## 📈 Generate the Confusion Matrix

```powershell
python -m src.plot_evaluation
```

This generates:

```text
data/confusion_matrix.png
```

---

## 🔮 Future Enhancements

- Automatic topic extraction
- Multi-topic detection
- Paragraph-level drift detection
- User-defined classification thresholds
- Larger evaluation datasets
- Multilingual topic drift detection
- Improved classification of partially relevant sentences
- Additional semantic similarity visualizations

---

## 👨‍💻 Project Summary

VoiceVault demonstrates how modern NLP techniques can be used for:

- Semantic similarity
- Sentence embeddings
- Topic drift detection
- Context-aware text filtering
- Sentence relevance classification
- Automatic text cleaning
- Model evaluation

Instead of relying only on keyword matching, VoiceVault focuses on understanding the **semantic meaning and context** of text.


