# Architecture Diagram

```mermaid
%%{init: {
  'theme': 'base',
  'flowchart': {
    'curve': 'basis',
    'nodeSpacing': 70,
    'rankSpacing': 90,
    'diagramPadding': 20
  },
  'themeVariables': {
    'primaryColor': '#e8f4fd',
    'primaryTextColor': '#000000',
    'primaryBorderColor': '#1565c0',
    'lineColor': '#333333',
    'fontSize': '14px'
  }
}}%%
graph LR
    A[User Browser<br>Gradio Interface] -->|HTTP / WebSocket| B[Cloud Run Service<br>vizedu-explainer]

    B -->|Gemini API call| C[Vertex AI<br>Gemini 2.5-flash-image]
    C -->|Interleaved TEXT + IMAGE| B

    B -->|Text-to-Speech request| D[Cloud Text-to-Speech API]
    D -->|MP3 audio| B

    B -->|Upload image/audio| E[Cloud Storage Bucket<br>assets]
    E -->|Public URLs| B
    B -->|Signed/Public URLs| A

    subgraph "Google Cloud"
        B
        C
        D
        E
    end