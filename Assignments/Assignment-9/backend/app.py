from flask import Flask, jsonify, request
import random

app = Flask(__name__)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # Return a dummy response simulating StyleGAN inference
    print("Received prediction request")
    return jsonify({
        "status": "success",
        "message": "Persona canvas generated successfully!",
        "style_vector": [random.random() for _ in range(5)]
    })

@app.route('/healthz', methods=['GET'])
def healthz():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
