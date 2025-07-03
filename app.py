import streamlit as st
from util import load_resume_and_create_retriever
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    """Send email to Atmin with user's question and information"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"New Question for Atmin from {name} - {company}"
        
        # Email body
        body = f"""
        Hi Atmin,
        
        You have received a new question from someone interested in your profile:
        
        **From:** {name}
        **Email:** {email}
        **Company:** {company}
        **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        **Question:**
        {question}
        
        **Additional Information:**
        {additional_info if additional_info else "No additional information provided."}
        
        Best regards,
        Your Resume Chat Bot
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

try:
    # Load resume and create retriever
    retriever = load_resume_and_create_retriever(resume_path)

    # Create two columns for the interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat UI
        st.subheader("Ask questions about Atmin's resume:")
        query = st.text_input("Enter your question")

        if query:
            qa_chain = RetrievalQA.from_chain_type(
                llm=Ollama(model="llama3"),
                retriever=retriever,
                return_source_documents=False
            )

            with st.spinner("Thinking..."):
                response = qa_chain.run(query)
                st.write("📄 Answer:", response)
    
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

# Add a note about email configuration
st.sidebar.markdown("---")
st.sidebar.markdown("### 📧 Email Setup")
st.sidebar.markdown("""
To enable email functionality, update the email configuration in the code:
- `SENDER_EMAIL`: Your Gmail address
- `SENDER_PASSWORD`: Your Gmail app password
- `RECIPIENT_EMAIL`: Atmin's email address
""")
