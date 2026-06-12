from fastapi import FastAPI
from supabase import create_client
import os

app = FastAPI()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

@app.get("/")
def home():
    return {
        "status": "online",
        "sistema": "apontamento-servicos"
    }

@app.get("/funcionarios")
def funcionarios():
    resultado = supabase.table("Funcionarios").select("*").execute()
    return resultado.datac