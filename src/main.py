from fastapi import FastAPI
from services.perguntas import responder
from services.auth import cria_usuario
from services.auth import autenticar_usuario
from services.vetorizacao import main

# Inicia a aplicação
app = FastAPI(
    title="IA-RAG-API",
    description="Api desenvolvida com FastAPI",
    version="1.0.0"
)


# Rota inicial get
@app.get("/")
async def health():
    return {"message": "teste"}


@app.post("/criar_usuario")
async def criar_usuario(username: str, email: str, password: str):
    
    resposta = cria_usuario(username, email, password)

    return resposta


@app.post("/autenticar_usuario")
async def autenticar_usuario(email: str):

    user = autenticar_usuario(email)

    return {
        "mensagem": "Usuário autenticado com sucesso" if user else "Usuário não encontrado",
    }

# Perguntas para a LLM
@app.post("/prompt")
async def get_pergunta(pergunta: str):
    
    resposta = responder(pergunta)

    return {
        "resposta": resposta
    }


# Treinamento do modelo
@app.post("/treinamento_modelo")
async def treina_modelo():
    
    main()

    return {
        "resposta": "Modelo treinado"
    }


@app.post("/cria_database")
async def cria_database():
    from services.database import Base, engine

    Base.metadata.create_all(engine)

    return {
        "resposta": "Database criada"
    }