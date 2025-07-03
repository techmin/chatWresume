import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.schema import Document

def extract_text_from_txt(file_path):
    """Extract text from .txt file"""
    lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                lines.append(line.rstrip())
        text = '\n'.join(lines)
        if not text.strip():
            raise ValueError("No text found in the .txt file.")
        return [Document(page_content=text, metadata={"source": file_path})]
    except Exception as e:
        raise Exception(f"Error reading .txt file: {str(e)}")

def extract_text_from_pdf_stream(file_path):
    """Extract text from PDF using stream-based approach like a scanner"""
    text_content = []
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"[INFO] PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    # Extract text from the page
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content.append(page_text.strip())
                        print(f"[DEBUG] Page {page_num + 1}: {len(page_text)} characters")
                        print(f"[DEBUG] Page {page_num + 1} preview: {page_text[:100]}...")
                    else:
                        print(f"[DEBUG] Page {page_num + 1}: No text found")
                except Exception as e:
                    print(f"[WARNING] Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
        
        if not text_content:
            raise ValueError("No text content extracted from any page")
            
        return text_content
        
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

def load_resume_and_create_retriever(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    print(f"[INFO] Loading file: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        docs = extract_text_from_txt(file_path)
    elif ext == ".pdf":
        text_content = extract_text_from_pdf_stream(file_path)
        docs = [Document(page_content=text, metadata={"source": file_path, "page": i+1}) for i, text in enumerate(text_content)]
    else:
        raise ValueError("Unsupported file type. Please upload a .pdf or .txt file.")

    print(f"[INFO] Loaded {len(docs)} document(s) with content")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    chunks = [c for c in chunks if c.page_content.strip()]
    print(f"[INFO] Split into {len(chunks)} chunks")

    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    print("[INFO] Creating vector store embeddings...")
    vectorstore = FAISS.from_documents(chunks, embedding_model)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    print("[INFO] Retriever created successfully")
    
    return retriever
