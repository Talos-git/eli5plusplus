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

# Callback function for Explain Topic button
def start_explanation():
    st.session_state.generating = True
    st.session_state.explanation = ""
    # No need for st.rerun() here, modifying session state will trigger it

col1, col2 = st.columns([9, 1])

with col1:
    # Text input for topic
    st.text_input(
        "Enter a topic:",
        key="topic",
        value=st.session_state.topic,
        disabled=st.session_state.generating,
        # Removed on_change as it conflicts with button logic
    )

with col2:
    # Explain Topic button
    st.write("") # Add vertical space for alignment
    st.write("") # Add vertical space for alignment
    st.button(
        "Explain Topic",
        key="explain_topic_button",
        disabled=st.session_state.generating or not st.session_state.topic,
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

# Callback function for example topic buttons
def select_example_topic(topic):
    st.session_state.topic = topic
    st.session_state.generating = True
    st.session_state.explanation = ""
    # Removed st.rerun() as it's a no-op in callbacks

# Callback function for random topic button
def select_random_topic():
    st.session_state.topic = random.choice(topics)
    st.session_state.generating = True
    st.session_state.explanation = ""
    # Removed st.rerun() as it's a no-op in callbacks

# Example Topics and Random Topic buttons
st.write("Or choose from an example topic:")

# Use columns for example topics
cols = st.columns(len(topics))
for i, topic in enumerate(topics):
    cols[i].button(
        topic,
        key=topic, # Use the topic string as the unique key
        disabled=st.session_state.generating,
        on_click=select_example_topic,
        args=(topic,) # Pass the topic to the callback
    )

# Random Topic button
st.button(
    "Random Topic",
    key="random_topic_button", # Add a unique key
    disabled=st.session_state.generating,
    on_click=select_random_topic
)

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