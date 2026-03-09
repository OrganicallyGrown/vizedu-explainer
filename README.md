# VizEdu Explainer – Gemini Interleaved Educational Storyteller

**Description**  
VizEdu Explainer is an advanced multimodal AI agent that turns any topic into a rich, engaging educational storybook for children. Using **Gemini 2.5 Flash Image** (Vertex AI), it generates:

- Fluid narration text  
- Interleaved diagrams & illustrations (native image output)  
- Synchronized, high-quality voice narration (Cloud Text-to-Speech with selectable          kid-friendly voices)  

All in **one cohesive response stream** — no separate calls or post-processing for visuals.

### Features
- Natural language input: topic + age + length + style + **voice style**  
- Native interleaved output: story paragraphs + diagrams appear together  
- Three selectable Neural2 voices:  
  - Youthful Female (Fun & Energetic) – en-US-Neural2-F  
  - Energetic Male (Exciting & Bold) – en-US-Neural2-D  
  - Warm Friendly Female (Gentle & Clear) – en-US-Neural2-J  
- Handles long narrations with automatic TTS chunking & audio concatenation  
- Assets stored in Cloud Storage with public URLs  
- Friendly error handling & quota retry logic  
- Fully deployed on **Google Cloud Run** with optional Terraform IaC

## Architecture

The system is built entirely on Google Cloud:

- Frontend: Gradio UI (hosted on Cloud Run)
- Core AI: Gemini 2.5-flash-image via Vertex AI (interleaved text + images)
- Voice narration: Cloud Text-to-Speech
- Asset storage & delivery: Cloud Storage

See the full horizontal diagram in [architecture.md](./architecture.md)

### Technologies Used
- **Gemini model**: gemini-2.5-flash-image (Vertex AI) – native interleaved TEXT + IMAGE  
- **Framework**: Google GenAI SDK  
- **Frontend**: Gradio (real-time UI with voice dropdown, markdown, gallery, audio player)  
- **Backend & Hosting**: Google Cloud Run (Dockerfile + gcloud deploy)  
- **Storage**: Google Cloud Storage (images & audio)  
- **Text-to-Speech**: Google Cloud Text-to-Speech (Neural2 voices + pydub/ffmpeg chunking)  
- **Other**: tenacity (quota retry), python-dotenv, Pillow  
- **Deployment**: gcloud CLI + optional Terraform IaC

### Local Spin-up (2 commands)
```bash
pip install -r requirements.txt
python app.py