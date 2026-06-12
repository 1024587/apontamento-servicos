from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "online",
        "sistema": "apontamento-servicos"
    }