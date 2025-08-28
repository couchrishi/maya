from flask import Flask, request, jsonify
import logging
from predictor import load_model

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load model on startup
model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.get_json()
        instances = data.get('instances', [])
        
        if not instances:
            return jsonify({"error": "No instances provided"}), 400
        
        # Generate predictions
        results = model.predict(instances)
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "model": "flux-game-assets"})

@app.route('/', methods=['GET'])
def home():
    """Basic info endpoint"""
    return jsonify({
        "name": "FLUX Game Assets Generator",
        "model": "FLUX.1-dev + Game Assets LoRA",
        "endpoints": {
            "/predict": "POST - Generate game assets",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)