from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent_runtime import ask_agent
import os
from typing import Optional
from dotenv import load_dotenv  
load_dotenv()


# Crear instancia del API
app = FastAPI(title="Text-to-SQL Agent (LangGraph + Gemini)", version="1.0.0")

# Configuración de API Key
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API keys from environment variable (more secure)
def get_valid_api_keys():
    api_key = os.getenv("API_KEY")
    return api_key

VALID_API_KEYS = get_valid_api_keys()
async def validate_api_key(api_key: Optional[str] = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=401, 
            detail="API Key required. Please include 'X-API-Key' in headers."
        )
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API Key"
        )
    
    return api_key

# Configuraciones de comunicación
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir la estructura de la pregunta del Frontend
class AskRequest(BaseModel):
    question: str
    
# Serve static files (CSS, JS, images if any)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve your main frontend page
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

# Endpoint para verificar que el API responda
@app.get("/health")
def health():
    return {"status": "Estamos Arriba"}

# Endpoint para preguntas
@app.post("/ask")
def ask(req: AskRequest, api_key: str = Depends(validate_api_key)):
    # Se valida que la pregunta no esté vacia
    q = (req.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="Pregunta vacía.")

    # Se llama al agente
    try:
        result = ask_agent(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando el agente: {e}")

    # Se prepara la salida
    payload = {
        "final_answer": result['final_answer'],
        "tool_calls": result['tool_calls'],
        "result": result['last_result'] 
    }

    return payload