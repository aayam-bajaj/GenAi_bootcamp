import streamlit as st
import time
import helper as helper

# Set the page configuration for a wider layout
st.set_page_config(layout="wide")

# --- Sidebar Configuration ---
st.sidebar.title("Configuration")

# Dropdown to select the API service
api_service = st.sidebar.selectbox(
    "Choose API Service",
    ["Ollama", "OpenRouter"],
    help="Select Ollama for local models or OpenRouter for cloud models."
)

# Dynamically display inputs based on the selected service
if api_service == "Ollama":
    # Inputs for the local Ollama service
    OLLAMA_SERVER = st.sidebar.text_input("Ollama Server", "http://localhost:11434")
    MODEL = st.sidebar.text_input("Model", "gemma:2b")
    OPENROUTER_KEY = None
else:  # OpenRouter is selected
    # Input for the OpenRouter API Key (using password type for security)
    OPENROUTER_KEY = st.sidebar.text_input(
        "OpenRouter API Key",
        type="password",
        help="Get your free key from https://openrouter.ai/keys"
    )
    # Default to the Grok fast model, but allow user to change
    MODEL = st.sidebar.text_input("Model", "x-ai/grok-4-fast:free")
    OLLAMA_SERVER = None

# Common configuration options
temp = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.1, help="Controls the creativity of the model.")
prompt_style = st.sidebar.radio("Prompt Style", ["v1(1)", "v2(2)"])


# --- Main Application Layout ---
left, right = st.columns(2, gap="large")

# Left column for PDF upload and display
with left:
    st.title("PDF -> ASK -> ANSWER")
    st.markdown("Upload a PDF document and ask questions about its content.")
    up = st.file_uploader("Upload PDF", type=["pdf"])
    
    extracted_text = ""
    if up:
        extracted_text = helper.read_pdf_text(up)
        st.success(f"PDF Uploaded Successfully. Character count: {len(extracted_text)}")
        # Show the extracted text in an expander
        with st.expander("View Extracted PDF Text"):
            st.write(extracted_text)

# Right column for Q&A interaction
with right:
    st.subheader("Ask Your Question")
    q = st.text_input("Question", placeholder="Ask about the content of the uploaded document")
    
    if st.button("Ask PDF", type="primary", use_container_width=True):
        # --- Input Validation ---
        if not up:
            st.warning("Please upload a PDF document first.")
        elif not q.strip():
            st.warning("Please enter a question to ask.")
        elif api_service == "OpenRouter" and not OPENROUTER_KEY:
            st.warning("Please enter your OpenRouter API Key in the sidebar.")
        else:
            # --- Prompt Generation and API Call ---
            prompt = helper.make_prompt(prompt_style, q, extracted_text)

            with st.spinner(f"Calling model: `{MODEL}` via `{api_service}`..."):
                t0 = time.time()
                ans = ""
                # Call the appropriate function based on service selection
                if api_service == "Ollama":
                    ans = helper.call_ollama(OLLAMA_SERVER, MODEL, prompt, temp)
                else:  # OpenRouter
                    ans = helper.call_openrouter(OPENROUTER_KEY, MODEL, prompt, temp)
                
                elapsed = time.time() - t0
                
                # Display the answer and performance stats
                st.write(ans)
                st.info(f"**Time Taken: {elapsed:.2f} seconds**")

                # Show the exact prompt used in an expander for debugging
                with st.expander("View Full Prompt Sent to Model"):
                    st.write(prompt)


