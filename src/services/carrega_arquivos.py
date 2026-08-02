import boto3
from services.models import User
from services.database import SessionLocal
from services.s3_connection import get_s3_client


def upload_arquivos(arquivo, email: str):
    """
    Faz upload dos arquivos enviados pelo usuario para um bucket S3 identificado pelo username
    """

    session = SessionLocal()

    user = session.query(User).filter(User.email == email).first()

    if not user:
        return {
            "mensagem": "Usuário não encontrado"
        }

    bucket = user.username  # nome do bucket é o username do usuário

    # Cria o cliente S3
    s3 = get_s3_client()

    # Cria o bucket se não existir
    if bucket not in [b["Name"] for b in s3.list_buckets()["Buckets"]]:
        s3.create_bucket(Bucket=bucket)
    else:
        print(f"Bucket {bucket} já existe.")

    
    # Upload do arquivo para o bucket do usuario (arquivos pdf)
    s3.upload_fileobj(
        Bucket=bucket, 
        Key=arquivo.filename, 
        Fileobj=arquivo.file
    )
    
    if not arquivo.filename.endswith(".pdf"):
        return {
            "mensagem": "Apenas arquivos PDF são permitidos"
        }


