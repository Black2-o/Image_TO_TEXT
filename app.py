from flask import Flask, request, render_template, send_file
from google import genai
import PIL.Image
import os

# Access the API key
API_KEY = os.getenv("API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Define the path for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Route for uploading image and processing
@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Check if the post request has the image part
        if 'image' not in request.files:
            return 'No image part'
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return 'No selected image'
        
        if image_file:
            # Save the uploaded image
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(image_path)
            
            # Process the image with genai
            image = PIL.Image.open(image_path)
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Can You Give Me all The Text From Bangla also English and if there are any numbers also that? I just need all the text.", image]
            )
            
            text = response.text
            # Save the text to a file
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.txt")
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(text)
            
            return render_template('result.html', text=text)
    
    return render_template('upload.html')

# Route to download the processed output
@app.route('/download')
def download_file():
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'output.txt'), as_attachment=True)

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
