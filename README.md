# PaperSummarizer AI

**PaperSummarizer AI** is an intelligent web application that summarizes academic papers, articles, and web content using a locally hosted BART-based model. It accepts inputs in multiple formats including raw text, URLs, PDFs, and batch PDF uploads. The application is built entirely with local resources, ensuring data privacy without relying on third-party APIs.

##  Features

-  User Authentication (Register/Login)
-  Text, URL, and PDF summarization
-  Batch PDF upload support
-  Local BART model (`facebook/bart-large-cnn`) for summarization
-  Summary history tracking
-  Modern, responsive user interface
-  Data stored locally in JSON files

## 🛠 Tech Stack

- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Backend:** Python, Flask
- **NLP Model:** HuggingFace Transformers (BART)
- **PDF Parsing:** PyMuPDF, PyPDF2
- **Data Storage:** JSON files (users and summaries)
- **Other Libraries:** Flask-Login, BeautifulSoup, jusText, trafilatura

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AITextCondenser.git
cd AITextCondenser
2. Create and Activate Virtual Environment (optional but recommended)
bash
Copy
Edit
python -m venv venv
On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Run the Application
bash
Copy
Edit
python app.py
Visit http://127.0.0.1:5000 in your browser.

📁 Folder Structure
pgsql
Copy
Edit
AITextCondenser/
├── app.py
├── auth.py
├── main.py
├── routes/
├── templates/
├── static/
├── summarizer/
├── storage/
├── data/
│   ├── users.json
│   └── summaries.json
├── uploads/
├── venv/
└── requirements.txt
📌 Note
This project uses JSON files for data storage, making it simple and lightweight. You can later upgrade to MongoDB or another database if needed.