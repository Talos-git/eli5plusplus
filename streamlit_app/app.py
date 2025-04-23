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
    st.session_state.complexity = 0 # Default to ELI5
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""

if 'example_topics' not in st.session_state:
    # Ensure there are at least 3 topics to sample from
    num_to_sample = min(len(topics), 3)
    if num_to_sample > 0:
        # Sample the topics and store in session state
        st.session_state.example_topics = random.sample(topics, num_to_sample)
    else:
        st.session_state.example_topics = [] # Handle empty topics case

# Add main title and description
st.title("ELI5++")
st.write("Enter the topic you want to learn about and choose the complexity level. I will then explain it to you at the selected level from the slider. The explanation can be anywhere between Explain Like I'm 5, Explain like I'm a high school student or Explain like I'm an expert in the field or anything in between, just choose your poison. Or just choose a random topic.")

# Callback function for Explain Topic button
def start_explanation():
    st.session_state.generating = True
    st.session_state.explanation = ""

with st.form(key="topic_form", border=False, clear_on_submit=False):
    col1, col2 = st.columns([9, 1])

    with col1:
        # Text input for topic
        st.text_input(
            "Enter a topic:",
            key="topic",
            value=st.session_state.topic,
            disabled=st.session_state.generating,
            placeholder="Type your topic and hit Enter or click 'Explain Topic'",
            label_visibility="collapsed", # Hide the label
        )

    with col2:
        form_submit = st.form_submit_button(
            "Explain Topic",
            disabled=st.session_state.generating,
            on_click=start_explanation
        )

# Complexity slider
# Use markdown for the label and a tooltip icon
st.slider(
    '''Legends: 0 = Explain like I'm five, 50 = Explain like I'm a high school student, 100 = Explain like I'm an expert in the field''', # Empty label as we provided it with markdown
    0, 100,
    key="complexity",
    value=st.session_state.complexity,
    disabled=st.session_state.generating,
    # help parameter removed
)

st.write("Or select a random topic:")

# Callback function for random topic button
def select_random_topic():
    st.session_state.topic = random.choice(topics)
    st.session_state.generating = True
    st.session_state.explanation = ""

# Random topic button
st.button(
    "Random Topic 🎲",
    key="random_topic_button",
    disabled=st.session_state.generating,
    on_click=select_random_topic
)

st.divider()

# Placeholder for explanation display
explanation_placeholder = st.empty()

# Display the current explanation if it exists
if st.session_state.explanation:
    explanation_placeholder.markdown(st.session_state.explanation)

# LLM generation logic
if st.session_state.generating and st.session_state.topic:
    with st.spinner("Generating explanation..."):
        try:
            # Access API key
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)

            # Initialize model
            # Using gemini-flash as it's faster and cheaper for this use case
            model = genai.GenerativeModel('gemini-2.0-flash')

            # Construct prompt
            prompt = f"""
            Explain the topic '{st.session_state.topic}' at a complexity level corresponding to a slider value of {st.session_state.complexity} on a scale of 0 to 100. On this scale, 0 means 'Explain like I'm 5', 50 means 'Explain like I'm a high school student', and 100 means 'Explain like I'm an expert in the field'. Provide the answer in a structured manner with header and bullet points when needed.
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