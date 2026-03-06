# Architecture Diagram

```mermaid
graph TD
    A[User Browser<br>Gradio Interface] -->|HTTP / WebSocket| B[Cloud Run Service<br>vizedu-explainer]

    B -->|Gemini API call| C[Vertex AI<br>Gemini 2.5-flash-image]
    C -->|Interleaved response<br>TEXT + IMAGE| B

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

    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333