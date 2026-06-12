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

    # Verifica se já existe apontamento aberto
    apontamento_aberto = (
        supabase
        .table("Apontamentos")
        .select("*")
        .eq("funcionario_id", funcionario_id)
        .eq("status", "aberto")
        .execute()
    )

    if apontamento_aberto.data:
        return {
            "erro": "Já existe um apontamento aberto para este funcionário"
        }

    supabase.table("Apontamentos").insert({
        "funcionario_id": funcionario_id,
        "entrada": datetime.utcnow().isoformat(),
        "status": "aberto"
    }).execute()

    return {
        "sucesso": True,
        "funcionario": funcionario.data[0]["nome"]
    }

@app.post("/saida")
def registrar_saida(telefone: str):

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

    apontamento = (
        supabase
        .table("Apontamentos")
        .select("*")
        .eq("funcionario_id", funcionario_id)
        .eq("status", "aberto")
        .execute()
    )

    if not apontamento.data:
        return {"erro": "Nenhum apontamento aberto"}

    apontamento_id = apontamento.data[0]["id"]

    supabase.table("Apontamentos").update({
        "saida": datetime.utcnow().isoformat()
    }).eq("id", apontamento_id).execute()

    return {
        "sucesso": True,
        "mensagem": "Qual serviço foi realizado?"
    }

@app.post("/servico")
def registrar_servico(telefone: str, servico: str):

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

    apontamento = (
        supabase
        .table("Apontamentos")
        .select("*")
        .eq("funcionario_id", funcionario_id)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not apontamento.data:
        return {"erro": "Apontamento não encontrado"}

    apontamento_id = apontamento.data[0]["id"]

    supabase.table("Apontamentos").update({
        "servico": servico,
        "status": "fechado"
    }).eq("id", apontamento_id).execute()

    return {
        "sucesso": True,
        "mensagem": "Apontamento finalizado"
    }