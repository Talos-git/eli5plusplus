# Project Plan: ELI5++ Streamlit App

**Goal:** Create a simple Streamlit web application that generates LLM-powered explanations tailored to a user-selected complexity level, with random and example topics also setting a default complexity, streaming responses, disabled inputs during generation, markdown output, and responsiveness.

**Steps:**

1.  **Project Setup:**
    *   Create a new subdirectory named `streamlit_app` in the workspace root.
    *   Create a Python file named `topics.py` inside `streamlit_app` to store the list of example topics.
    *   Create the main Streamlit application file named `app.py` inside `streamlit_app`.
    *   Create a `requirements.txt` file in the workspace root to list necessary Python packages (streamlit, google-generativeai).

2.  **Define Example Topics (`streamlit_app/topics.py`):**
    *   Create a Python list containing strings of example topics.

3.  **Develop the Streamlit Application (`streamlit_app/app.py`):**
    *   Import necessary libraries (`streamlit`, `google.generativeai`, `random`, `json` - if using JSON for secrets, or just `os` if using environment variables, but `st.secrets` is preferred).
    *   Import the `topics` list from `topics.py`.
    *   Configure the Streamlit page (title, layout). Streamlit applications are generally responsive by default, adapting to different screen sizes, including mobile.
    *   Initialize Streamlit session state variables:
        *   `st.session_state.topic`: Stores the current topic input (default: empty string).
        *   `st.session_state.complexity`: Stores the current slider value (default: 50).
        *   `st.session_state.generating`: Boolean to indicate if an explanation is being generated (default: `False`).
        *   `st.session_state.explanation`: Stores the generated explanation (default: empty string).
    *   Add the main title and description for the app.
    *   Create the text input field for the user to enter a topic, linked to `st.session_state.topic`. Set the `disabled` parameter based on `st.session_state.generating`.
    *   Create the complexity slider (`st.slider`) with a range from 0 to 100, linked to `st.session_state.complexity`. Add labels or captions to indicate the complexity extremes ("Simple" / "Expert"). Set the `disabled` parameter based on `st.session_state.generating`.
    *   Implement a function to map the slider value (0-100) to a descriptive complexity string based on the mapping: 0="Explain like I'm 5", 50="Explain like I'm a high school student", 100="Explain like I'm an expert in the field". This function will be used to help construct the prompt.
    *   Create a section for example topics:
        *   Use `st.columns` to arrange example topic buttons horizontally.
        *   For each example topic, create a `st.button`. Set the `disabled` parameter based on `st.session_state.generating`.
        *   When an example button is clicked, update `st.session_state.topic` with the example topic *and* set `st.session_state.complexity` to 50. Rerun the app to update the inputs.
    *   Create the "Random Topic" button: Set the `disabled` parameter based on `st.session_state.generating`.
        *   When clicked, select a random topic from the `topics` list.
        *   Update `st.session_state.topic` with the random topic *and* set `st.session_state.complexity` to 50. Rerun the app to update the inputs.
    *   Create the "Explain Topic" button. Set the `disabled` parameter based on `st.session_state.generating`.
    *   Add a placeholder or empty container (`st.empty()`) where the explanation will be displayed.
    *   Implement the logic triggered by the "Explain Topic" button:
        *   Set `st.session_state.generating` to `True` and rerun the app to disable inputs.
        *   Get the current topic from `st.session_state.topic`.
        *   Get the current slider value from `st.session_state.complexity`.
        *   Construct the prompt string. The prompt will explicitly mention the slider value and the anchor points to guide the LLM on the desired complexity.
            *   **Prompt Construction Detail:** The prompt will look something like this:
                ```
                "Explain the topic '{topic}' at a complexity level corresponding to a slider value of {slider_value} on a scale of 0 to 100. On this scale, 0 means 'Explain like I'm 5', 50 means 'Explain like I'm a high school student', and 100 means 'Explain like I'm an expert in the field'. Provide the explanation in markdown format."
                ```
                This approach uses the slider value directly in the prompt, along with the context of the scale and its anchor points, allowing the LLM to interpret the desired complexity level more effectively than just a single descriptive phrase derived from the slider value.
        *   Display a loading spinner (`st.spinner`) while waiting for the API response.
        *   Access the Gemini API key using `st.secrets["GEMINI_API_KEY"]`.
        *   Initialize the Google Generative AI client.
        *   Call the Gemini model (`gemini-pro` or `gemini-flash`) with the constructed prompt, setting `stream=True`.
        *   Iterate through the streamed response chunks and append them to `st.session_state.explanation`. Update the display area with the accumulating explanation using `st.markdown`. **Ensure `st.markdown` is used here to render the output with markdown formatting.**
        *   Handle potential errors during the API call.
        *   Once the streaming is complete, set `st.session_state.generating` to `False` and rerun the app to re-enable inputs.

4.  **API Key Management:**
    *   Instruct the user on how to add their `GEMINI_API_KEY` to Streamlit Secrets (`.streamlit/secrets.toml`).

5.  **Running the Application:**
    *   Provide instructions on how to install the required packages (`pip install -r requirements.txt`).
    *   Provide the command to run the Streamlit application (`streamlit run streamlit_app/app.py`).

**Mermaid Diagram:**

```mermaid
graph TD A[User Input Topic & Complexity (Session State)] --> B{Explain Topic Button Clicked?} A --> C{Random Topic Button Clicked?} A --> D{Example Topic Button Clicked?} B --> E[Set Generating = True] E --> F[Rerun App (Inputs Disabled)] F --> G[Get Topic & Slider Value from Session State] G --> H[Construct LLM Prompt (using Slider Value & Scale Context)] H --> I[Display Loading Spinner] I --> J[Call Gemini API with Prompt (stream=True)] J --> K{Streamed Response Chunks} K --> L[Append to Explanation in Session State] L --> M[Update Display Area (using st.markdown)] K -- End of Stream --> N[Set Generating = False] N --> O[Rerun App (Inputs Enabled)] C --> P[Select Random Topic] P --> Q[Update Topic & Complexity in Session State] Q --> O D --> R[Get Example Topic] R --> Q M --> P_end[Explanation Displayed] O --> A subgraph Files topics.py app.py requirements.txt .streamlit/secrets.toml end app.py --> topics.py app.py --> .streamlit/secrets.toml requirements.txt --> app.py