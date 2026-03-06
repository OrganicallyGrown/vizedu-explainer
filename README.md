# VizEdu Explainer – Gemini Interleaved Educational Storyteller

**Description**  
VizEdu Explainer is an advanced multimodal AI agent that turns any topic into a rich, engaging educational storybook for children. Using **Gemini 2.5 Flash Image** (Vertex AI), it generates:

- Fluid narration text  
- Interleaved diagrams & illustrations (native image output)  
- Synchronized voice narration (Cloud Text-to-Speech)  

All in **one cohesive response stream** — no separate calls or post-processing for visuals.

### Features
- Natural language input: topic + age + length + style  
- Interleaved output: story paragraphs alternated with relevant diagrams  
- Voiceover audio automatically generated and playable  
- Assets stored in Cloud Storage with public URLs  
- Fully hosted on **Google Cloud Run**  
- Bonus: Terraform IaC files included (optional automated deployment)

### Technologies Used
- **Gemini model**: gemini-2.5-flash-image (native interleaved TEXT + IMAGE)  
- **Framework**: Google GenAI SDK + Vertex AI  
- **Backend**: Google Cloud Run (containerized with Dockerfile)  
- **Storage**: Cloud Storage (images & audio)  
- **TTS**: Cloud Text-to-Speech  
- **Frontend**: Gradio (real-time UI)  
- **Other**: pydub (audio concatenation), Terraform (IaC bonus)

### Local Spin-up (2 commands)
```bash
pip install -r requirements.txt
python app.py