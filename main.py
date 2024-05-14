from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import json
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

import os
import json
import requests

from openai import OpenAI


load_dotenv()

# OpenAI.api_key = os.getenv("OPEN_AI_KEY")
# OpenAI.organization = os.getenv("OPEN_AI_ORG")
# client = OpenAI(api_key="OPEN_AI_KEY")

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY"),
    organization=os.environ.get("OPEN_AI_ORG"),
)

elevenlabs_key = os.getenv("ELEVENLABS_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add the origin of your React.js frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# @app.post("/talk")
# async def post_audio(file: UploadFile):
#     user_message = await transcribe_audio(file)
#     chat_response = get_chat_response(user_message)
#     audio_output = text_to_speech(chat_response)

#     def iterfile():   
#         yield audio_output  

#     return StreamingResponse(iterfile(), media_type="audio/mpeg")
  

import ffmpeg
import tempfile

@app.post("/talk")
async def post_audio(file: UploadFile):
    # Convert the uploaded file to MPEG format

    file_content = await file.read()
    print("File content: ", file)

    try:
        # Now continue with your existing logic
        # file = await convert_to_mpeg(file)
        # Write the binary data to a temporary file
        with open("audio.wav", "wb") as audio_file:
            audio_file.write(file_content)

        # Convert the WAV file to MPEG format using ffmpeg
        ffmpeg.input("audio.wav").output("audio.mp3", y="-y").run()

        # Read the converted MPEG file
        with open("audio.mp3", "rb") as mpeg_file:
            audio_output = mpeg_file.read()

        user_message = await transcribe_audio(file)
        chat_response = get_chat_response(user_message)
        audio_output = text_to_speech(chat_response)

        def iterfile():
            yield audio_output

        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    except Exception as e:
        error_message = {"error": str(e)}
        return JSONResponse(content=json.dumps(error_message), status_code=200)
    

# import os
# import tempfile
# import mimetypes
# import shutil

# async def transcribe_audio(file_data):
#     try:
#         if isinstance(file_data, str):
#             # If file_data is a string, assume it's a file path and read its content as bytes
#             with open(file_data, "rb") as file:
#                 file_bytes = file.read()
#         elif isinstance(file_data, bytes):
#             # If file_data is already bytes, use it directly
#             file_bytes = file_data
#         else:
#             # If file_data is neither a string nor bytes, raise an error
#             raise ValueError("Input data must be either a file path or bytes.")

#         # Pass the file bytes to the transcription service
#         transcription = client.audio.transcriptions.create(            
#             model="whisper-1", 
#             file=file_bytes
#         )
#         print(transcription.text)
#         return transcription.text
    
#     except Exception as e:
#         # If an error occurs during transcription, raise an HTTPException with the error message
#         raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {e}")

# import subprocess
# import shutil
# import os
# import asyncio
# from fastapi import HTTPException

# async def convert_to_mpeg(file: UploadFile) -> str:
#     try:
#         # Define the output MPEG file path
#         output_filename = "converted_audio.mpeg"

#         # Use ffmpeg to convert the uploaded file to MPEG format
#         process = await asyncio.create_subprocess_exec(
#             "ffmpeg", "-i", "-", output_filename,
#             stdin=asyncio.subprocess.PIPE,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )

#         # Write the uploaded file's content to the stdin of the ffmpeg process
#         stdout, stderr = await process.communicate(file.file.read())

#         # Check if ffmpeg process exited successfully
#         if process.returncode != 0:
#             # If conversion fails, raise an HTTPException with an error message
#             raise HTTPException(status_code=500, detail=f"Failed to convert file to MPEG format: {stderr.decode()}")

#         return output_filename

#     except Exception as e:
#         # If any error occurs during the conversion process, raise an HTTPException with an error message
#         raise HTTPException(status_code=500, detail=f"Failed to convert file to MPEG format: {e}")



import io

#Functions
async def transcribe_audio(file):
    audio_file = open(file.filename, "rb")
    # mime_type = mimetypes.guess_type("audio.mpeg")[0]

    # if(mime_type == "audio/mpeg"):
    #     mime_type = "audio/mpeg3"

    # file_object = open(file, "rb")
   
    # contents = await file.read()

    transcription = client.audio.transcriptions.create(            
        model="whisper-1", 
        file=audio_file
    )
    print(transcription.text)
    return transcription.text

def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})

    gpt_response = gpt_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages = messages
                    )
    
    # parsed_gpt_response = gpt_response['choices'][0]['message']['content']

    parsed_gpt_response = gpt_response.choices[0].message.content

    save_messages(user_message, parsed_gpt_response)

    return parsed_gpt_response


def load_messages():
    messages = []
    file = 'database.json'

    empty = os.stat(file).st_size == 0

    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    else:
        messages.append(
            {"role": "system", "content": "You are interviewing the user for a front-end React developer position. \
              Ask short questions that are relevant to a junior level developer. Your name is Ace. The user is Geo. \
              Keep responses under 30 words and be funny sometimes"}
        )
    return messages

def save_messages(user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})
    # messages.append(user_message)
    # messages.append(gpt_response)
    with open(file, 'w') as f:
        json.dump(messages, f)

def text_to_speech(text):
    # voice_id = 'GBv7mTt0atIp3Br8iCZE'
    voice_id = '7WiFw1ITUvZ7Fre0fSQO'

    body = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key
    }

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        # response = requests.post(url, json=body, headers=headers)
        response = requests.request("POST", url, json=body, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print('something went wrong')
    except Exception as e:
        print(e)