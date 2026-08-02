from langchain_ollama import OllamaEmbeddings, ChatOllama
from sqlalchemy import select
from services.database import SessionLocal
from services.models import Chunk, Document as DBDocument, User


EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"
TOP_K = 5


def buscar_chunks_relevantes(pergunta: str, email: str, session, top_k: int = TOP_K):
    """
    Gera o embedding da pergunta e busca os chunks mais próximos
    no Postgres usando pgvector
    """
    embed = OllamaEmbeddings(model=EMBED_MODEL)
    vetor_pergunta = embed.embed_query(pergunta)

    # quanto menor, mais similar
    stmt = (
        select(Chunk, DBDocument.filename)
        .join(DBDocument, Chunk.document_id == DBDocument.id)
        .join(User, DBDocument.user_id == User.id)
        .where(User.email == email)
        .order_by(Chunk.embedding.cosine_distance(vetor_pergunta))
        .limit(top_k)
    )

    resultados = session.execute(stmt).all()

    return resultados  # lista de tuplas (Chunk, filename)


def montar_prompt(pergunta: str, resultados) -> str:
    """Monta o prompt com o contexto recuperado."""
    contexto = "\n\n".join(
        f"[Fonte: {filename}, página {chunk.page}]\n{chunk.content}"
        for chunk, filename in resultados
    )

    prompt = f"""Você é um assistente que responde perguntas com base APENAS no contexto fornecido abaixo.
    Se a informação não estiver no contexto, diga claramente que não sabe — não invente respostas.

    Contexto:
    {contexto}

    Pergunta: {pergunta}

    Resposta:"""

    return prompt


def responder(pergunta: str, email: str) -> str:
    session = SessionLocal()

    try:
        resultados = buscar_chunks_relevantes(pergunta, email, session)

        if not resultados:
            return "Não encontrei nenhum documento relevante para essa pergunta."

        prompt = montar_prompt(pergunta, resultados)

        llm = ChatOllama(model=LLM_MODEL, temperature=0)
        resposta = llm.invoke(prompt)

        # Mostra as fontes usadas, útil para debug/transparência
        fontes = {f"{filename} (pág. {chunk.page})" for chunk, filename in resultados}
        print("\nFontes consultadas:")
        for fonte in fontes:
            print(f"  - {fonte}")

        return resposta.content

    finally:
        session.close()


def main():
    print("Faça sua pergunta (Ctrl+C para sair)\n")

    while True:
        pergunta = input("Pergunta: ").strip()

        if not pergunta:
            continue

        resposta = responder(pergunta)
        print(f"\nResposta: {resposta}\n")


if __name__ == "__main__":
    main()