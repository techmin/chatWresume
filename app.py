import streamlit as st
from util import load_resume_and_create_qa_chain
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

st.set_page_config(page_title="Resume Q&A", layout="wide")
st.title("💬 Chat With Your Resume")

# 🔧 Set your resume file path (make sure it's correct!)
resume_path = "AS_KB.pdf" 

try:
    # Load resume and create retriever
    retriever = load_resume_and_create_qa_chain(resume_path)

    # Chat UI
    st.subheader("Ask questions about your resume:")
    query = st.text_input("Enter your question")

    if query:
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0),
            retriever=retriever,
            return_source_documents=False
        )

        with st.spinner("Thinking..."):
            response = qa_chain.run(query)
            st.write("📄 Answer:", response)

except FileNotFoundError as e:
    st.error(f"❌ {str(e)}")
except Exception as e:
    st.error(f"⚠️ Unexpected error: {str(e)}")
