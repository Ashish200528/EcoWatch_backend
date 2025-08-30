import os
import uuid
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Import your existing Gemini analyzer functions
from gemini_analyzer import analyze_report, calculate_score

# --- 1. INITIALIZE FIREBASE ADMIN SDK ---
# This block runs once when the server starts.
load_dotenv()

# Use the credentials file you provided
cred = credentials.Certificate("firebase_credentials.json")

# Get the storage bucket name from your .env file
storage_bucket = os.getenv("STORAGE_BUCKET")
if not storage_bucket:
    raise ValueError("STORAGE_BUCKET environment variable not set in .env file.")

firebase_admin.initialize_app(cred, {
    'storageBucket': storage_bucket
})

# Get a client for Firestore and Storage services
db = firestore.client()
bucket = storage.bucket()

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
        user_uid = request.form.get("uid") # Get the User's UID from Flutter

        if not all([description, category, latitude, longitude, image_file, user_uid]):
            return jsonify({"error": "Missing required form fields (including uid)"}), 400

        # --- 3. UPLOAD IMAGE TO FIREBASE STORAGE ---
        # Create a unique filename to prevent overwrites
        image_filename = f"reports/{uuid.uuid4()}{os.path.splitext(image_file.filename)[1]}"
        blob = bucket.blob(image_filename)
        
        # Upload the file's content
        blob.upload_from_file(image_file, content_type=image_file.content_type)
        
        # Make the file publicly accessible and get its URL
        blob.make_public()
        image_url = blob.public_url
        print(f"Image uploaded successfully: {image_url}")

        # --- 4. SAVE INITIAL UPLOAD TO FIRESTORE ---
        report_doc_ref = db.collection('flutter_to_flask_to_Gemini').document()
        report_data = {
            "category": category,
            "description": description,
            "image_url": image_url,
            "latitude": latitude,
            "longitude": longitude,
            "pkey": report_doc_ref.id,
            "uuid": user_uid
        }
        report_doc_ref.set(report_data)
        print(f"Saved initial report to Firestore with key: {report_doc_ref.id}")

        # --- 5. PERFORM AI ANALYSIS & SAVE RESULT ---
        image_file.seek(0) # Reset file pointer for Gemini
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
        
        # --- 6. PERFORM GAMIFICATION SCORING & SAVE RESULT ---
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

                # --- 7. UPDATE USER'S TOTAL POINTS ---
                total_score_earned = gamification_data.get("total_score", 0)
                if total_score_earned > 0:
                    user_ref = db.collection('users').document(user_uid)
                    user_ref.update({
                        'points': firestore.Increment(total_score_earned)
                    })
                    print(f"Updated user {user_uid} points by {total_score_earned}.")

        # --- 8. RETURN SUCCESS RESPONSE ---
        return jsonify({
            "message": "Data processed and stored successfully.",
            "report_id": report_doc_ref.id,
            "image_url": image_url,
            "initial_analysis": ai_analysis_result,
            "final_score": score_result
        }), 200

    except Exception as e:
        print(f"An error occurred in the /upload route: {e}")
        traceback.print_exc() # Print full error for debugging
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

# -------------------- MAIN --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)

