# MedSummarize AI
## A RAG-Driven Chatbot for Medical Paper and Article Summarization
### Under the Guidance of Professor Dr. Antonio Diana 
#### By : Hemanth Akkenapally, Manasa Jagati, Adithya Kale


## Overview
MedSummarize is an AI-powered chatbot designed to simplify the summarization of medical research papers. By leveraging **Retrieval-Augmented Generation (RAG)** techniques, it provides concise, accurate, and contextually relevant summaries, enabling healthcare professionals, researchers, and students to quickly grasp critical insights. The system supports multiple file formats like DOCX, PDF, and TXT, and offers customizable summary lengths tailored to user needs.

## Key Features
- **Multi-format Support:** Processes DOCX, PDF, and TXT files.
- **Advanced Summarization:** Uses Facebook's **BART** model for abstractive summarization.
- **Efficient Retrieval:** Employs **SciBERT** embeddings and **FAISS** for context retrieval.
- **User-Friendly Interface:** Flask-based chatbot interface with interactive options for users.
- **Cloud Integration:** Scalable and reliable storage using AWS S3.

## System Architecture
The architecture consists of modular components designed for seamless summarization:
1. **File Parsing Module:** Extracts text from various formats using libraries like PyMuPDF and python-docx.
2. **Embedding Module:** Generates dense vector representations using **SciBERT** for semantic understanding.
3. **Retrieval Module:** Uses **FAISS** to efficiently retrieve relevant content from a medical literature corpus.
4. **Summarization Module:** Leverages the **BART-large-cnn** model for generating concise summaries.
5. **AWS Integration:** Ensures scalability and reliability with S3 for storing embeddings, indices, and parsed files.

## Technologies Used
- **Libraries:** PyMuPDF (fitz), python-docx, Hugging Face Transformers, FAISS
- **Models:** SciBERT, BART-large-cnn
- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Cloud:** AWS S3 for storage and scalability

## Installation and Setup
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Hemanth-Akkenapally/DATA_690_032264_NLP.git
   cd ChatBot_using_RAG

2. **Install Dependencies:**
    ```bash
        !pip install -r requirements.txt

3. Drive link for Embeddings, FAISS Indexes and All_texts files: https://drive.google.com/drive/folders/1ZMTZbDjhHpGa6l0V_HWJPu7B1bONUr5h?usp=drive_link

- (I have used s3 to store and run the files by configuring the AWS through cmd.)
- you can find Python Notebook for generating the embeddings, indexes and all_texts.

4. **Run the Flask App:**
    ```bash
        python app.py

5. **References:**
- Hugging Face: SciBERT
- Hugging Face: BART-large-cnn
- FAISS
