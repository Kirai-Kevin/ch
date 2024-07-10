import os
from flask import Flask, render_template, jsonify
from flask import request
from dotenv import load_dotenv
import replicate
import logging

# Initialize Flask application
app = Flask(__name__)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Replicate API token from environment variables
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN is not set in .env file")

# Initialize Replicate client
client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Chatbot context
context = """You are an educational assistant named Sam designed to help students learn various subjects. 
Your responses should be informative, engaging, and tailored to the student's level of understanding. 
Encourage critical thinking and provide explanations that foster learning."""

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid input, JSON expected"}), 400

        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"error": "Message must be provided"}), 400

        # Prepare the prompt for the language model
        prompt = f"{context}\n\nStudent: {user_message}\n\nSam:"

        # Generate response using Replicate API
        output = client.run(
            "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
            input={
                "prompt": prompt,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_length": 500,
                "repetition_penalty": 1.2
            }
        )

        # Process the output
        if isinstance(output, list):
            response = ' '.join(output).strip()
        elif isinstance(output, str):
            response = output.strip()
        else:
            response = "I apologize, but I couldn't generate a response. Could you please rephrase your question?"

        return jsonify({"answer": response})

    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate error: {str(e)}")
        return jsonify({"error": "I'm having trouble connecting to my knowledge base. Please try again later."}), 503
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True)
