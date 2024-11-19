import os
import boto3
from flask import Flask, request, jsonify, render_template
import fitz  # PyMuPDF for PDF handling
from docx import Document
from transformers import BartTokenizer, BartForConditionalGeneration
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import tempfile

# Initialize Flask app
app = Flask(_name_)

# AWS S3 Configurations
S3_BUCKET_NAME = "medsummarize-data"
S3_REGION_NAME = "us-east-2"
s3_client = boto3.client('s3', region_name=S3_REGION_NAME)

# Local paths for downloaded files
faiss_index_path = "/tmp/all_faiss_index"
embeddings_path = "/tmp/all_embeddings.npy"
txt_file_path = "/tmp/all_texts.txt"

# Helper function to download files from S3
def download_from_s3(bucket_name, key, local_path):
    try:
        s3_client.download_file(bucket_name, key, local_path)
        print(f"Downloaded {key} to {local_path}")
    except Exception as e:
        raise FileNotFoundError(f"Error downloading {key} from S3: {e}")

# Download FAISS index, embeddings, and text data from S3
try:
    download_from_s3(S3_BUCKET_NAME, "all_faiss_index", faiss_index_path)
    download_from_s3(S3_BUCKET_NAME, "all_embeddings.npy", embeddings_path)
    download_from_s3(S3_BUCKET_NAME, "all_texts.txt", txt_file_path)
except FileNotFoundError as e:
    print(f"Error: {e}")
    raise SystemExit("Failed to load necessary files from S3. Ensure files exist in the bucket.")

# Load models and data
# Sentence Transformer model for embeddings
embedding_model = SentenceTransformer("allenai/scibert_scivocab_uncased")

# Summarization model
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
summarization_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

# Load FAISS index and embeddings
try:
    index = faiss.read_index(faiss_index_path)
    all_embeddings = np.load(embeddings_path)
except Exception as e:
    raise FileNotFoundError(f"Error loading FAISS index or embeddings: {e}")

# Load text data
try:
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        all_texts = [text.strip() for text in file.read().split(',') if text.strip()]
except FileNotFoundError:
    all_texts = []
    print("The provided .txt file is invalid or missing.")

# File parsing utilities
def parse_pdf(filepath):
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_docx(filepath):
    doc = Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_txt(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def extract_text_from_file(filepath):
    if filepath.endswith('.pdf'):
        return parse_pdf(filepath)
    elif filepath.endswith('.docx'):
        return parse_docx(filepath)
    elif filepath.endswith('.txt'):
        return parse_txt(filepath)
    else:
        raise ValueError("Unsupported file format. Please upload .pdf, .docx, or .txt.")

# Retrieval and summarization functions
def retrieve_context(query_text, index, all_texts, embedding_model, k=5):
    query_embedding = embedding_model.encode([query_text], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, k)
    retrieved_contexts = [all_texts[i] for i in indices.flatten()]
    return " ".join(retrieved_contexts)

def generate_summary(context, model, tokenizer, max_length=200):
    inputs = tokenizer(context, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        max_length=max_length,
        num_beams=4,
        early_stopping=True,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7  # Add randomness
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Flask routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get user input or uploaded file
        user_message = request.form.get("message")
        file = request.files.get("file")

        # Process file if uploaded
        if file:
            # Create a temporary file in the system's temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as temp_file:
                file.save(temp_file.name)  # Save the uploaded file to the temporary file
                temp_filepath = temp_file.name

            try:
                # Process the file (e.g., extract text)
                extracted_text = extract_text_from_file(temp_filepath)
            finally:
                # Clean up the temporary file
                os.remove(temp_filepath)
        else:
            extracted_text = user_message

        # Retrieve context and generate response
        retrieved_context = retrieve_context(extracted_text, index, all_texts, embedding_model)
        combined_input = extracted_text + "\n" + retrieved_context
        summary = generate_summary(combined_input, summarization_model, tokenizer)

        return jsonify({"response": summary})
    except Exception as e:
        return jsonify({"error": str(e)})

# Run Flask app
if _name_ == "_main_":
    app.run(debug=True)