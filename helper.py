import pdfplumber
import requests
import streamlit as st
import json
def read_pdf_text(uploaded_file):
    parts = []
    print(parts)
    with pdfplumber.open(uploaded_file) as pdf:
        st.write("Loading the Library")
        for page in pdf.pages:
            st.write(f"Page:{page}")
            extracted_text = page.extract_text()
            parts.append(extracted_text)

    return "\n\n".join(parts).strip()

def make_prompt(version, question, content):
    if version.startswith("v1"):
        return f""" Answer the question based on the content provided. Guess if needed.
        Question: {question}
        Content: {content}
        """
    if version.startswith("v2"):
        return f""" Answer ONLY if you can cite a phrase from the document provided. If not present, reply exactly, "Not found in document".
        Question: {question}
        Content: {content}
        """
def call_ollama(ollama_server, model, prompt, temperature, max_tokens=512):
    api_url = f"{ollama_server}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        #"temperature": temperature,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens}
    }
    #answer = requests.post(api_url, json=payload, timeout=120)
    answer = requests.post(api_url, json=payload, timeout=120)
    print(answer)
    answer.raise_for_status()
    return(answer.json().get("response") or "").strip()
def call_openrouter(api_key, model, prompt, temp):
    """
    Sends a request to the OpenRouter API and returns the model's response.
    """
    if not api_key:
        return "Error: OpenRouter API key is missing. Please add it in the sidebar."

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temp,
            }),
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"API Call Error (OpenRouter): {e}"
    except (KeyError, IndexError):
        return f"Error: Could not parse response from OpenRouter. Response: {response.text}"


