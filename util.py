import os
import PyPDF2
import re
import string
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI

def preprocess_query(query: str) -> str:
    """
    Preprocess and normalize user queries for better matching.
    
    Args:
        query (str): Raw user query
    
    Returns:
        str: Preprocessed query
    """
    # Convert to lowercase
    query = query.lower()
    
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    
    # Remove punctuation except for important ones
    # Keep question marks, periods, and commas for context
    query = re.sub(r'[^\w\s\?\.\,]', '', query)
    
    # Normalize common abbreviations and contractions
    replacements = {
        'what is': 'what is',
        'what are': 'what are',
        'how do': 'how do',
        'can you': 'can you',
        'tell me': 'tell me',
        'show me': 'show me',
        'i want': 'i want',
        'i need': 'i need',
        'experience': 'experience',
        'skills': 'skills',
        'education': 'education',
        'work': 'work',
        'job': 'job',
        'position': 'position',
        'role': 'role',
        'responsibilities': 'responsibilities',
        'achievements': 'achievements',
        'projects': 'projects',
        'technologies': 'technologies',
        'languages': 'languages',
        'frameworks': 'frameworks',
        'tools': 'tools',
        'certifications': 'certifications',
        'degrees': 'degrees',
        'university': 'university',
        'college': 'college',
        'company': 'company',
        'employer': 'employer',
        'duration': 'duration',
        'years': 'years',
        'months': 'months',
        'salary': 'salary',
        'location': 'location',
        'remote': 'remote',
        'hybrid': 'hybrid',
        'onsite': 'onsite'
    }
    
    for old, new in replacements.items():
        query = query.replace(old, new)
    
    print(f"[DEBUG] Preprocessed query: '{query}'")
    return query

def expand_query(query: str, llm=None) -> List[str]:
    """
    Expand query with alternative phrasings for better retrieval.
    
    Args:
        query (str): Original query
        llm: Optional LLM for query expansion
    
    Returns:
        List[str]: List of expanded queries
    """
    expanded_queries = [query]
    
    # Simple rule-based expansions for common patterns
    if 'experience' in query:
        expanded_queries.extend([
            query.replace('experience', 'work experience'),
            query.replace('experience', 'job experience'),
            query.replace('experience', 'professional experience')
        ])
    
    if 'skills' in query:
        expanded_queries.extend([
            query.replace('skills', 'technical skills'),
            query.replace('skills', 'programming skills'),
            query.replace('skills', 'competencies')
        ])
    
    if 'education' in query:
        expanded_queries.extend([
            query.replace('education', 'academic background'),
            query.replace('education', 'degrees'),
            query.replace('education', 'qualifications')
        ])
    
    # Add question variations
    if query.endswith('?'):
        question_variations = [
            query.replace('what', 'tell me about'),
            query.replace('how', 'explain'),
            query.replace('when', 'what time'),
            query.replace('where', 'in which location'),
            query.replace('why', 'what is the reason')
        ]
        expanded_queries.extend(question_variations)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in expanded_queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    print(f"[DEBUG] Query expansion: {len(unique_queries)} variations generated")
    return unique_queries

def extract_keywords(query: str) -> List[str]:
    """
    Extract key terms from query for better matching.
    
    Args:
        query (str): User query
    
    Returns:
        List[str]: List of important keywords
    """
    # Common resume-related keywords
    resume_keywords = [
        'experience', 'skills', 'education', 'work', 'job', 'position', 'role',
        'responsibilities', 'achievements', 'projects', 'technologies', 'languages',
        'frameworks', 'tools', 'certifications', 'degrees', 'university', 'college',
        'company', 'employer', 'duration', 'years', 'months', 'salary', 'location',
        'remote', 'hybrid', 'onsite', 'python', 'java', 'javascript', 'react',
        'node', 'sql', 'database', 'api', 'aws', 'cloud', 'devops', 'agile',
        'scrum', 'leadership', 'management', 'team', 'collaboration', 'communication'
    ]
    
    # Extract keywords that appear in the query
    query_lower = query.lower()
    keywords = [keyword for keyword in resume_keywords if keyword in query_lower]
    
    # Also extract any capitalized terms (likely proper nouns)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', query)
    keywords.extend(proper_nouns)
    
    print(f"[DEBUG] Extracted keywords: {keywords}")
    return keywords

