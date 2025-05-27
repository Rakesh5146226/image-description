from flask import Flask, render_template, request, jsonify
import base64
import requests
import mimetypes

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAXswbyoxGHyK2XzwvZ6EBvl8QpBSERz1g"
# Use the newer model, as gemini-pro-vision is deprecated
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/caption", methods=["POST"])
def caption():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Detect mime type from filename
    mime_type, _ = mimetypes.guess_type(image_file.filename)
    if not mime_type:
        mime_type = "image/jpeg"  # fallback

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_b64
                        }
                    },
                    {
                        "text": "Describe this image"
                    }
                ]
            }
        ]
    }

    response = requests.post(GEMINI_URL, json=payload)
    print("API status code:", response.status_code)
    print("API response:", response.text)

    try:
        result = response.json()
        caption = result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Error parsing caption:", e)
        caption = "Could not generate caption."

    return jsonify({"caption": caption})

if __name__ == "__main__":
    app.run(debug=True)