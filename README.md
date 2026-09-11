# ResumeLens AI

ResumeLens AI is a beginner-friendly Streamlit app that compares a PDF resume with a job description using the Google Gemini API. It returns an overall score, strengths, missing skills, improvement suggestions, and a job description match assessment.

## Setup

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Create a local environment file and add your API key.

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and replace `your_google_ai_studio_key_here` with the API key from Google AI Studio. The default model is `gemma-4-26b-a4b-it`; change `GEMINI_MODEL` if your account uses a different available model.

4. Start the app.

   ```bash
   streamlit run app.py
   ```

## Notes

- Upload a text-based PDF. Scanned image-only PDFs may not contain extractable text.
- The app sends the extracted resume text and job description to Gemini for analysis.
- Never commit `.env` or share your API key. The `.gitignore` file keeps local secrets out of Git.
