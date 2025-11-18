from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests, json, os

app = FastAPI()

# CORS (libera acesso pro site e app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.get("/")
def home():
    return {"status": "online", "message": "Calvo Pensante API rodando!"}

@app.post("/chat")
def chat(payload: dict):
    user = payload.get("user", "anon")
    text = payload.get("text", "")

    memory = load_memory()
    history = memory.get(user, [])

    history.append({"role": "user", "content": text})

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct"),
            "messages": history
        }
    )

    result = response.json()
    reply = result["choices"][0]["message"]["content"]

    history.append({"role": "assistant", "content": reply})
    memory[user] = history[-10:]  
    save_memory(memory)

    return {"reply": reply}
