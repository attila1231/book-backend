# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import base64



client = OpenAI(api_key=os.getenv("API_KEY"))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.161:8000/analyze-book"],  # Set your app domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-book")
async def analyze_book(file: UploadFile = File(...)):
    contents = await file.read()

    # Save uploaded file as temp
    with open("temp.jpg", "wb") as f:
        f.write(contents)

    try:
        # Encode the uploaded image to data URL
        encoded = base64.b64encode(contents).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{encoded}"

        # Create chat completion with image
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You will be provided with an image of a book cover. Please provide in bullet points the following information about the book: title, author, genre, summary, age-group, who is it for"},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
        )

        output_text = response.choices[0].message.content
        return {"result": output_text}

    except Exception as e:
        print("OpenAI error:", e)
        return {"error": str(e)}
