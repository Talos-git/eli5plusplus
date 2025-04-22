import streamlit as st
import google.generativeai as genai
import random
import os # Keep os import for potential environment variable fallback, though st.secrets is preferred

from topics import topics

# Configure Streamlit page
st.set_page_config(page_title="ELI5++", layout="wide")

# Initialize Streamlit session state variables
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'complexity' not in st.session_state:
    st.session_state.complexity = 50 # Default to high school level
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""

# Add main title and description
st.title("ELI5++")
st.write("Get explanations for complex topics tailored to your desired complexity level.")

# Text input for topic
st.text_input(
    "Enter a topic:",
    key="topic",
    value=st.session_state.topic,
    disabled=st.session_state.generating,
    # Removed on_change as it conflicts with button logic
)

# Complexity slider
st.slider(
    "Select Complexity Level:",
    0, 100,
    key="complexity",
    value=st.session_state.complexity,
    disabled=st.session_state.generating,
    help="0: Explain like I'm 5, 50: High School Student, 100: Expert"
)

# Example Topics and Random Topic buttons
st.write("Or choose from an example topic:")

# Use columns for example topics
cols = st.columns(len(topics))
for i, topic in enumerate(topics):
    if cols[i].button(topic, disabled=st.session_state.generating):
        st.session_state.topic = topic
        st.session_state.complexity = 50 # Set complexity to default for examples
        st.rerun()

# Random Topic button
if st.button("Random Topic", disabled=st.session_state.generating):
    st.session_state.topic = random.choice(topics)
    st.session_state.complexity = 50 # Set complexity to default for random topic
    st.rerun()

# Explain Topic button
if st.button("Explain Topic", disabled=st.session_state.generating or not st.session_state.topic):
    st.session_state.generating = True
    st.session_state.explanation = "" # Clear previous explanation
    st.rerun() # Rerun to disable inputs and show spinner

# Placeholder for explanation display
explanation_placeholder = st.empty()

# Display the current explanation if it exists
if st.session_state.explanation:
    explanation_placeholder.markdown(st.session_state.explanation)

# Function to map slider value to complexity description (not strictly needed for prompt but good for context)
def map_complexity_value_to_description(value):
    if value <= 25:
        return "Explain like I'm 5"
    elif value <= 75:
        return "Explain like I'm a high school student"
    else:
        return "Explain like I'm an expert in the field"

# LLM generation logic
if st.session_state.generating and st.session_state.topic:
    with st.spinner("Generating explanation..."):
        try:
            # Access API key
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)

            # Initialize model
            # Using gemini-flash as it's faster and cheaper for this use case
            model = genai.GenerativeModel('gemini-flash-1.5-latest')

            # Construct prompt
            prompt = f"""
            Explain the topic '{st.session_state.topic}' at a complexity level corresponding to a slider value of {st.session_state.complexity} on a scale of 0 to 100. On this scale, 0 means 'Explain like I'm 5', 50 means 'Explain like I'm a high school student', and 100 means 'Explain like I'm an expert in the field'. Provide the explanation in markdown format.
            """

            # Stream response
            response = model.generate_content(prompt, stream=True)

            # Iterate and display streamed chunks
            full_explanation = ""
            for chunk in response:
                if chunk.text:
                    full_explanation += chunk.text
                    explanation_placeholder.markdown(full_explanation)

            st.session_state.explanation = full_explanation # Store the final explanation
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.explanation = f"Error generating explanation: {e}" # Store error message
            explanation_placeholder.markdown(st.session_state.explanation)
        finally:
            st.session_state.generating = False
            st.rerun() # Rerun to re-enable inputs