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