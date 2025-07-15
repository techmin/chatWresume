import streamlit as st
from util import load_resume_and_create_retriever, ask, ask_with_sources
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
import requests
from datetime import datetime

st.set_page_config(page_title="Resume Q&A", layout="wide")
st.title("💬 Chat With Atmin's Resume")

# 🔧 Set your resume file path (make sure it's correct!)
resume_path = "AS_KB.txt" 

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Replace with your email
SENDER_PASSWORD = "your-app-password"  # Replace with your app password
RECIPIENT_EMAIL = "atmin@example.com"  # Replace with Atmin's email


def send_email_to_atmin(name, email, company, question, additional_info):
    """Send email to Atmin with user's question and information via Formspree"""
    try:
        FORMSPREE_ENDPOINT = "https://formspree.io/f/mzzvbpqn"  # Replace with your Formspree endpoint
        data = {
            "name": name,
            "email": email,
            "company": company,
            "question": question,
            "additional_info": additional_info,
            "_subject": f"New Question for Atmin from {name} - {company}",
        }
        response = requests.post(FORMSPREE_ENDPOINT, data=data)
        if response.status_code == 200 or response.status_code == 202:
            return True
        else:
            st.error(f"Failed to send email: {response.text}")
            return False
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

try:
    # Load resume and create retriever
    retriever = load_resume_and_create_retriever(resume_path)

    # Create two columns for the interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat UI
        st.subheader("🤖 Ask questions about Atmin's resume:")
        
        # Chat input
        query = st.text_input("Enter your question", placeholder="e.g., What are Atmin's skills? What experience does he have?")
        
        # Model selection
        model = "llama3"
        # Show sources option
        show_sources = st.checkbox("Show source documents", value=False)
        
        if st.button("🔍 Ask Question", type="primary"):
            if query.strip():
                with st.spinner("🤔 Thinking..."):
                    try:
                        if show_sources:
                            answer, sources = ask_with_sources(query, retriever=retriever, model=model)
                            
                            # Display answer
                            st.markdown("### 📄 Answer:")
                            st.write(answer)
                            
                            # Display sources
                            if sources:
                                st.markdown("### 📚 Source Documents:")
                                for i, source in enumerate(sources, 1):
                                    with st.expander(f"Source {i}"):
                                        st.write(source.page_content)
                                        if hasattr(source, 'metadata'):
                                            st.caption(f"Source: {source.metadata.get('source', 'Unknown')}")
                        else:
                            answer = ask(query, retriever=retriever, model=model)
                            st.markdown("### 📄 Answer:")
                            st.write(answer)
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "question": query,
                            "answer": answer if not show_sources else answer,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a question.")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("💬 Chat History")
            
            for i, chat in enumerate(st.session_state.chat_history):
                with st.container():
                    st.markdown(f"**Q ({chat['timestamp']}):** {chat['question']}")
                    st.markdown(f"**A:** {chat['answer']}")
                    if i < len(st.session_state.chat_history) - 1:
                        st.markdown("---")
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
    
    with col2:
        # Ask Atmin directly section
        st.subheader("📧 Ask Atmin Directly")
        st.write("Have a specific question? Send it directly to Atmin!")
        
        # Create a form for collecting user information
        with st.form("ask_atmin_form"):
            name = st.text_input("Your Name *", placeholder="Enter your full name")
            email = st.text_input("Your Email *", placeholder="your.email@company.com")
            company = st.text_input("Your Company", placeholder="Company name")
            question = st.text_area("Your Question *", placeholder="What would you like to ask Atmin?", height=100)
            additional_info = st.text_area("Additional Information", placeholder="Any additional context or information...", height=80)
            
            submit_button = st.form_submit_button("📧 Send to Atmin")
            
            if submit_button:
                if name and email and question:
                    if send_email_to_atmin(name, email, company, question, additional_info):
                        st.success("✅ Your message has been sent to Atmin! He'll get back to you soon.")
                    else:
                        st.error("❌ Failed to send message. Please try again later.")
                else:
                    st.error("❌ Please fill in all required fields (Name, Email, and Question).")

except FileNotFoundError as e:
    st.error(f"❌ {str(e)}")
except Exception as e:
    st.error(f"⚠️ Unexpected error: {str(e)}")

# # Add a note about email configuration
# st.sidebar.markdown("---")
# st.sidebar.markdown("### 📧 Email Setup")
# st.sidebar.markdown("""
# To enable email functionality, update the email configuration in the code:
# - `SENDER_EMAIL`: Your Gmail address
# - `SENDER_PASSWORD`: Your Gmail app password
# - `RECIPIENT_EMAIL`: Atmin's email address
# """)

# Add usage instructions
st.sidebar.markdown("### 💡 Usage Tips")
st.sidebar.markdown("""
- **Ask specific questions** about Atmin's experience, skills, or background
- **Try different models** to see which gives the best answers
- **Enable source documents** to see where the information comes from
- **Use the chat history** to reference previous questions and answers
""")
