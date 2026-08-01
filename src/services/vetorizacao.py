import os
import boto3
from io import BytesIO
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from services.database import SessionLocal
from services.models import Chunk, Document as DBDocument
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

EMBED_BATCH_SIZE = 50  # ajuste conforme necessidade/limite do seu Ollama


def listar_objetos(s3_client, bucket: str):
    """Lista todos os objetos do bucket, tratando paginação"""
    objetos = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for pagina in paginator.paginate(Bucket=bucket):
        objetos.extend(pagina.get("Contents", []))
    return objetos


def carrega_documentos(s3_client, bucket: str, session) -> list:
    """
    Lê os PDFs do MinIO, cria 1 DBDocument por arquivo e retorna
    a lista de langchain Documents (1 por página), já com document_id
    no metadata para linkar os chunks depois
    """
    documentos = []

    for obj in listar_objetos(s3_client, bucket):

        arquivo = s3_client.get_object(Bucket=bucket, Key=obj["Key"])
        pdf_bytes = BytesIO(arquivo["Body"].read())
        reader = PdfReader(pdf_bytes)

        # Cria o registro do documento UMA vez por arquivo
        documento_db = DBDocument(
            filename=obj["Key"],
            bucket=bucket,
            object_key=obj["Key"],
        )
        session.add(documento_db)
        session.flush()  # gera o ID sem commitar ainda

        for page_number, page in enumerate(reader.pages):
            texto = page.extract_text() or ""

            if not texto.strip():
                continue  # pula páginas vazias/sem texto extraivel

            documentos.append(
                Document(
                    page_content=texto,
                    metadata={
                        "source": obj["Key"],
                        "bucket": bucket,
                        "page": page_number,
                        "document_id": documento_db.id,
                    },
                )
            )

    return documentos


def criar_chunks(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    return splitter.split_documents(documentos)


def criar_vetores(chunks, batch_size: int = EMBED_BATCH_SIZE):
    """Gera embeddings em lotes para evitar timeout no Ollama"""
    embed = OllamaEmbeddings(model="nomic-embed-text")
    vetores = []

    textos = [chunk.page_content for chunk in chunks]
    for i in range(0, len(textos), batch_size):
        lote = textos[i:i + batch_size]
        vetores.extend(embed.embed_documents(lote))

    return vetores

def salvar_chunks(chunks, vetores, session):
    for indice, (chunk, vetor) in enumerate(zip(chunks, vetores)):
        registro = Chunk(
            document_id=chunk.metadata["document_id"],
            chunk_index=indice,
            page=chunk.metadata["page"],
            content=chunk.page_content,
            embedding=vetor,
        )
        session.add(registro)


def deletar_chunks(session):
    """Deleta todos os chunks e documentos do banco de dados"""
    try:
        session.query(Chunk).delete()
        session.query(DBDocument).delete()
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main():
    s3 = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    session = SessionLocal()

    try:
        documentos = carrega_documentos(s3_client=s3, bucket="documentos", session=session)

        chunks = criar_chunks(documentos=documentos)

        vetores = criar_vetores(chunks=chunks)

        deletar_chunks(session=session)  # limpa antes de salvar novos

        salvar_chunks(chunks=chunks, vetores=vetores, session=session)

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()