def process_query_advanced(query: str, use_expansion: bool = True) -> List[str]:
    """
    Advanced query processing with multiple strategies.
    
    Args:
        query (str): Original user query
        use_expansion (bool): Whether to use query expansion
    
    Returns:
        List[str]: List of processed queries to try
    """
    queries_to_try = []
    
    # 1. Original query
    queries_to_try.append(query)
    
    # 2. Preprocessed query
    processed_query = preprocess_query(query)
    queries_to_try.append(processed_query)
    
    # 3. Query expansion if enabled
    if use_expansion:
        expanded_queries = expand_query(processed_query)
        queries_to_try.extend(expanded_queries)
    
    # 4. Keyword-based queries
    keywords = extract_keywords(processed_query)
    if keywords:
        keyword_query = f"What are the {', '.join(keywords[:3])} mentioned in the resume?"
        queries_to_try.append(keyword_query)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries_to_try:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    print(f"[DEBUG] Advanced query processing: {len(unique_queries)} queries to try")
    for i, q in enumerate(unique_queries):
        print(f"[DEBUG] Query {i+1}: '{q}'")
    
    return unique_queries

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

    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    print("[INFO] Retriever created successfully")
    
    return retriever

def ask(query, retriever=None, file_path="AS_KB.txt", model="gemini"):
    """
    Ask a question and get a response based on the resume content.
    
    Args:
        query (str): The question to ask
        retriever: Optional pre-loaded retriever. If None, will load from file_path
        file_path (str): Path to the resume file (default: "AS_KB.txt")
        model (str): Ollama model to use (default: "llama3")
    
    Returns:
        str: The answer to the question
    """
    try:
        # Preprocess the query
        print(f"[INFO] Original query: '{query}'")
        processed_query = preprocess_query(query)
        
        # Extract keywords for better context
        keywords = extract_keywords(processed_query)
        
        # Load retriever if not provided
        if retriever is None:
            print(f"[INFO] Loading retriever from {file_path}")
            retriever = load_resume_and_create_retriever(file_path)
        
        # Create QA chain
        print(f"[INFO] Creating QA chain with model: {model}")
        if model in ["gemini", "gemini-pro", "gemini-2.0-flash", "gemini-pro-vision"]:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
        else:
            from langchain_community.llms import Ollama
            llm = Ollama(model=model)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=False
        )
        
        # Get response with processed query
        print(f"[INFO] Processing preprocessed query: {processed_query}")
        response = qa_chain.run(processed_query)
        print(f"[INFO] Response generated successfully")
        
        return response
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return f"Sorry, I encountered an error while processing your question: {str(e)}"

def ask_with_sources(query, retriever=None, file_path="AS_KB.txt", model="mistral"):
    """
    Ask a question and get a response with source documents.
    
    Args:
        query (str): The question to ask
        retriever: Optional pre-loaded retriever. If None, will load from file_path
        file_path (str): Path to the resume file (default: "AS_KB.txt")
        model (str): Ollama model to use (default: "llama3")
    
    Returns:
        tuple: (answer, source_documents)
    """
    try:
        # Preprocess the query
        print(f"[INFO] Original query: '{query}'")
        processed_query = preprocess_query(query)
        
        # Extract keywords for better context
        keywords = extract_keywords(processed_query)
        
        # Load retriever if not provided
        if retriever is None:
            print(f"[INFO] Loading retriever from {file_path}")
            retriever = load_resume_and_create_retriever(file_path)
        
        # Create QA chain that returns source documents
        print(f"[INFO] Creating QA chain with model: {model}")
        if model in ["gemini", "gemini-pro", "gemini-2.0-flash", "gemini-pro-vision"]:
            llm = ChatGoogleGenerativeAI(model="gemini-pro")
        else:
            from langchain_community.llms import Ollama
            llm = Ollama(model=model)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )
        
        # Get response with sources using processed query
        print(f"[INFO] Processing preprocessed query: {processed_query}")
        result = qa_chain({"query": processed_query})
        answer = result["result"]
        source_documents = result["source_documents"]
        
        print(f"[INFO] Response generated successfully with {len(source_documents)} source documents")
        
        return answer, source_documents
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return f"Sorry, I encountered an error while processing your question: {str(e)}", []
