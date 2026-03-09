import os
import uuid
from io import BytesIO

from google import genai
from google.genai.types import GenerateContentConfig
from google.cloud import storage, texttospeech
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
from pydub import AudioSegment


# ====================== CLIENT SETUP ======================
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"
)

storage_client = storage.Client()
tts_client = texttospeech.TextToSpeechClient()
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


# ====================== RETRY DECORATOR ======================
@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    reraise=True
)
def call_gemini(prompt: str, config: GenerateContentConfig):
    return client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=config
    )


# ====================== MAIN FUNCTION ======================
def generate_interleaved_explanation(
    topic: str,
    age: str = "12",
    length: str = "medium",
    style: str = "fun",
    voice_name: str = "en-US-Neural2-F"     # ← new parameter + default youthful female
) -> dict:
    
    prompt = f"""Create a short, fun, engaging educational explanation about "{topic}" for a {age}-year-old in a {style} style.

- Start directly with the story narration — no thinking, planning, outlining, notes, or meta-comments.
- Make it vivid and exciting with kid-friendly analogies.
- Keep narration short ({length} length).
- After each key paragraph (1-3 sentences), generate one relevant diagram or illustration to explain that part visually.
- Use clear labels in diagrams when needed.
- Output only the final narration and interleaved images."""

    config = GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_output_tokens=2048,
        candidate_count=1
    )

    try:
        response = call_gemini(prompt, config)
    except Exception as e:
        print(f"Gemini call failed: {str(e)}")
        
        fallback_text = "Oops! Gemini is a bit busy right now.\n\nTry a shorter topic or wait a moment and try again! 🌱"
        
        # Optional fallback audio
        try:
            synthesis_input = texttospeech.SynthesisInput(text="Sorry! Gemini is busy right now. Try a shorter topic.")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-F"   # neutral fallback voice
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            fallback_tts = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            
            blob_name = f"audio/fallback_{uuid.uuid4()}.mp3"
            blob = storage_client.bucket(BUCKET_NAME).blob(blob_name)
            blob.upload_from_string(fallback_tts.audio_content, content_type="audio/mpeg")
            blob.make_public()
            fallback_audio_url = blob.public_url
        except:
            fallback_audio_url = None

        return {
            "narration": fallback_text,
            "image_urls": [],
            "audio_url": fallback_audio_url,
            "topic": topic
        }

    # ====================== PROCESS RESPONSE ======================
    parts = response.candidates[0].content.parts
    narration = ""
    image_bytes_list = []

    for part in parts:
        if part.text:
            narration += part.text + "\n\n"
        if part.inline_data:
            image_bytes_list.append(part.inline_data.data)

    # ====================== SAVE IMAGES ======================
    image_urls = []
    bucket = storage_client.bucket(BUCKET_NAME)
    for img_bytes in image_bytes_list:
        blob_name = f"images/{uuid.uuid4()}.jpg"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(img_bytes, content_type="image/jpeg")
        blob.make_public()
        image_urls.append(blob.public_url)

    # ====================== TTS WITH CHUNKING + SELECTED VOICE ======================
    def chunk_text(text: str, max_bytes: int = 4500):
        chunks = []
        current = ""
        for line in text.split("\n"):
            if len(current.encode('utf-8')) + len(line.encode('utf-8')) + 1 > max_bytes:
                chunks.append(current.strip())
                current = line
            else:
                current += "\n" + line if current else line
        if current:
            chunks.append(current.strip())
        return chunks

    narration_chunks = chunk_text(narration)
    audio_contents = []

    for chunk in narration_chunks:
        if not chunk.strip():
            continue
        
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        
        # Use the selected voice name passed from the UI
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        audio_contents.append(tts_response.audio_content)

    # Concatenate audio chunks
    final_audio = AudioSegment.empty()
    for content in audio_contents:
        chunk_audio = AudioSegment.from_file(BytesIO(content), format="mp3")
        final_audio += chunk_audio

    final_audio_io = BytesIO()
    final_audio.export(final_audio_io, format="mp3")
    final_audio_bytes = final_audio_io.getvalue()

    # Upload final audio
    audio_blob_name = f"audio/{uuid.uuid4()}.mp3"
    audio_blob = bucket.blob(audio_blob_name)
    audio_blob.upload_from_string(final_audio_bytes, content_type="audio/mpeg")
    audio_blob.make_public()

    return {
        "narration": narration,
        "image_urls": image_urls,
        "audio_url": audio_blob.public_url,
        "topic": topic
    }