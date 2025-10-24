from typing import Annotated, Sequence, TypedDict, Optional, List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import os
import sqlite3
import json

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
# Cargar .env para GOOGLE_API_KEY y otras variables de entorno
load_dotenv()

# Estado del agente
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Tools a utilizar
def _rows_to_dicts(cursor, rows):
    cols = [d[0] for d in cursor.description] if cursor.description else []
    out = [dict(zip(cols, r)) for r in rows]
    return cols, out

@tool
def query_tool(query: str):
    """Herramienta para hacer consultas a la base de datos 'ventas' (SQLite).
    Acepta un SQL query. La tabla 'ventas' tiene el siguiente esquema:
    id INTEGER PRIMARY KEY,
    producto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio REAL NOT NULL,
    pais TEXT NOT NULL,
    fecha_venta DATE NOT NULL
    """
    conn = sqlite3.connect("ventas.db")
    
    # Para obtener nombres de columnas
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cols, dict_rows = _rows_to_dicts(cursor, rows)
        result = {"columns": cols, "rows": dict_rows, "executed_sql": query}
        # Devolvemos JSON para que el LLM pueda “leerlo”
        return json.dumps(result, ensure_ascii=False)
    
    except:
        print("Llamado a query_tool falló")
        
    finally:
        conn.close()

# Puedes limitar a solo query_tool si quieres:
TOOLS = [query_tool] 

# Modelo
'''
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key = os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    verbose=True,
).bind_tools(TOOLS)
'''

# Modelo con autenticación forzada
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set (Railway → Variables).")

# Forzar el uso de API key explícitamente
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=GOOGLE_API_KEY,
    project=None,  # Evitar que busque proyecto de GCP
    temperature=0,
    verbose=True,
).bind_tools(TOOLS)

# SYSTEM_PROMPT con lo que debe realizar el agente e información básica de la empresa
SYSTEM_PROMPT = SystemMessage(
    content=(
        "Eres un asistente con acceso a un tool para hacer consultas SQL sobre la base 'ventas'. "
        "Usa el tool cuando necesites datos y luego responde al usuario con un resumen claro. "
        "Si el tool devuelve información, interprétalo y explica el resultado."
        "También puedes responder información sobre la empresa TechNova"
        "La empresa TechNova vende productos electrónicos. Tiene un promedio de 5.000 ventas mensuales en Latinoamérica."
        "Sus categorías principales son smartphones, notebooks y accesorios."
    )
)

# NODOS

# Nodo del llm
def model_call(state: AgentState) -> AgentState:
    # Inyectamos el system en cada vuelta
    response = model.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}

# Nodo para definir si continuar o acabar el proceso
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "continue"
    return "end"

# Grafo
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)
tool_node = ToolNode(tools=TOOLS)
graph.add_node("tools", tool_node)
graph.set_entry_point("our_agent")
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {"continue": "tools", "end": END},
)
graph.add_edge("tools", "our_agent")
app = graph.compile()

# ---------- Runner de alto nivel ----------
def ask_agent(question: str):
    """
    Ejecuta el grafo para una sola pregunta (stateless).
    Devuelve la respuesta final, los tool_calls detectados y el último resultado del tool (si lo hubo).
    """
    # Arrancamos con un HumanMessage
    pregunta_humano = {"messages": [HumanMessage(content=question)]}

    # Creamos las variables para guardar información sobre la respuesta
    tool_calls = [] # Las llamadas que hace el LLM
    last_tool_json = None # Última respuesta del tool al LLM
    final_text = "" # Respuesta final del agente

    # Usamos stream para capturar llamadas a tools y la respuesta final
    for step in app.stream(pregunta_humano, stream_mode="values"):
        msgs = step["messages"]
        last = msgs[-1]

        # Se registra la información que pide el LLM a los tools
        if hasattr(last, "tool_calls"): # Si no tiene argumentos se coloca None
            for tool_message in last.tool_calls:
                tool_calls.append({
                    "tool_name": tool_message.get("name"),
                    "arguments": tool_message.get("args"),
                })

        # Si fue un ToolMessage, se manda la información que manda el tool query_tool
        if isinstance(last, ToolMessage):
            try:
                tool_payload = json.loads(last.content)
                # Se verifica que el contenido que mande el tool sea un diccionario para luego pasarlo como
                if isinstance(tool_payload, dict):
                    last_tool_json = tool_payload
            except Exception:
                print("Tool ha mandado el contenido incorrecto o ha fallado")
                pass

        # Si es mensaje final del modelo (AIMessage), guardamos el texto
        if hasattr(last, "content") and isinstance(last, AIMessage):
            final_text = last.content or final_text
            
    return (
        {
            'final_answer': final_text or "No se generó respuesta.",
            'tool_calls': tool_calls,
            'last_result': last_tool_json
        }
    )