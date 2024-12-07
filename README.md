# LongSlop - AI Story and Article Generator

LongSlop is a demonstration project that uses Large Language Models (LLMs) and text-to-speech (TTS) services to generate long-form written content—such as articles or short stories—along with an audio narration. It provides a frontend interface where users can input a topic, select a writing style and length, and then watch as the article’s plan, outline, revisions, and final text are progressively generated and displayed.

This project leverages:
- **FastAPI** for the backend web server and streaming endpoints.
- **OpenAI** or **Anthropic** LLM APIs for content generation.
- **ElevenLabs** TTS for converting the final text into audio.
- **SQLite** for logging LLM calls.
- **Tailwind CSS** and vanilla JavaScript for a responsive frontend UI.
- **Server-Sent Events (SSE)** for real-time progress updates.

## Key Features

1. **Dynamic Content Generation**:  
   Users enter a topic and choose a writing style (e.g., Hemingway, Jane Austen, The Economist) and an article length (short, medium, long). The system:
   - Generates an initial narrative plan.
   - Converts that plan into a structured outline.
   - Critiques and refines the plan.
   - Produces a fully written article or short story, in the requested style, while avoiding specified forbidden words.
   
2. **Multi-Step Streaming Process**:
   The frontend receives updates via SSE:
   - **Plan**: Initial brainstorming output.
   - **Outline**: Hierarchical structure of the piece.
   - **Revised Plan**: Improved narrative strategy.
   - **Revised Outline**: Enhanced structured outline.
   - **Article**: The final written content.
   - **Audio** (optional): A synthesized .mp3 file narrating the article.

3. **Style Transfer and Forbidden Words Enforcement**:  
   The system attempts to write in a specified literary style. It applies strict filters to remove forbidden words or phrases, retrying if necessary.

4. **Text-to-Speech Integration**:  
   If enabled, the project uses ElevenLabs TTS to generate an audio file of the completed story. Different speakers (characters, narrator) are assigned distinct voices.

5. **Backend Database Logging**:  
   SQLite is used to record LLM calls, enabling auditing and future analysis.

## Project Structure

```
./
├── app
│   ├── constants
│   │   ├── __init__.py
│   │   ├── forbidden_words.py
│   │   ├── sample_scene_script.py
│   │   └── writing_styles.py
│   ├── routes
│   │   └── article_routes.py
│   ├── services
│   │   ├── audio_service.py
│   │   └── llm_service.py
│   ├── database.py
│   └── schemas.py
├── frontend
│   ├── backup (Previous versions of UI)
│   │   ├── index.html
│   │   ├── script.js
│   │   └── styles.css
│   ├── index.html (Main UI)
│   ├── script.js
│   └── style.css
└── main.py (FastAPI application entry)
```

### Notable Files

- **app/constants/writing_styles.py**: Defines available literary styles.
- **app/constants/forbidden_words.py**: Lists forbidden words to omit from generated text.
- **app/services/llm_service.py**: Primary logic for content generation using LLMs, structuring, style enforcement, and scene extraction.
- **app/services/audio_service.py**: Integrates with ElevenLabs TTS to create audio segments from script lines and stitch them together.
- **frontend/index.html**: The main user interface that uses SSE to display progress and final results.

## Requirements

- Python 3.9+
- OpenAI API Key and/or Anthropic API Key
- ElevenLabs API Key (for TTS)
- A `.env` file containing the required API keys, for example:
  ```
  OPENAI_API_KEY=your_openai_key
  ANTHROPIC_API_KEY=your_anthropic_key
  ELEVENLABS_API_KEY=your_elevenlabs_key
  DEBUG=true
  ```

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/longslop.git
   cd longslop
   ```

2. **Install Dependencies**:
   It’s recommended to use a virtual environment.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Add the `.env` File**:
   Create a `.env` file in the project root and add your API keys and configurations as mentioned above.

4. **Run the Server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The application will be available at [http://localhost:8000/frontend/](http://localhost:8000/frontend/).

## Usage

- Navigate to [http://localhost:8000/frontend/](http://localhost:8000/frontend/) in your browser.
- Enter a topic, choose a style and length, optionally toggle including headers or audio.
- Click "Generate". The UI will show the planning, outlining, revising steps, and finally the article’s full text.  
- If audio generation is enabled, the project will produce an MP3 file and provide a player for you to listen.

## Notes and Caveats

- **Experimental**: This is a demonstration project and may require refinement for production use.
- **LLM Costs**: Using OpenAI or Anthropic APIs will incur costs. Ensure you have billing set up and be mindful of usage.
- **Forbidden Words**: The code attempts to remove certain words. Some stylistic constraints might reduce creativity or require fine-tuning.
- **Audio Generation**: ElevenLabs TTS usage also has associated costs and limitations. The code currently assigns hardcoded voice IDs to speakers.
- **Local Development**: SSE and CORS are configured for local testing. For production, you may need stricter CORS rules and better error handling.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests. Please follow standard GitHub etiquette and include comprehensive commit messages and documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.