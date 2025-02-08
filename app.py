from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask API is running!"

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.json
    # Example: Dummy eco-score calculation
    eco_score = 75  # Replace with real logic
    return jsonify({"eco_score": eco_score})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render uses 0.0.0.0
