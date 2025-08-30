import os
import json
import google.generativeai as genai
from PIL import Image
import io
import traceback

def analyze_report(latitude, longitude, category, description, image_file):
    """
    Sends the report data to the Gemini API using an API key.
    """
    try:
        print("\n--- [DEBUG] Using Gemini API Key Method ---")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        system_prompt = """You are an AI model whose task is to analyze mangrove monitoring data. You will be given user input as a JSON object containing latitude, longitude, a category, and a description, along with an image of the site. Your responsibilities are:
1. Verify whether the provided latitude and longitude falls inside or near a known mangrove region based on your knowledge.
2. Analyze the uploaded image and check if it is consistent with the given category and description.
3. Provide structured output in JSON format with confidence levels.
Return the output in the following format only, without any markdown formatting:
{
 "location_verification": "Location Verified / Not in Mangrove Region / Unclear",
 "location_confidence": "XX%",
 "image_category_verification": "Consistent / Inconsistent / Unclear",
 "category_confidence": "XX%",
 "location_remarks": "Short explanation of reasoning for location verification",
 "category_remarks": "Short explanation of reasoning for category verification"
}
"""
        
        user_prompt = f'{system_prompt}\n\nAnalyze this data: {{"lat": {latitude}, "lon": {longitude}, "category": "{category}", "description": "{description}"}}'
        
        # Process the image
        image_bytes = image_file.read()
        image_file.seek(0)  # Reset file pointer
        
        # Convert image bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        print("[DEBUG] Making API call to Gemini...")
        
        # Generate content with the model
        response = model.generate_content([user_prompt, image])

        full_response = response.text

        print("--- [DEBUG] Raw AI Response Received ---")
        print(full_response)
        print("--------------------------------------")

        # --- THIS IS THE FIX ---
        # Clean the response string to remove the markdown fences before parsing.
        cleaned_response = full_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:] # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3] # Remove ```
        
        print("[DEBUG] Cleaned JSON string before parsing.")
        
        # Parse the cleaned string
        return json.loads(cleaned_response)

    except Exception as e:
        print("\n--- [CRITICAL] AN EXCEPTION OCCURRED IN AI ANALYSIS ---")
        traceback.print_exc()
        print("------------------------------------------------------\n")
        return {"error": "An error occurred during AI analysis.", "details": str(e)}
    
def calculate_score(analysis_data, description, category):
    """
    Sends the initial analysis to a second Gemini model for scoring.
    """
    try:
        print("\n--- [DEBUG] Starting Score Calculation ---")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        
        # Configure the Gemini API (same as in analyze_report)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # The new system prompt for the scoring model
        system_prompt = """You are an AI model whose task is to evaluate mangrove monitoring submissions.  
You will be given structured verification data (from a previous AI analysis) and the original user-provided description and category.  
Your task is to calculate a score across multiple parameters and provide a breakdown with clear remarks based on the strict criteria provided.

Scoring Criteria (max 100 points):
1. Image Verification (max 50)  
 - If image_category_verification is "Consistent" → score 40–50  
 - If "Partially Consistent" → score 20–39  
 - If "Inconsistent" → score 0–19  

2. Description Quality (max 20)  
 - If description is clear, specific, and matches the image → 15–20  
 - If description is vague but somewhat relevant → 8–14  
 - If irrelevant/unclear → 0–7  

3. Correct Tagging (category) (max 10)  
 - If category matches image evidence → 8–10  
 - If somewhat correct → 4–7  
 - If incorrect → 0–3  

4. Valid Geo-tag (max 10)  
 - If location_verification is "Location Verified" with confidence >80% → 8–10  
 - If confidence 50–80% → 4–7  
 - If not verified / outside mangrove region → 0–3  

5. Bonus/Adjustment (+/-10, optional)  
 - Exceptional clarity, multiple angles, or community-level importance → + up to 10  
 - Misleading, unclear, or duplicated data → - up to 10  

Output Format (JSON only):
{
 "image_score": <int>,
 "description_score": <int>,
 "category_score": <int>,
 "geo_score": <int>,
 "bonus_adjustment": <int>,
 "total_score": <int>,
 "remarks": "Short summary highlighting strengths and weaknesses"
}
"""
        
        # Combine the first AI's analysis and the original user data into a new prompt
        input_for_scoring = {
            "initial_analysis_results": analysis_data,
            "original_user_description": description,
            "original_user_category": category
        }
        user_prompt = f"{system_prompt}\n\nEvaluate this submission:\n{json.dumps(input_for_scoring, indent=2)}"

        print("[DEBUG] Making API call to Gemini for scoring...")
        
        # Generate content with the model (same pattern as analyze_report)
        response = model.generate_content([user_prompt])

        full_response = response.text

        print("--- [DEBUG] Raw Score Response Received ---")
        print(full_response)
        print("-----------------------------------------")

        # Clean the response string
        cleaned_response = full_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        
        return json.loads(cleaned_response)

    except Exception as e:
        print("\n--- [CRITICAL] AN EXCEPTION OCCURRED IN SCORE CALCULATION ---")
        traceback.print_exc()
        print("-----------------------------------------------------------\n")
        return {"error": "An error occurred during score calculation.", "details": str(e)}
