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
st.write("Enter the topic you want to learn about and choose the complexity level. I will then explain it to you at the selected complexity level. You can also choose from example topics or get a random topic.")

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

st.write("Or choose from an example topic:")

# Callback function for example topic buttons
def select_example_topic(topic):
    st.session_state.topic = topic
    st.session_state.generating = True
    st.session_state.explanation = ""

# Callback function for random topic button
def select_random_topic():
    st.session_state.topic = random.choice(topics)
    st.session_state.generating = True
    st.session_state.explanation = ""

# --- Inject CSS for horizontal button layout ---
# This CSS targets the divs Streamlit creates for each button within the first column.
# Adjust margin-right and margin-bottom for spacing.
# Vertical-align helps align the Random button in the second column.
css_button_row = """
<style>
    /* Target containers of example buttons in the first column */
    /* This selector finds divs directly containing a button whose key starts with 'example_topic_' */
    /* Adjust the parent selector if needed based on Streamlit version/structure */
    div[data-testid="stVerticalBlock"] div:has(> button[key^="example_topic_"]) {
        display: inline-block;  /* Arrange buttons like text */
        margin-right: 10px;     /* Space between buttons horizontally */
        margin-bottom: 10px;    /* Space if they wrap */
        vertical-align: top;    /* Align tops */
    }

    /* Target container of the random button in the second column */
    div[data-testid="stVerticalBlock"] div:has(> button[key="random_topic_button"]) {
        display: inline-block;  /* Make it flow like the others */
        vertical-align: top;    /* Align its top with the example buttons */
        /* You might need a slight margin-top adjustment here if alignment isn't perfect */
        /* margin-top: 1px; */ /* Example: Uncomment and adjust if needed */
    }
</style>
"""
st.markdown(css_button_row, unsafe_allow_html=True)


# --- Use Columns for the button row structure ---
# Adjust the ratio [8, 2] as needed for desired spacing around the random button
col_examples, col_random = st.columns([8, 2])

# Retrieve the randomly selected topics
display_topics = st.session_state.example_topics

# --- Place Example Buttons in the First Column ---
# CSS will make them appear horizontally inline
with col_examples:
    if display_topics:
        for i, topic in enumerate(display_topics):
            st.button(
                topic,
                key=f"example_topic_{i}", # Unique key using index
                disabled=st.session_state.generating,
                on_click=select_example_topic, # Use the callback directly
                args=(topic,) # Pass the specific topic to the callback
            )
    else:
        st.write("No example topics available.") # Keep the fallback

# --- Place Random Button in the Second Column ---
# CSS attempts to vertically align it with the first row
with col_random:
    st.button(
        "Random Topic",
        key="random_topic_button",
        disabled=st.session_state.generating,
        on_click=select_random_topic
    )

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