from fastapi import FastAPI, UploadFile, File

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
    from services.auth import cria_usuario
    
    resposta = cria_usuario(username, email, password)

    return resposta


@app.post("/autenticar_usuario")
async def autenticar_usuario(email: str):
    from services.auth import autenticar_usuario

    user = autenticar_usuario(email)

    return {
        "mensagem": "Usuário autenticado com sucesso" if user else "Usuário não encontrado",
    }


# Perguntas para a LLM
@app.post("/prompt")
async def get_pergunta(pergunta: str, email: str):
    from services.perguntas import responder
    
    resposta = responder(pergunta, email)

    return {
        "resposta": resposta
    }


# Treinamento do modelo
@app.post("/treinamento_modelo")
async def treina_modelo(email: str):
    from services.vetorizacao import main
    
    main(email=email)

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


@app.post("/carrega_arquivos")
async def carrega_arquivos(arquivo: UploadFile, email: str):
    from services.carrega_arquivos import upload_arquivos

    resposta = upload_arquivos(arquivo=arquivo, email=email)

    return resposta


@app.post("/login")
async def login(email: str, password: str):
    from services.auth import login as login_service

    resposta = login_service(email, password)

    return resposta