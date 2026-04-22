# Use a lightweight Python image as the base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.8 /uv /uvx /bin/

# Copy project metadata and install dependencies
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Copy the Streamlit application files
COPY streamlit_app/ ./streamlit_app/

# Expose the port Streamlit runs on
EXPOSE 8080

# Command to run the Stream Streamlit app
CMD ["uv", "run", "streamlit", "run", "streamlit_app/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
