import streamlit as st
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
        extracted_text = "write function here"
        st.success(f"PDF Uploaded Successfully, Length:{len(extracted_text)}")
        with st.expander("PDF Text"):
            st.write(extracted_text)

with right:
    st.subheader("ASK QnA")
    st.text_input("Question", placeholder= "Please ask question on uploaded document")
