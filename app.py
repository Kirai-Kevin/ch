import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import requests
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Initialize Flask application
app = Flask(__name__)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Hugging Face API token from environment variables
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("HUGGINGFACE_API_TOKEN is not set in .env file")

# Hugging Face API base URL and headers
API_URL = "https://api-inference.huggingface.co/models/"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

# Route to render a basic HTML page
@app.route("/")
def index():
    return render_template('base.html')

# Endpoint to handle model prediction
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        model_name = data.get("model")
        message = data.get("message")
        
        # Validate input parameters
        if not model_name or not message:
            return jsonify({"error": "Both 'model' and 'message' must be provided"}), 400

        # Ensure model_name matches the loaded model
        if model_name != "meta-llama/Meta-Llama-3-8B-Instruct":
            return jsonify({"error": "Invalid model name"}), 400

        # Tokenize input messages
        inputs = tokenizer([message], return_tensors="pt", padding=True, truncation=True)

        # Generate responses
        with torch.no_grad():
            outputs = model.generate(inputs.input_ids, max_length=100)

        # Decode generated responses
        generated_texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        if not generated_texts:
            return jsonify({"answer": "I'm sorry, but I couldn't generate a response. How else can I assist you?"})

        return jsonify({"answer": generated_texts[0]})

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({"error": "I'm having trouble connecting to my knowledge base. Please try again later."}), 503
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        return jsonify({"error": str(e)}), 400  # Bad request for missing environment variable
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500

if __name__ == '__main__':
    # Run the Flask application
    app.run(host="0.0.0.0", port=8080, debug=True)
