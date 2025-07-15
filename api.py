#!/usr/bin/env python3
"""
Simple API interface for the ask() function
"""

from flask import Flask, request, jsonify
from util import ask, ask_with_sources
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Resume Q&A API is running"})

@app.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question about the resume"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        
        query = data['query']
        model = data.get('model', 'llama3')
        file_path = data.get('file_path', 'AS_KB.txt')
        include_sources = data.get('include_sources', False)
        
        logger.info(f"Processing query: {query}")
        
        if include_sources:
            answer, sources = ask_with_sources(query, file_path=file_path, model=model)
            
            # Format source documents
            formatted_sources = []
            for source in sources:
                formatted_sources.append({
                    "content": source.page_content,
                    "metadata": source.metadata if hasattr(source, 'metadata') else {}
                })
            
            return jsonify({
                "answer": answer,
                "sources": formatted_sources,
                "query": query,
                "model": model
            })
        else:
            answer = ask(query, file_path=file_path, model=model)
            
            return jsonify({
                "answer": answer,
                "query": query,
                "model": model
            })
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['GET'])
def ask_question_get():
    """Ask a question via GET request (for simple testing)"""
    query = request.args.get('q')
    model = request.args.get('model', 'llama3')
    include_sources = request.args.get('sources', 'false').lower() == 'true'
    
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400
    
    try:
        logger.info(f"Processing GET query: {query}")
        
        if include_sources:
            answer, sources = ask_with_sources(query, model=model)
            
            # Format source documents
            formatted_sources = []
            for source in sources:
                formatted_sources.append({
                    "content": source.page_content,
                    "metadata": source.metadata if hasattr(source, 'metadata') else {}
                })
            
            return jsonify({
                "answer": answer,
                "sources": formatted_sources,
                "query": query,
                "model": model
            })
        else:
            answer = ask(query, model=model)
            
            return jsonify({
                "answer": answer,
                "query": query,
                "model": model
            })
    
    except Exception as e:
        logger.error(f"Error processing GET query: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Resume Q&A API...")
    print("📝 Available endpoints:")
    print("  - GET  /health - Health check")
    print("  - POST /ask    - Ask question (JSON body)")
    print("  - GET  /ask    - Ask question (query parameter)")
    print("\n💡 Example usage:")
    print("  curl -X POST http://localhost:5000/ask \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"query\": \"What are Atmin\\'s skills?\"}'")
    print("\n  curl 'http://localhost:5000/ask?q=What%20are%20Atmin%27s%20skills?'")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 