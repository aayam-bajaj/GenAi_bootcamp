import io, re, json, base64, requests, time
import streamlit as st
from PIL import Image
import time
import helper_id as helper_id
#st.title("First Gen Ai document Bot")
st.set_page_config(page_title="ID Bot" , layout="wide")
st.title("Student ID -> Name & DOB Extraction")
OLLAMA = st.sidebar.text_input("Ollama Host", "http://localhost:11434").rstrip("/")
MODEL = st.sidebar.text_input("Vision Model", "qwen2.5vl:3b")
temp = st.sidebar.slider("Temperature", 0.0,1.0,0.2,0.1)
prompt_style = st.sidebar.radio("Prompt Style" , ["v1(1)", "v2(2)"])

left, right = st.columns(2, gap="large")

with left:
    up = st.file_uploader("Upload Student ID", type = ["jpg", "jpeg", "png"]) 
    if up:
        img = Image.open(up)
        st.image(img, caption="Uploaded ID", use_container_width=True)
    else:
        st.info("Upload an image of Student ID to extract Name and DOB")

with right:
    st.subheader("Extraction")
    run = st.button("Extract Name & DOB", type="primary", use_container_width=True)
    if run:
        if not up:
            st.warning("Please upload an Image first")
        else:
            prompt = helper_id.make_prompt(prompt_style)
            b64 = helper_id.image_to_base64(img)
            with st.spinner(f"Calling model:{MODEL} via Ollama..."):
                try:
                    t0 = time.time()
                    resp = helper_id.call_ollama(OLLAMA, MODEL, prompt, b64, temp)
                    elapsed = time.time() - t0
                except requests.exceptions.RequestException as e:
                    st.error(str(e))
                    resp, elapsed = "", 0
            if resp:
                st.markdown("**Extracted Information**")
                st.write(f"**{resp}**")
                st.write(f"** Time Taken:{elapsed:.2f} seconds **")
                st.caption(f"Model: `{MODEL}` | Prompt: {prompt_style} | Temperature: `{temp}`")
                    