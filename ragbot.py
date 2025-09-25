import os, time, streamlit as st
from pathlib import Path
from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="RAG Bot", layout="wide", page_icon="🤖")
st.title("RAGBOT")
st.caption("Tiny RAG bot using Ollama + Langchain + FAISS")

DATA_DIR = Path("data2")
FILES = [DATA_DIR/"iphone_histroy.txt", DATA_DIR/"iphone_specs.txt", DATA_DIR/"iphone_care.txt"]
EMBED_MODEL = "nomic-embed-text"

HEAVY = st.text_input("Heavy LLM Model", "qwen2.5vl:3b")
LIGHT = st.text_input("Light LLM Model", "gemma3:1b")
top_k = st.slider("Top-K", 1, 8, 5)
version = st.radio("Prompt Version", ["v1 (hallucinate)", "v2(loose RAG)", "v3 (strict RAG)"], horizontal=True)
model_pick = st.radio("Which model to use now?", ["Heavy", "Light"], horizontal=True)

@st.cache_resource(show_spinner=False)
def build_store():
    texts = []
    for p in FILES:
        texts.append(p.read_text(encoding="utf-8"))
    splitter = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=40)
    docs = []
    for p, t, in zip(FILES, texts):
        for c in splitter.split_text(t):
            docs.append({"page_content": c, "metadata": {"source": p.name}})
    emb = OllamaEmbeddings(model=EMBED_MODEL)
    store = FAISS.from_texts([d["page_content"] for d in docs], emb, metadatas=[d["metadata"] for d in docs])
    return store