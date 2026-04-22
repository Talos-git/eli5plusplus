# eli5plusplus

Streamlit app for generating explanations at different complexity levels using Gemini.

## Prerequisites

- `uv`
- Python 3.13
- `GEMINI_API_KEY` set in your environment

## Getting Started

```bash
uv sync
uv run streamlit run streamlit_app/app.py
```

## Docker

The container image installs dependencies with `uv` and starts the app with:

```bash
uv run streamlit run streamlit_app/app.py --server.port=8080 --server.address=0.0.0.0
```
