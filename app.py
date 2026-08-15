import streamlit as st
import pandas as pd

from src.text_processor import split_into_sentences
from src.similarity_engine import calculate_similarity
from src.drift_detector import detect_topic_drift
from src.text_cleaner import clean_text


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="DriftClean",
    page_icon="🧠",
    layout="wide"
)


# -------------------------------------------------
# PAGE HEADER
# -------------------------------------------------

st.title("🧠 DriftClean")
st.subheader("NLP-Based Topic Drift Detection and Context-Aware Text Filtering")

st.write(
    "Enter a main topic and provide text. DriftClean analyzes each sentence "
    "using semantic similarity, detects topic drift, removes irrelevant "
    "content, and creates a cleaned topic-focused version of the text."
)

st.divider()


# -------------------------------------------------
# USER INPUT
# -------------------------------------------------

topic = st.text_input(
    "Enter the Main Topic",
    placeholder="Example: Artificial Intelligence in Healthcare"
)

text = st.text_area(
    "Paste Your Text",
    placeholder="Paste the text you want DriftClean to analyze...",
    height=250
)


# -------------------------------------------------
# SENSITIVITY SETTINGS
# -------------------------------------------------

st.write("### 🎚️ Drift Detection Sensitivity")

sensitivity = st.selectbox(
    "Choose Sensitivity Level",
    ["Balanced", "Strict", "Lenient"],
    help=(
        "Strict removes more weakly related sentences. "
        "Balanced provides normal filtering. "
        "Lenient keeps more sentences."
    )
)

if sensitivity == "Strict":
    high_threshold = 0.70
    partial_threshold = 0.45

elif sensitivity == "Lenient":
    high_threshold = 0.40
    partial_threshold = 0.20

else:
    high_threshold = 0.50
    partial_threshold = 0.30


st.caption(
    f"Current thresholds → Highly Relevant: ≥ {high_threshold} | "
    f"Partially Relevant: ≥ {partial_threshold} | "
    f"Off Topic: < {partial_threshold}"
)


# -------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------

if st.button("🧠 Analyze and Clean Text", use_container_width=True):

    if not topic or not topic.strip():
        st.warning("Please enter a main topic.")

    elif not text or not text.strip():
        st.warning("Please enter some text to analyze.")

    else:
        with st.spinner("DriftClean is analyzing semantic meaning..."):

            # STEP 1: Sentence tokenization
            sentences = split_into_sentences(text)

            # STEP 2: Semantic similarity
            scores = calculate_similarity(topic, sentences)

            # STEP 3: Topic drift detection
            results = detect_topic_drift(
                sentences,
                scores,
                high_threshold,
                partial_threshold
            )

            # STEP 4: Remove off-topic sentences
            cleaned_text = clean_text(results)


        st.success(
            f"Analysis completed! {len(sentences)} sentences were analyzed "
            f"using {sensitivity} sensitivity."
        )


        # -------------------------------------------------
        # CLEANED TEXT
        # -------------------------------------------------

        st.write("## 🧹 Cleaned Topic-Focused Text")

        if cleaned_text and cleaned_text.strip():

            st.code(cleaned_text, language=None)

            st.download_button(
                label="📥 Download Cleaned Text",
                data=cleaned_text,
                file_name="driftclean_cleaned_text.txt",
                mime="text/plain",
                use_container_width=True
            )

        else:
            st.warning(
                "No relevant sentences were found for the selected topic."
            )

        st.divider()


        # -------------------------------------------------
        # DETAILED ANALYSIS
        # -------------------------------------------------

        st.write("## 📌 Detailed Analysis")
        st.write(f"**Main Topic:** {topic}")
        st.write(f"**Sensitivity Mode:** {sensitivity}")

        st.divider()

        highly_relevant = 0
        partially_relevant = 0
        off_topic = 0


        for index, result in enumerate(results, start=1):

            classification = result["classification"]
            score = result["similarity_score"]
            sentence = result["sentence"]

            if classification == "Highly Relevant":
                highly_relevant += 1
                icon = "🟢"

            elif classification == "Partially Relevant":
                partially_relevant += 1
                icon = "🟡"

            else:
                off_topic += 1
                icon = "🔴"


            st.write(f"### {icon} Sentence {index}")
            st.write(sentence)
            st.write(f"**Similarity Score:** {score}")
            st.write(f"**Classification:** {classification}")

            st.divider()


        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        st.write("## 📊 Summary")

        total_sentences = len(results)

        drift_percentage = (
            off_topic / total_sentences
        ) * 100


        # Determine drift severity
        if drift_percentage <= 20:
            severity = "🟢 Low Drift"

        elif drift_percentage <= 50:
            severity = "🟡 Moderate Drift"

        else:
            severity = "🔴 High Drift"


        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Highly Relevant",
            highly_relevant
        )

        col2.metric(
            "Partially Relevant",
            partially_relevant
        )

        col3.metric(
            "Off Topic",
            off_topic
        )

        col4.metric(
            "Topic Drift",
            f"{drift_percentage:.2f}%"
        )


        # -------------------------------------------------
        # DRIFT SEVERITY
        # -------------------------------------------------

        st.write("### 🚦 Drift Severity")
        st.info(severity)

        st.divider()


        # -------------------------------------------------
        # SIMILARITY SCORE VISUALIZATION
        # -------------------------------------------------

        st.write("## 📈 Sentence Similarity Visualization")

        chart_data = pd.DataFrame({
            "Sentence": [
                f"Sentence {index}"
                for index in range(1, len(results) + 1)
            ],
            "Similarity Score": [
                result["similarity_score"]
                for result in results
            ]
        })

        chart_data = chart_data.set_index("Sentence")

        st.bar_chart(chart_data)