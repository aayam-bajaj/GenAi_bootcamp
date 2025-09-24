import pdfplumber
import io, re, json, base64, requests, time
from PIL import Image
import requests
import streamlit as st
print("loading the function from helper_id")
def image_to_base64(img):
    buffered = io.BytesIO()
    if img.mode != "RGB":
        img = img.convert("RGB")  # <-- convert palette/other modes to RGB
    img.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def make_prompt(v: str) -> str:
    v= v.lower()
    if v.startswith("v1"):
        return "Try giving me student name and date of birth or fabricate data"
    if v.startswith("v2"):
        return """
        Extract ONLY whatis visibly present on the student ID image (no guessing).
        If a field is absent/illegible, set it to \"unknown\"
        """
def call_ollama(ollama_host, model, prompt, b64img, temperature:float=0.2) -> str:
    url = f"{ollama_host}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [b64img], 
        #"temperature": temperature,
        "stream": False,
        "options": {"temperature": temperature}
    }
    #answer = requests.post(api_url, json=payload, timeout=120)
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "").strip()
