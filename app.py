import pandas as pd
from flask import Flask, request, jsonify
from rapidfuzz import process

app = Flask(__name__)

def load_eco_scores(csv_file):
    """Load eco scores from a CSV file into a dictionary."""
    df = pd.read_csv(csv_file)
    return dict(zip(df["Material Name"], df["Eco Score"]))

def correct_material_names(materials, eco_scores):
    """Correct material names using AI-powered fuzzy matching."""
    corrected = {}
    suggestions = {}
    
    for mat, perc in materials.items():
        best_match, score, _ = process.extractOne(mat, eco_scores.keys())
        if score > 80:  # Acceptable confidence level
            corrected[best_match] = perc
        else:
            suggestions[mat] = best_match  # Suggest the closest match

    return corrected, suggestions

def calculate_weighted_eco_score(materials, eco_scores):
    """Calculate the weighted average eco score and list considered materials."""
    total_weight = sum(materials.values())
    
    if total_weight == 0:
        return {"error": "Total weight cannot be zero."}

    weighted_score = sum((eco_scores.get(mat, 0) * (perc / total_weight)) for mat, perc in materials.items())
    considered_materials = list(materials.keys())

    return {"eco_score": round(weighted_score, 2), "considered_materials": considered_materials}

@app.route("/")
def home():
    return "Eco Score API is running!"

@app.route("/calculate", methods=["POST"])
def calculate():
    """Handle eco score calculation from user input."""
    try:
        data = request.json
        materials = {}

        for mat, perc in data.get("materials", {}).items():
            try:
                materials[mat] = float(perc)
            except ValueError:
                return jsonify({"error": "Invalid format. Please provide numbers for percentages."}), 400

        eco_scores = load_eco_scores("eco_scores.csv")
        corrected, suggestions = correct_material_names(materials, eco_scores)

        if suggestions:
            return jsonify({"suggestions": suggestions, "message": "Some material names were unclear. Please confirm corrections."})

        result = calculate_weighted_eco_score(corrected, eco_scores)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
