from fastapi import FastAPI, Request, Query
from supabase import create_client
from datetime import datetime
import json
import os

app = FastAPI()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

VERIFY_TOKEN = "AGUIATEC123"


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

    apontamento_aberto = (
        supabase
        .table("Apontamentos")
        .select("*")
        .eq("funcionario_id", funcionario_id)
        .in_("status", ["aberto", "aguardando_servico"])
        .execute()
    )

    if apontamento_aberto.data:
        return {
            "erro": "Já existe um apontamento em andamento para este funcionário"
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
        "saida": datetime.utcnow().isoformat(),
        "status": "aguardando_servico"
    }).eq("id", apontamento_id).execute()

    return {
        "sucesso": True,
        "mensagem": "Qual serviço foi realizado?"
    }


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
        .eq("status", "aguardando_servico")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if not apontamento.data:
        return {"erro": "Nenhum apontamento aguardando serviço"}

    apontamento_id = apontamento.data[0]["id"]

    supabase.table("Apontamentos").update({
        "servico": servico,
        "status": "fechado"
    }).eq("id", apontamento_id).execute()

    return {
        "sucesso": True,
        "mensagem": "Apontamento finalizado"
    }


@app.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):

    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return {"erro": "Token inválido"}


@app.post("/webhook")
async def receber_webhook(request: Request):

    dados = await request.json()

    print("")
    print("======================================")
    print("WEBHOOK RECEBIDO")
    print("======================================")

    print(json.dumps(dados, indent=2, ensure_ascii=False))

    try:

        valor = dados["entry"][0]["changes"][0]["value"]

        if "messages" in valor:

            mensagem = valor["messages"][0]

            telefone = mensagem.get("from", "")

            texto = ""

            if mensagem.get("type") == "text":
                texto = mensagem["text"]["body"].strip()

            print("")
            print("######## MENSAGEM DETECTADA ########")
            print("TELEFONE:", telefone)
            print("TEXTO:", texto)
            print("###################################")
            print("")

            comando = texto.lower().strip()

print("COMANDO RECEBIDO =", repr(comando))

if comando == "entrada":

    print("ENTROU EM ENTRADA")
    resultado = registrar_entrada(telefone)

elif comando == "saida":

    print("ENTROU EM SAIDA")
    resultado = registrar_saida(telefone)

else:

    print("ENTROU EM SERVICO")
    resultado = registrar_servico(
        telefone,
        texto
    )

                print("")
                print("RESULTADO SERVICO:")
                print(resultado)
                print("")

        else:

            print("")
            print("Evento recebido sem campo messages")
            print("")

    except Exception as erro:

        print("")
        print("ERRO AO PROCESSAR WEBHOOK")
        print(str(erro))
        print("")

    return {"status": "ok"}