import os
import gradio as gr
from vizedu_agent import generate_interleaved_explanation
from dotenv import load_dotenv

load_dotenv()

# Custom CSS for a professional, production-grade look
css = """
#container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}
.header-card {
    background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
    color: white !important;
    padding: 3rem 2rem;
    border-radius: 1.5rem;
    text-align: center;
    margin-bottom: 2.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}
.header-card h1 {
    font-size: 3.2rem !important;
    font-weight: 850 !important;
    margin-bottom: 0.5rem !important;
    color: white !important;
    letter-spacing: -0.025em;
}
.header-card p {
    font-size: 1.25rem !important;
    opacity: 0.9;
    color: white !important;
}
.config-panel {
    background: var(--background-fill-secondary);
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid var(--border-color-primary);
}
.output-panel {
    background: var(--background-fill-primary);
    border-radius: 1rem;
    padding: 1.5rem;
    border: 1px solid var(--border-color-primary);
}
.footer-text {
    text-align: center;
    margin-top: 4rem;
    padding: 2rem 0;
    border-top: 1px solid var(--border-color-primary);
    font-size: 0.95rem;
    opacity: 0.8;
}
/* Hide standard Gradio footer */
footer {
    display: none !important;
}
/* Markdown content styling */
#output-markdown {
    padding: 1.5rem;
    background: var(--background-fill-secondary);
    border-radius: 1rem;
    font-size: 1.1rem;
    line-height: 1.7;
    margin-bottom: 1.5rem;
}
.prose img {
    border-radius: 1rem;
    margin: 2rem 0;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
/* Button customizations */
#generate-btn {
    height: 3.5rem;
    font-weight: 600;
    font-size: 1.1rem;
}
/* Tab styling */
.tabs {
    border: none !important;
}
.tab-nav {
    border-bottom: 1px solid var(--border-color-primary) !important;
    margin-bottom: 1.5rem !important;
}
"""

def explain(topic, age, length, style, voice_choice):
    if not topic.strip():
        return "### ⚠️ Please enter a topic to begin.", None, []
    
    try:
        result = generate_interleaved_explanation(topic, age, length, style, voice_choice)
        
        narration_parts = [p.strip() for p in result['narration'].split('\n\n') if p.strip()]
        images = result.get("image_urls", [])
        
        interleaved_content = f"# {result['topic']}\n\n"
        
        for i, part in enumerate(narration_parts):
            interleaved_content += f"{part}\n\n"
            if i < len(images):
                interleaved_content += f"![Diagram {i+1}]({images[i]})\n\n"
                
        if len(images) > len(narration_parts):
            for i in range(len(narration_parts), len(images)):
                interleaved_content += f"![Diagram {i+1}]({images[i]})\n\n"

        return interleaved_content, result.get("audio_url"), images
    except Exception as e:
        return f"### ❌ Error during generation\n{str(e)}", None, []

# Professional theme configuration
theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    button_primary_background_fill="*primary_600",
    button_primary_background_fill_hover="*primary_700",
    block_radius="1rem",
)

with gr.Blocks(title="VizEdu Explainer") as demo:
    with gr.Column(elem_id="container"):
        # Custom Header Card
        gr.HTML("""
            <div class="header-card">
                <h1>📚 VizEdu Explainer</h1>
                <p>Transform complex topics into engaging educational stories with Gemini 2.5 Flash</p>
            </div>
        """)

        with gr.Row(equal_height=False):
            # Configuration Sidebar
            with gr.Column(scale=2, variant="panel", elem_classes="config-panel"):
                with gr.Group():
                    gr.Markdown("### ⚙️ Story Configuration")
                    topic = gr.Textbox(
                        label="Topic to Explain", 
                        placeholder="e.g., Quantum Entanglement, The Water Cycle",
                        value="How do plants make food",
                        lines=2
                    )
                
                with gr.Group():
                    with gr.Row():
                        age = gr.Dropdown(
                            choices=[
                                ("🧒 Child (8+)", "8"),
                                ("🧑 Teen (12+)", "12"),
                                ("🎓 Young Adult (16+)", "16"),
                                ("🧔 Adult", "adult")
                            ], 
                            label="Target Audience", 
                            value="12"
                        )
                        length = gr.Dropdown(
                            choices=[
                                ("⏱️ Short", "short"),
                                ("📝 Medium", "medium"),
                                ("📖 Long", "long")
                            ], 
                            label="Content Length", 
                            value="medium"
                        )
                
                style = gr.Radio(
                    choices=[
                        ("😊 Fun", "fun"),
                        ("🧠 Serious", "serious"),
                        ("🎨 Cartoon", "cartoon"),
                        ("👔 Professional", "professional"),
                        ("✨ Minimalist", "minimalist")
                    ], 
                    label="Visual & Tone Style", 
                    value="fun"
                )
                
                # New: Voice selection dropdown
                voice_choice = gr.Dropdown(
                    choices=[
                        ("Youthful Female (Fun & Energetic)", "en-US-Neural2-F"),
                        ("Energetic Male (Exciting & Bold)", "en-US-Neural2-D"),
                        ("Warm Friendly Female (Gentle & Clear)", "en-US-Neural2-J")
                    ],
                    label="Voice Style",
                    value="en-US-Neural2-F",  # default
                    interactive=True
                )
                
                generate_btn = gr.Button("✨ Generate Story", variant="primary", elem_id="generate-btn")
                
                with gr.Accordion("💡 Need inspiration?", open=False):
                    gr.Examples(
                        examples=[
                            ["How do black holes work?", "12", "medium", "cartoon"],
                            ["The history of the Roman Empire", "adult", "long", "serious"],
                            ["Why is the sky blue?", "8", "short", "fun"]
                        ],
                        inputs=[topic, age, length, style, voice_choice]
                    )

            # Output Area
            with gr.Column(scale=3, variant="panel", elem_classes="output-panel"):
                with gr.Tabs(elem_classes="tabs"):
                    with gr.TabItem("📖 Interactive Story"):
                        with gr.Group():
                            audio_out = gr.Audio(
                                label="🎙️ Narration Player", 
                                autoplay=False,
                                container=True
                            )
                            output_md = gr.Markdown(
                                label="Story Content", 
                                height=650,
                                elem_id="output-markdown"
                            )
                    
                    with gr.TabItem("🖼️ Visual Gallery"):
                        gallery = gr.Gallery(
                            label="Generated Illustrations", 
                            columns=2, 
                            object_fit="contain",
                            preview=True
                        )

        # Footer
        with gr.Row(elem_classes="footer-text"):
            with gr.Column():
                gr.Markdown("""
                    **VizEdu Explainer** • Powered by **Gemini-2.5-flash-image** • Multi-modal Generation • Vertex AI
                    
                    <small>Built for educational clarity and visual engagement.</small>
                """)
                theme_btn = gr.Button("🌓 Toggle Dark Mode", variant="secondary", size="sm")

    # Dark mode toggle logic
    theme_btn.click(
        None, 
        None, 
        None, 
        js="() => document.querySelector('body').classList.toggle('dark')"
    )

    # Generation trigger
    generate_btn.click(
        fn=explain, 
        inputs=[topic, age, length, style, voice_choice], 
        outputs=[output_md, audio_out, gallery],
        api_name="explain"
    )

# Enable queuing for robust multi-user handling
demo.queue(default_concurrency_limit=5)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 8080)),
        theme=theme,
        css=css
    )
