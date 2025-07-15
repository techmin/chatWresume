# 💬 Chat With Resume

An intelligent Q&A system that allows you to ask questions about Atmin's resume using AI-powered search and retrieval.

## 🚀 Features

- **Smart Q&A**: Ask questions about skills, experience, education, and achievements
- **Multiple AI Models**: Support for llama3, llama2, mistral, and codellama
- **Source Documents**: Option to see where information comes from
- **Chat History**: Keep track of previous questions and answers
- **Web Interface**: Beautiful Streamlit-based UI
- **API Access**: RESTful API with Swagger documentation
- **Email Integration**: Direct contact form to reach Atmin

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chatWresume
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama:**
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull the required models:
     ```bash
     ollama pull llama3
     ollama pull nomic-embed-text
     ```

## 🎯 Usage

### Web Interface

Start the Streamlit app:
```bash
streamlit run app.py
```

Features:
- **Ask Questions**: Type questions about Atmin's resume
- **Model Selection**: Choose from different AI models
- **Source Documents**: Toggle to see where information comes from
- **Chat History**: View and clear previous conversations
- **Direct Contact**: Send questions directly to Atmin

### API with Swagger Documentation

Start the API server with Swagger:
```bash
python api_swagger.py
```

#### Access Swagger UI
- **Swagger Documentation**: http://localhost:5000/docs
- **API Tester**: Open `api_test.html` in your browser

#### API Endpoints

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Ask Question (POST):**
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Atmin'\''s skills?", "model": "llama3"}'
```

**Ask Question (GET):**
```bash
curl "http://localhost:5000/api/ask?q=What%20are%20Atmin%27s%20skills?&model=llama3"
```

**Get Available Models:**
```bash
curl http://localhost:5000/api/models
```

**Get Example Questions:**
```bash
curl http://localhost:5000/api/examples
```

**With Source Documents:**
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Atmin'\''s skills?", "include_sources": true}'
```

### Programmatic Usage

#### Simple Ask Function

```python
from util import ask

# Ask a simple question
answer = ask("What are Atmin's technical skills?")
print(answer)

# Use a different model
answer = ask("What is Atmin's work experience?", model="mistral")
print(answer)
```

#### Ask with Source Documents

```python
from util import ask_with_sources

# Get answer with source documents
answer, sources = ask_with_sources("What are Atmin's achievements?")

print(f"Answer: {answer}")
print(f"Sources: {len(sources)} documents")

for i, source in enumerate(sources, 1):
    print(f"\nSource {i}:")
    print(f"Content: {source.page_content[:200]}...")
    print(f"Metadata: {source.metadata}")
```

### Example Script

Run the example script to see the functionality in action:
```bash
python example_usage.py
```

## 🔧 Configuration

### Email Setup

To enable email functionality, update the configuration in `app.py`:

```python
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECIPIENT_EMAIL = "atmin@example.com"
```

### Resume File

The system uses `AS_KB.txt` by default. You can change this in the code or specify a different file path when calling the functions.

## 📁 File Structure

```
chatWresume/
├── app.py              # Streamlit web interface
├── api_swagger.py      # Flask API with Swagger documentation
├── api_test.html       # HTML interface for testing API
├── util.py             # Core Q&A functionality
├── example_usage.py    # Example usage script
├── AS_KB.txt          # Resume knowledge base
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🛠️ Core Functions

### `ask(query, retriever=None, file_path="AS_KB.txt", model="llama3")`

Ask a question and get an answer based on the resume content.

**Parameters:**
- `query` (str): The question to ask
- `retriever`: Optional pre-loaded retriever
- `file_path` (str): Path to resume file
- `model` (str): Ollama model to use

**Returns:**
- `str`: The answer to the question

### `ask_with_sources(query, retriever=None, file_path="AS_KB.txt", model="llama3")`

Ask a question and get an answer with source documents.

**Parameters:**
- Same as `ask()`

**Returns:**
- `tuple`: (answer, source_documents)

## 🤖 Supported Models

- **llama3**: Latest Llama model (default)
- **llama2**: Llama 2 model
- **mistral**: Mistral model
- **codellama**: Code-focused Llama model

## 📝 Example Questions

Try these example questions:

- "What are Atmin's technical skills?"
- "What is Atmin's work experience?"
- "What education does Atmin have?"
- "What are Atmin's achievements?"
- "What programming languages does Atmin know?"
- "What projects has Atmin worked on?"
- "What is Atmin's background in AI/ML?"

## 🔍 API Testing

### Swagger UI
1. Start the API: `python api_swagger.py`
2. Open: http://localhost:5000/docs
3. Test endpoints directly in the browser

### HTML Tester
1. Start the API: `python api_swagger.py`
2. Open `api_test.html` in your browser
3. Use the interactive interface to test the API

### cURL Examples
```bash
# Health check
curl http://localhost:5000/api/health

# Ask a question
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Atmin'\''s skills?"}'

# Get available models
curl http://localhost:5000/api/models

# Get example questions
curl http://localhost:5000/api/examples
```

## 🚨 Troubleshooting

### Common Issues

1. **Ollama not running:**
   ```bash
   ollama serve
   ```

2. **Model not found:**
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

3. **File not found:**
   - Ensure `AS_KB.txt` exists in the project directory
   - Check file permissions

4. **Memory issues:**
   - Use smaller models like `mistral` instead of `llama3`
   - Reduce chunk size in `util.py`

5. **API not accessible:**
   - Check if the API server is running: `python api_swagger.py`
   - Verify the port (5000) is not in use
   - Check firewall settings

### Error Messages

- **"File not found"**: Check if the resume file exists
- **"No text found"**: The file might be empty or corrupted
- **"Model not available"**: Pull the required Ollama model
- **"Connection refused"**: API server not running

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Contact Atmin directly through the web interface
- Check the troubleshooting section above
