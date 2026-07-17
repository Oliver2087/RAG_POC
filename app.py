import os

import pandas as pd
import streamlit as st


if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

if "OPENAI_MODEL" in st.secrets:
    os.environ["OPENAI_MODEL"] = st.secrets["OPENAI_MODEL"]

from orchestrator import process_clinical_text


st.set_page_config(
    page_title="Clinical Extraction POC",
    page_icon="",
    layout="wide",
)


def run_pipeline(text: str) -> None:
    with st.spinner("Running extraction, review, and repair..."):
        record, review, final_record = process_clinical_text(text)

    st.success(f"Review status: {review.status}")

    tab_extract, tab_review, tab_final = st.tabs(
        ["Initial Extract", "Review", "Final Record"]
    )

    with tab_extract:
        st.json(record.model_dump(mode="json"))

    with tab_review:
        st.json(review.model_dump(mode="json"))

    with tab_final:
        st.json(final_record.model_dump(mode="json"))


st.title("Clinical Extraction POC")
st.caption("Extract, review, and repair structured clinical JSON from text.")

input_mode = st.radio(
    "Input type",
    ["Paste text", "Upload CSV"],
    horizontal=True,
)

if input_mode == "Paste text":
    clinical_text = st.text_area(
        "Clinical text",
        height=260,
        placeholder="Paste a discharge summary or clinical note here...",
    )

    if st.button("Run pipeline", type="primary"):
        if not clinical_text.strip():
            st.error("Paste clinical text before running the pipeline.")
        else:
            run_pipeline(clinical_text)

else:
    uploaded_file = st.file_uploader("CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(f"Loaded {len(df)} rows.")

        text_column = st.selectbox("Clinical text column", list(df.columns))
        row_position = st.number_input(
            "Row number",
            min_value=0,
            max_value=max(len(df) - 1, 0),
            value=0,
            step=1,
        )

        with st.expander("Preview selected text"):
            st.write(str(df.iloc[row_position][text_column])[:4000])

        if st.button("Run selected row", type="primary"):
            run_pipeline(str(df.iloc[row_position][text_column]))
