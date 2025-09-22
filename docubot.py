import streamlit as st
import time
import helper as helper
#st.title("First Gen Ai document Bot")
st.set_page_config(layout="wide")
OLLAMA = st.sidebar.text_input("Ollama Server", "http://localhost:11434")
MODEL = st.sidebar.text_input("Model", "gemma3:1b")
temp = st.sidebar.slider("Temperature", 0.0,1.0,0.2,0.1)
prompt_style = st.sidebar.radio("Prompt Style" , ["v1(1)"])

left, right = st.columns(2, gap="large")

with left:
    st.title("PDF -> ASK -> ANSWER")
    up = st.file_uploader("PDF Upload", type = ["pdf"]) 
    if up:
        extracted_text = helper.read_pdf_text(up)
        st.success(f"PDF Uploaded Successfully, Length:{len(extracted_text)}")
        with st.expander("PDF Text"):
            st.write(extracted_text)

with right:
    st.subheader("ASK QnA")
    q=st.text_input("Question", placeholder= "Please ask question on uploaded document")
    button = st.button("Ask PDF", type="primary", use_container_width=True)
    if not up:
        st.warning("Please upload a PDF first")
    elif not q.strip():
        st.warning("Please ask question")
    else:
        prompt = helper.make_prompt(prompt_style, q, extracted_text)

        with st.spinner(f"Calling model:{MODEL}"):
            t0 = time.time()
            ans = helper.call_ollama(OLLAMA, MODEL, prompt, temp)
            st.write(ans)
            elapsed = time.time() - t0
            st.write(f"** Time Taken:{elapsed:.2f}")
        
            with st.expander("Prompt"):
                st.write(prompt)

