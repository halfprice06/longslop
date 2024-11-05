# Your LLM Project

A FastAPI-based application that integrates with LLMs.

## Setup

1. Clone the repository

## Dependencies

1. Install dependencies using `pip-tools`:
   ```bash
   pip install pip-tools
   pip-sync requirements.txt
   ```

## Environment Variables

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