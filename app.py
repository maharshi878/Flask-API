from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import pandas as pd
from rapidfuzz import process

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

def load_eco_scores(csv_file):
    """Load eco scores from a CSV file into a dictionary."""
    df = pd.read_csv(csv_file)
    eco_scores = dict(zip(df["Material Name"].str.lower(), df["Eco Score"]))
    return eco_scores

def correct_material_names(materials, eco_scores):
    """Correct material names using AI-powered fuzzy matching."""
    corrected = {}
    suggestions = {}
    for mat, perc in materials.items():
        best_match, score, _ = process.extractOne(mat.lower(), eco_scores.keys())
        if score > 80:  # Acceptable confidence level
            corrected[best_match] = perc
        else:
            suggestions[mat] = best_match
    return corrected, suggestions

def calculate_weighted_eco_score(materials, eco_scores):
    """Calculate the weighted average eco score and list considered materials."""
    total_weight = sum(materials.values())
    
    if total_weight == 0:
        return {"error": "Total weight cannot be zero."}, []

    weighted_score = sum((eco_scores.get(mat, 0) * (perc / total_weight)) for mat, perc in materials.items())
    considered_materials = list(materials.keys())

    return round(weighted_score, 2), considered_materials

@app.route('/')
def index():
    """Render the main web page."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Handle eco score calculation from user input."""
    try:
        data = request.json
        materials = {}

        for mat, perc in data.get("materials", {}).items():
            try:
                materials[mat.lower()] = float(perc)
            except ValueError:
                return jsonify({"error": f"Invalid percentage value for {mat}. Please enter a number."})

        eco_scores = load_eco_scores("eco_scores.csv")
        corrected, suggestions = correct_material_names(materials, eco_scores)

        if suggestions:
            return jsonify({"suggestions": suggestions, "message": "Some material names were unclear. Please confirm corrections."})

        score, considered = calculate_weighted_eco_score(corrected, eco_scores)

        return jsonify({"eco_score": score, "considered_materials": considered})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
