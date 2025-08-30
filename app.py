import os
import uuid
import json
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Import your existing Gemini analyzer functions
from gemini_analyzer import analyze_report, calculate_score

# --- 1. INITIALIZE FIREBASE ADMIN SDK (Storage part removed) ---
load_dotenv()

try:
    firebase_creds_json_str = os.getenv("FIREBASE_CREDS_JSON")
    if firebase_creds_json_str:
        print("Initializing Firebase from environment variable...")
        cred_json = json.loads(firebase_creds_json_str)
        cred = credentials.Certificate(cred_json)
    else:
        print("Initializing Firebase from local 'firebase_credentials.json' file...")
        cred = credentials.Certificate("firebase_credentials.json")

    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully (for Firestore).")
except Exception as e:
    print("!!! CRITICAL: FAILED TO INITIALIZE FIREBASE ADMIN SDK !!!")
    print(f"Error: {e}")
    traceback.print_exc()

# Get a client for the Firestore service
db = firestore.client()

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
        # --- 2. EXTRACT DATA FROM FLUTTER APP ---
        description = request.form.get("description")
        category = request.form.get("category")
        latitude = float(request.form.get("latitude", 0.0))
        longitude = float(request.form.get("longitude", 0.0))
        image_file = request.files.get("image")
        
        # --- THIS IS THE FIX ---
        # Changed "user_uuid" to "uid" to match what the Flutter app sends.
        user_uid = request.form.get("uid") 

        if not all([description, category, latitude, longitude, image_file, user_uid]):
            return jsonify({"error": "Missing required form fields (including uid)"}), 400

        # --- 3. SAVE INITIAL UPLOAD TO FIRESTORE (image_url removed) ---
        report_doc_ref = db.collection('flutter_to_flask_to_Gemini').document()
        report_data = {
            "category": category,
            "description": description,
            "image_url": "removed_from_process", # Placeholder
            "latitude": latitude,
            "longitude": longitude,
            "pkey": report_doc_ref.id,
            "uuid": user_uid
        }
        report_doc_ref.set(report_data)
        print(f"Saved initial report to Firestore with key: {report_doc_ref.id}")

        # --- 4. PERFORM AI ANALYSIS & SAVE RESULT ---
        image_file.seek(0)
        ai_analysis_result = analyze_report(
            latitude=latitude, longitude=longitude, category=category,
            description=description, image_file=image_file
        )
        
        if "error" not in ai_analysis_result:
            analysis_doc_ref = db.collection('Gemini_to_Flask').document()
            analysis_data = ai_analysis_result.copy()
            analysis_data["pkey"] = report_doc_ref.id
            analysis_data["uuid"] = user_uid
            analysis_doc_ref.set(analysis_data)
            print("Saved AI analysis result to Firestore.")
        
        # --- 5. PERFORM GAMIFICATION SCORING & SAVE RESULT ---
        score_result = {}
        if "error" not in ai_analysis_result:
            score_result = calculate_score(
                analysis_data=ai_analysis_result,
                description=description, category=category
            )
            
            if "error" not in score_result:
                gamification_doc_ref = db.collection('Gamification').document()
                gamification_data = score_result.copy()
                gamification_data["pkey"] = report_doc_ref.id
                gamification_data["uuid"] = user_uid
                gamification_doc_ref.set(gamification_data)
                print("Saved gamification score result to Firestore.")

                # --- 6. UPDATE USER'S TOTAL POINTS ---
                total_score_earned = gamification_data.get("total_score", 0)
                if total_score_earned > 0:
                    user_ref = db.collection('users').document(user_uid)
                    user_ref.update({
                        'points': firestore.Increment(total_score_earned)
                    })
                    print(f"Updated user {user_uid} points by {total_score_earned}.")

        # --- 7. RETURN SUCCESS RESPONSE ---
        return jsonify({
            "message": "Data processed successfully (image not stored).",
            "report_id": report_doc_ref.id,
            "initial_analysis": ai_analysis_result,
            "final_score": score_result
        }), 200

    except Exception as e:
        print(f"An error occurred in the /upload route: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

# -------------------- MAIN --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)