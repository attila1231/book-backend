# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import base64



client = OpenAI(api_key="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")
app = FastAPI()
with open("temp.jpg", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{encoded}"

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

    # Save temp file for OpenAI
    with open("temp.jpg", "wb") as f:
        f.write(contents)

    try:
        with open("temp.jpg", "rb") as image_file:
            file_response = client.files.create(file=image_file, purpose="vision")
            file_id = file_response.id

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
