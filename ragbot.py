import os, time, streamlit as st
from pathlib import Path
from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="RAG Bot", layout="wide", page_icon="🤖")
st.title("RAGBOT")
st.caption("Tiny RAG bot using Ollama + Langchain + FAISS")

DATA_DIR = Path("data2")
FILES = [DATA_DIR/"iphone_history.txt", DATA_DIR/"iphone_specs.txt", DATA_DIR/"iphone_care.txt"]
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
col = st.columns(2, gap = "large")
with col[0]:
    if st.button("Run indexing (vector store)"):
        t0 = time.time()
        st.session_state["store"] = build_store()
        st.success(f"Indexing done. Time taken: {time.time()-t0:.1f} seconds")
with col[1]:
    st.write("Ollama should be running")
q = st.text_input("Ask a question about iPhone")
go = st.button("Ask")

def make_prompt(v, question, ctx):
    if v.startswith("v1"):
        return f"""You are an imaginative tech story teller. Ignore accuracy and answer creatively.
Question: {question}
Answer:"""
    if v.startswith("v2"):
        return f"""You are a helpful iPhone expert. Use the context if relevant; if missing, make reasonable inferences.
Context: {ctx}
Question: {question}
Answer:"""
    #v3
    return f"""You are precise. Use ONLY the context. If not in context, say: "I don't know based on the docs."
    Context: {ctx}
    Question: {question}
    Answer with brief citations like [source]:"""
if go:
    if "store" not in st.session_state:
        st.warning("Run indexing first")
    elif not q.strip():
        st.warning("Please ask a question")
    else:
        store = st.session_state["store"]
        ctx = ""
        if not version.startswith("v1"):
            docs = store.similarity_search(q, k=top_k)
            ctx = "\n\n".join([f"[{d.metadata.get('source', 'doc')}] {d.page_content}" for d in docs])
        
        prompt = make_prompt(version, q, ctx)
        model = HEAVY if model_pick == "Heavy" else LIGHT
        llm = Ollama(model=model)
        with st.spinner(f"Generating with {model}..."):
            out = llm.invoke(prompt)
        st.markdown(f"**Model:** `{model}` | **Prompt:** `{version}`")
        st.write(out)
        