# Use a lightweight Python image as the base
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application files
COPY streamlit_app/ ./streamlit_app/

# Expose the port Streamlit runs on
EXPOSE 8080

# Command to run the Stream Streamlit app
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port=8080", "--server.address=0.0.0.0"]