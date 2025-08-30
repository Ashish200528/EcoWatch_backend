import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from the .env file (for the GEMINI_API_KEY)
load_dotenv()

# Import the analysis function from your other file
from gemini_analyzer import analyze_report

app = Flask(__name__)

# -------------------- ROUTES --------------------

@app.route("/", methods=["GET"])
def index():
    """
    Root endpoint to confirm the server is running.
    """
    return jsonify({"message": "Welcome to the EcoWatch Analysis API!"}), 200

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "ok"}), 200

@app.route("/upload", methods=["POST"])
def upload_data():
    """
    Handles the file upload and sends data to the AI for analysis.
    """
    try:
        # --- 1. Extract form data ---
        user_uuid = request.form.get("user_uuid")
        description = request.form.get("description")
        category = request.form.get("category")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        image_file = request.files.get("image")

        # Basic validation to ensure required fields are present
        if not all([description, category, latitude, longitude, image_file]):
            return jsonify({"error": "Missing required form fields"}), 400

        print("--- Form Data Received ---")
        print(f"User: {user_uuid}, Category: {category}, Lat: {latitude}, Lon: {longitude}")
        print("--------------------------")


        # --- 2. Call the AI analysis function ---
        ai_analysis_result = analyze_report(
            latitude=latitude,
            longitude=longitude,
            category=category,
            description=description,
            image_file=image_file
        )

        # Print the final AI response to the backend log for verification
        print("\n--- Final AI Analysis Response ---")
        print(ai_analysis_result)
        print("----------------------------------\n")

        # --- 3. Return the response to the client ---
        return jsonify({
            "message": "Data analyzed successfully.",
            "ai_analysis": ai_analysis_result
        }), 200

    except Exception as e:
        # Log any unexpected errors that occur in this route
        print(f"An error occurred in the /upload route: {e}")
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500


# -------------------- MAIN --------------------
if __name__ == "__main__":
    # The server will run on port 5000 by default for local development
    # For production, Render will use the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)