from fastapi import FastAPI
from supabase import create_client
from datetime import datetime
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
    return resultado.data

@app.post("/entrada")
def registrar_entrada(telefone: str):

    funcionario = (
        supabase
        .table("Funcionarios")
        .select("*")
        .eq("telefone", telefone)
        .execute()
    )

    if not funcionario.data:
        return {"erro": "Funcionário não encontrado"}

    funcionario_id = funcionario.data[0]["id"]

    supabase.table("Apontamentos").insert({
        "funcionario_id": funcionario_id,
        "entrada": datetime.utcnow().isoformat(),
        "status": "aberto"
    }).execute()

    return {
        "sucesso": True,
        "funcionario": funcionario.data[0]["nome"]
    }