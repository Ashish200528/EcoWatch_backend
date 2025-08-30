import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Import BOTH functions from your analyzer file
from gemini_analyzer import analyze_report, calculate_score

app = Flask(__name__)

# -------------------- ROUTES --------------------

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to the EcoWatch Analysis API!"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/upload", methods=["POST"])
def upload_data():
    try:
        # --- 1. Extract form data ---
        description = request.form.get("description")
        category = request.form.get("category")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        image_file = request.files.get("image")

        if not all([description, category, latitude, longitude, image_file]):
            return jsonify({"error": "Missing required form fields"}), 400

        # --- 2. Call the first AI analysis function ---
        ai_analysis_result = analyze_report(
            latitude=latitude,
            longitude=longitude,
            category=category,
            description=description,
            image_file=image_file
        )
        
        score_result = {}
        # --- 3. Call the second AI scoring function ---
        # Only proceed if the first analysis was successful
        if "error" not in ai_analysis_result:
            score_result = calculate_score(
                analysis_data=ai_analysis_result,
                description=description,
                category=category
            )
            
            # Print the final score to the backend log, as you requested
            print("\n--- Final Score Result ---")
            print(score_result)
            print("--------------------------\n")
        else:
            score_result = {"error": "Scoring skipped due to initial analysis failure."}

        # --- 4. Return the combined response to the client ---
        return jsonify({
            "message": "Data processed successfully.",
            "initial_analysis": ai_analysis_result,
            "final_score": score_result
        }), 200

    except Exception as e:
        print(f"An error occurred in the /upload route: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

# -------------------- MAIN --------------------
if __name__ == "__main__":
    # The server will run on port 5000 by default for local development
    # For production, Render will use the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)