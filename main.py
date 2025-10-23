from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_runtime import ask_agent

# Crear instancia del API
app = FastAPI(title="Text-to-SQL Agent (LangGraph + Gemini)", version="1.0.0")

# Configuraciones de comunicación, se da permiso a todo
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

# Endpoint para verificar que el API responda
@app.get("/health")
def health():
    return {"status": "Estamos Arriba"}

# Endpoint para preguntas
@app.post("/ask")
def ask(req: AskRequest):
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