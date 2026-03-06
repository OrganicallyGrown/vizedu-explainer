from io import BytesIO
from pydub import AudioSegment
import os
import uuid
from google import genai
from google.genai.types import GenerateContentConfig
from google.cloud import storage, texttospeech

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="us-central1"   
)

storage_client = storage.Client()
tts_client = texttospeech.TextToSpeechClient()
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def generate_interleaved_explanation(topic: str, age: str = "12", length: str = "medium", style: str = "fun") -> dict:
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
    top_p=0.92,
    top_k=40,
    max_output_tokens=2048,        
    candidate_count=1,

)

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=config
    )

    parts = response.candidates[0].content.parts
    narration = ""
    image_bytes_list = []

    for part in parts:
        if part.text:
            narration += part.text + "\n\n"
        if part.inline_data:
            image_bytes_list.append(part.inline_data.data)

    # Save images
    image_urls = []
    for img_bytes in image_bytes_list:
        blob_name = f"images/{uuid.uuid4()}.jpg"
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(img_bytes, content_type="image/jpeg")
        blob.make_public()
        image_urls.append(blob.public_url)

    # TTS narration - Split narration into chunks < 4500 chars (~safe under 5000 bytes)
    def chunk_text(text, max_bytes=4500):
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

    # Generate audio for each chunk
    audio_contents = []
    for idx, chunk in enumerate(narration_chunks):
        if not chunk.strip():
            continue
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response_chunk = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        audio_contents.append(response_chunk.audio_content)

    # Concatenate all MP3 chunks into one (using pydub)
    from pydub import AudioSegment
    from io import BytesIO

    final_audio = AudioSegment.empty()
    for content in audio_contents:
        chunk_audio = AudioSegment.from_file(BytesIO(content), format="mp3")
        final_audio += chunk_audio

    # Export final audio to bytes
    final_audio_io = BytesIO()
    final_audio.export(final_audio_io, format="mp3")
    final_audio_bytes = final_audio_io.getvalue()

    # Upload the concatenated audio to GCS
    audio_blob_name = f"audio/{uuid.uuid4()}.mp3"
    bucket = storage_client.bucket(BUCKET_NAME)
    audio_blob = bucket.blob(audio_blob_name)
    audio_blob.upload_from_string(final_audio_bytes, content_type="audio/mpeg")
    audio_blob.make_public()
    audio_url = audio_blob.public_url

    return {
        "narration": narration,
        "image_urls": image_urls,
        "audio_url": audio_url,
        "topic": topic
    }