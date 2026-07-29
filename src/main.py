from fastapi import FastAPI
from services.perguntas import responder

# Inicia a aplicação
app = FastAPI(
    title="IA-RAG-API",
    description="Api desenvolvida com FastAPI para um modelo de conferencia de processos academicos",
    version="1.0.0"
)


# Rota inicial get
@app.get("/")
async def health():
    return {"message": "teste"}


@app.post("/")
async def get_pergunta(pergunta: str):
    
    resposta = responder(pergunta)

    return {
        "resposta": resposta
    }