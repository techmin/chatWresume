#!/usr/bin/env python3
"""
Example usage of the ask() function for resume Q&A
"""

from util import ask, ask_with_sources

def main():
    """Demonstrate the ask functionality"""
    
    print("🤖 Resume Q&A Example")
    print("=" * 50)
    
    # Example questions to ask
    example_questions = [
        "What are Atmin's technical skills?",
        "What is Atmin's work experience?",
        "What education does Atmin have?",
        "What are Atmin's achievements?",
        "What programming languages does Atmin know?"
    ]
    
    print("\n📝 Example Questions and Answers:")
    print("-" * 50)
    
    for i, question in enumerate(example_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)
        
        try:
            # Get answer
            answer = ask(question)
            print(f"Answer: {answer}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🔍 Example with source documents:")
    print("-" * 50)
    
    # Example with source documents
    question = "What are Atmin's main skills and experience?"
    print(f"Question: {question}")
    
    try:
        answer, sources = ask_with_sources(question)
        print(f"\nAnswer: {answer}")
        print(f"\nSources ({len(sources)} documents):")
        
        for i, source in enumerate(sources, 1):
            print(f"\nSource {i}:")
            print(f"Content: {source.page_content[:200]}...")
            if hasattr(source, 'metadata'):
                print(f"Metadata: {source.metadata}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 