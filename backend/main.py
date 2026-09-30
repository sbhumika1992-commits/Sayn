from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
from groq import Groq
import requests
import os
import tempfile

load_dotenv()

app = FastAPI(title="SAYN AI Voice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RIME_API_KEY = os.getenv("RIME_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


@app.get("/")
def home():
    return {
        "status": "SAYN backend running",
        "chat": bool(GROQ_API_KEY),
        "rime": bool(RIME_API_KEY)
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_path = None

    try:
        audio_data = await file.read()

        if not audio_data:
            return {"text": "", "error": "Empty audio file"}

        # IMPORTANT:
        # Chrome MediaRecorder normally sends WebM/Opus.
        # Keep the real extension instead of pretending it is WAV.
        original_name = file.filename or "sayn_voice.webm"
        extension = os.path.splitext(original_name)[1].lower()

        if extension not in {
            ".wav", ".webm", ".mp3", ".m4a",
            ".mp4", ".mpeg", ".mpga", ".ogg"
        }:
            extension = ".webm"

        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp:
            temp.write(audio_data)
            temp_path = temp.name

        if not client:
            return {"text": "", "error": "GROQ_API_KEY not configured"}

        with open(temp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                language="en",
                response_format="json"
            )

        text = (result.text or "").strip()

        print("USER:", text)

        return {"text": text}

    except Exception as e:
        print("TRANSCRIBE ERROR:", repr(e))
        return {"text": "", "error": str(e)}

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


@app.post("/chat")
async def chat(data: dict):
    try:
        message = (data.get("message") or "").strip()

        if not message:
            return {"response": ""}

        if not client:
            return {"response": "SAYN AI is not configured. Check GROQ_API_KEY."}

        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are SAYN, a helpful AI voice assistant.
Always answer in clear natural English unless
the user explicitly asks for another language.
Give the exact answer first.
Be concise but useful.
Do not invent facts.
Do not use emojis.
Do not use markdown.
Keep normal answers around 2 to 5 sentences.
"""
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.2,
            max_tokens=250
        )

        answer = (
            completion.choices[0].message.content or ""
        ).strip()

        print("SAYN:", answer)

        return {"response": answer}

    except Exception as e:
        print("CHAT ERROR:", repr(e))
        return {
            "response": "Sorry, I could not process that request."
        }


@app.post("/speak")
async def speak(data: dict):
    try:
        message = (data.get("message") or "").strip()

        if not message:
            return Response(
                content=b"",
                media_type="audio/wav"
            )

        if not RIME_API_KEY:
            return Response(
                content=b"",
                media_type="audio/wav"
            )

        url = "https://users.rime.ai/v1/rime-tts"

        headers = {
            "Authorization": f"Bearer {RIME_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": message,
            "speaker": "luna",
            "modelId": "arcana",
            "lang": "eng"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return Response(
            content=response.content,
            media_type="audio/wav"
        )

    except Exception as e:
        print("SPEECH ERROR:", repr(e))

        return Response(
            content=b"",
            media_type="audio/wav",
            status_code=500
        )
