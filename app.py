"""ResumeLens AI: a beginner-friendly resume and job description reviewer."""

import json
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


load_dotenv()

APP_TITLE = "ResumeLens AI"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")


def extract_resume_text(uploaded_file: Any) -> str:
    """Extract text from every page in an uploaded PDF."""
    reader = PdfReader(uploaded_file)
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(page for page in pages if page).strip()


def parse_review(response_text: str) -> dict[str, Any]:
    """Parse the model's JSON response and provide a useful error for bad output."""
    cleaned = response_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    result = json.loads(cleaned)
    if not isinstance(result, dict):
        raise ValueError("The model returned an unexpected review format.")
    return result


def request_review(resume_text: str, job_description: str) -> dict[str, Any]:
    """Ask Gemini for a structured resume review."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Add your Google AI Studio key to .env.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=(
            "Act as a resume coach. Compare the resume with the job description. "
            "Return only JSON with score (0-100), strengths, missing_skills, suggestions, "
            "and jd_match. jd_match must contain assessment, matched_skills, and gaps. "
            "Use arrays of strings and do not invent experience.\n\n"
            f"RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"
        ),
    )
    content = response.text
    if not content:
        raise ValueError("Gemini returned an empty review.")
    return parse_review(content)


def list_items(items: Any, empty_message: str = "No items reported.") -> None:
    """Render a model-generated list safely."""
    if isinstance(items, list) and items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption(empty_message)


def render_review(review: dict[str, Any]) -> None:
    """Render the structured review in a scannable layout."""
    score = review.get("score", 0)
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        score = 0

    st.subheader("Your resume score")
    score_col, summary_col = st.columns([1, 2])
    with score_col:
        st.metric("Overall score", f"{score}/100")
        st.progress(score / 100)
    with summary_col:
        st.markdown("**Job description match**")
        jd_match = review.get("jd_match", {})
        if isinstance(jd_match, dict):
            st.write(jd_match.get("assessment", "No assessment returned."))
        else:
            st.write(str(jd_match))

    strengths_col, skills_col = st.columns(2)
    with strengths_col:
        with st.container(border=True):
            st.markdown("### Strengths")
            list_items(review.get("strengths"))
    with skills_col:
        with st.container(border=True):
            st.markdown("### Missing skills")
            list_items(review.get("missing_skills"))

    st.markdown("### Improvement suggestions")
    list_items(review.get("suggestions"))

    if isinstance(jd_match, dict):
        matched_col, gaps_col = st.columns(2)
        with matched_col:
            st.markdown("**Matched skills**")
            list_items(jd_match.get("matched_skills"))
        with gaps_col:
            st.markdown("**Job description gaps**")
            list_items(jd_match.get("gaps"))


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="centered")
    st.markdown(
        """
        <style>
        .block-container { max-width: 900px; padding-top: 3rem; }
        h1 { letter-spacing: -0.02em; }
        .subtitle { color: #5f6b7a; font-size: 1.05rem; margin-top: -0.7rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title(APP_TITLE)
    st.markdown(
        '<p class="subtitle">A clear, practical read on how your resume fits a role.</p>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.subheader("How it works")
        st.markdown("1. Upload a PDF resume.\n2. Paste the job description.\n3. Get focused feedback.")
        st.caption("Your API key stays in your local environment and is never shown in the app.")

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
    job_description = st.text_area(
        "Paste the job description",
        height=260,
        placeholder="Paste the complete job description here...",
    )

    review_clicked = st.button("Analyze resume", type="primary", use_container_width=True)
    if not review_clicked:
        return
    if uploaded_file is None:
        st.error("Please upload a PDF resume first.")
        return
    if not job_description.strip():
        st.error("Please paste a job description first.")
        return

    try:
        with st.spinner("Reading your resume and preparing feedback..."):
            resume_text = extract_resume_text(uploaded_file)
            if not resume_text:
                raise ValueError("No selectable text was found in this PDF. Try a text-based PDF.")
            review = request_review(resume_text, job_description.strip())
        st.divider()
        render_review(review)
    except Exception as error:
        st.error(f"We could not complete the review: {error}")


if __name__ == "__main__":
    main()
