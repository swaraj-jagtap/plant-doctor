import os
from flask import Flask, request, render_template, jsonify
from datetime import datetime
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# It's recommended to handle the case where the API key might not be set
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)

# It's good practice to create the app instance first
app = Flask(__name__)

# --- Prompt Template ---
# Moved the prompt to a more readable format and made it more robust.
prompt_template = """You are a Plant Doctor and a friendly agent for "Vrindavan Garden Center" nursery.
Your primary goal is to help customers revive their plants and suggest solutions that involve purchasing products or services from our nursery.
**Under no circumstances should you suggest returning, discarding, or replacing the plant.** Focus on actionable solutions for revival.
Analyze the image of the plant and determine its health status.
Your response should be entirely in English and formatted clearly for a website.

First, clearly state in bold: **"The plant appears to be [Healthy/Unhealthy]."**

If the plant appears unhealthy:
1.  Provide a detailed diagnosis of the illness or issue.
2.  Suggest a comprehensive treatment plan, including specific steps and recommended dates starting from today (like a prescription).
3.  **Important:** If the diagnosis involves a fungus, pests (like mealybugs), nutrient deficiencies, or soil issues, strongly recommend visiting "Vrindavan Garden Center" for special assistance and necessary products (e.g., pesticides, fungicides, specific fertilizers, soil amendments, tools). Frame all solutions as opportunities for the customer to save their plant with our expert help.
4.  Recommend a date for the next checkup.

If the plant appears healthy:
1.  State that the plant is healthy.
2.  Provide general tips for maintaining its health, recommending general plant care products (like premium potting mix, slow-release fertilizer, or watering cans) available at "Vrindavan Garden Center."
3.  Recommend a date for the next checkup.

Today's date is {date}.
"""

# --- Routes ---

@app.route('/')
def home():
    """Renders the homepage."""
    # Assuming your homepage HTML file is named 'vrindavan_homepage.html'
    # and is located in the 'templates' folder.
    return render_template('vrindavan_homepage.html')

@app.route('/plant-doctor')
def plant_doctor():
    """Renders the AI Plant Doctor page."""
    # This serves the new plant_doctor.html file.
    return render_template('plant_doctor.html')

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """Handles the image upload and Gemini API call."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided.'}), 400
        
        image_file = request.files['image']
        
        # Use a try-except block for image opening to catch corrupted files
        try:
            image = Image.open(image_file.stream)
        except Exception as e:
            return jsonify({'error': f'Invalid or corrupted image file: {e}'}), 400

        # Format the prompt
        current_date = datetime.now().strftime("%B %d, %Y")
        formatted_prompt = prompt_template.format(date=current_date)

        # Call Gemini API
        model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
        
        # Generate content
        response = model.generate_content([formatted_prompt, image])

        # Check if the response has text
        if response.text:
            return jsonify({'diagnosis': response.text})
        else:
            # Handle cases where the model might not respond due to safety settings etc.
            return jsonify({'error': 'The model could not generate a response. This may be due to the content policy. Please try a different image.'}), 500

    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"An unexpected error occurred in /diagnose: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 to make the app accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)