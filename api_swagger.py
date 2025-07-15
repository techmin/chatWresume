#!/usr/bin/env python3
"""
Resume Q&A API with Swagger/OpenAPI documentation
"""

from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from util import ask, ask_with_sources
import logging
from http import HTTPStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app, 
    title='Resume Q&A API',
    version='1.0',
    description='An intelligent Q&A system for searching and retrieving information from Atmin\'s resume',
    doc='/docs',
    default='api',
    default_label='Resume Q&A Endpoints'
)

# Define namespaces
ns = api.namespace('api', description='Resume Q&A operations')

# Define models for Swagger documentation
question_model = api.model('Question', {
    'query': fields.String(required=True, description='The question to ask about the resume'),
    'model': fields.String(description='AI model to use (llama3, llama2, mistral, codellama)', default='llama3'),
    'file_path': fields.String(description='Path to resume file', default='AS_KB.txt'),
    'include_sources': fields.Boolean(description='Include source documents in response', default=False)
})

answer_model = api.model('Answer', {
    'answer': fields.String(description='The answer to the question'),
    'query': fields.String(description='The original question'),
    'model': fields.String(description='The AI model used'),
    'sources': fields.List(fields.Raw, description='Source documents (if requested)')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

health_model = api.model('Health', {
    'status': fields.String(description='Service status'),
    'message': fields.String(description='Service message'),
    'version': fields.String(description='API version')
})

@ns.route('/health')
class HealthCheck(Resource):
    @ns.doc('health_check')
    @ns.marshal_with(health_model)
    def get(self):
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'message': 'Resume Q&A API is running',
            'version': '1.0'
        }

@ns.route('/ask')
class AskQuestion(Resource):
    @ns.doc('ask_question_post')
    @ns.expect(question_model)
    @ns.marshal_with(answer_model)
    @ns.response(400, 'Bad Request', error_model)
    @ns.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Ask a question about the resume (POST)"""
        try:
            data = request.get_json()
            
            if not data or 'query' not in data:
                api.abort(400, 'Missing "query" parameter')
            
            query = data['query']
            model = data.get('model', 'llama3')
            file_path = data.get('file_path', 'AS_KB.txt')
            include_sources = data.get('include_sources', False)
            
            logger.info(f"Processing POST query: {query}")
            
            if include_sources:
                answer, sources = ask_with_sources(query, file_path=file_path, model=model)
                
                # Format source documents
                formatted_sources = []
                for source in sources:
                    formatted_sources.append({
                        "content": source.page_content,
                        "metadata": source.metadata if hasattr(source, 'metadata') else {}
                    })
                
                return {
                    "answer": answer,
                    "sources": formatted_sources,
                    "query": query,
                    "model": model
                }
            else:
                answer = ask(query, file_path=file_path, model=model)
                
                return {
                    "answer": answer,
                    "query": query,
                    "model": model,
                    "sources": []
                }
        
        except Exception as e:
            logger.error(f"Error processing POST query: {str(e)}")
            api.abort(500, str(e))

@ns.route('/ask')
class AskQuestionGet(Resource):
    @ns.doc('ask_question_get')
    @ns.param('q', 'The question to ask', required=True)
    @ns.param('model', 'AI model to use', enum=['llama3', 'llama2', 'mistral', 'codellama'], default='llama3')
    @ns.param('sources', 'Include source documents', type=bool, default=False)
    @ns.marshal_with(answer_model)
    @ns.response(400, 'Bad Request', error_model)
    @ns.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Ask a question about the resume (GET)"""
        query = request.args.get('q')
        model = request.args.get('model', 'llama3')
        include_sources = request.args.get('sources', 'false').lower() == 'true'
        
        if not query:
            api.abort(400, 'Missing "q" parameter')
        
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
                
                return {
                    "answer": answer,
                    "sources": formatted_sources,
                    "query": query,
                    "model": model
                }
            else:
                answer = ask(query, model=model)
                
                return {
                    "answer": answer,
                    "query": query,
                    "model": model,
                    "sources": []
                }
        
        except Exception as e:
            logger.error(f"Error processing GET query: {str(e)}")
            api.abort(500, str(e))

@ns.route('/models')
class AvailableModels(Resource):
    @ns.doc('get_models')
    def get(self):
        """Get list of available AI models"""
        return {
            'models': [
                {
                    'name': 'llama3',
                    'description': 'Latest Llama model (default)',
                    'recommended': True
                },
                {
                    'name': 'llama2',
                    'description': 'Llama 2 model',
                    'recommended': False
                },
                {
                    'name': 'mistral',
                    'description': 'Mistral model (faster, smaller)',
                    'recommended': False
                },
                {
                    'name': 'codellama',
                    'description': 'Code-focused Llama model',
                    'recommended': False
                }
            ]
        }

@ns.route('/examples')
class ExampleQuestions(Resource):
    @ns.doc('get_examples')
    def get(self):
        """Get example questions to try"""
        return {
            'examples': [
                "What are Atmin's technical skills?",
                "What is Atmin's work experience?",
                "What education does Atmin have?",
                "What are Atmin's achievements?",
                "What programming languages does Atmin know?",
                "What projects has Atmin worked on?",
                "What is Atmin's background in AI/ML?",
                "What are Atmin's strengths?",
                "What technologies does Atmin use?",
                "What is Atmin's career objective?"
            ]
        }

if __name__ == '__main__':
    print("🚀 Starting Resume Q&A API with Swagger...")
    print("📝 Available endpoints:")
    print("  - GET  /docs - Swagger UI documentation")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/ask - Ask question (JSON body)")
    print("  - GET  /api/ask - Ask question (query parameter)")
    print("  - GET  /api/models - Available AI models")
    print("  - GET  /api/examples - Example questions")
    print("\n💡 Access Swagger UI at: http://localhost:5000/docs")
    print("\n🔧 Example usage:")
    print("  curl -X POST http://localhost:5000/api/ask \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"query\": \"What are Atmin\\'s skills?\"}'")
    print("\n  curl 'http://localhost:5000/api/ask?q=What%20are%20Atmin%27s%20skills?'")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 