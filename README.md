# nonslop

An AI-powered article generator that creates well-structured articles in various styles and lengths.

## Features

- Generate articles on any topic with customizable length and style.
- Supports multiple AI providers: OpenAI and Anthropic (Claude).
- Provides planning stages with an initial plan and structured outline.
- Backend API built with FastAPI in Python.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/nonslop.git
   cd nonslop
   ```

2. **Install dependencies using `pip-tools`**:
   ```bash
   pip install pip-tools
   pip-sync requirements.txt
   ```

3. **Set up environment variables**:

   Create a `.env` file at the root of the project and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure

- `main.py`: Sets up the FastAPI application, including middleware, routes, and error handling.
- `app/services/llm_service.py`: Contains services for generating articles using OpenAI and Anthropic APIs.