from services.models import User
from services.database import SessionLocal
from services.s3_connection import get_s3_client


def cria_usuario(username, email, password):

    """Cria um usuário no banco de dados"""
    session = SessionLocal()
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    if session.query(User).filter(User.email == email).first():
        return {
            "mensagem": "Usuário já cadastrado"
        }

    session.add(user)
    session.commit()

    s3 = get_s3_client()

    s3.create_bucket(Bucket=username)  # cria o bucket do usuário no S3

    return {
        "mensagem": "Usuário criado com sucesso"
    }


def get_password_hash(password):
    """Gera o hash da senha"""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def autenticar_usuario(email):
    """Autentica o usuário no banco de dados"""
    session = SessionLocal()
    user = session.query(User).filter(User.email == email).first()

    if not user:
        return False

    return user


def login(email, password):
    """Faz o login do usuário"""
    user = autenticar_usuario(email)

    if not user:
        return {
            "mensagem": "Usuário não encontrado"
        }

    if not verify_password(password, user.hashed_password):
        return {
            "mensagem": "Senha incorreta"
        }

    return {
        "mensagem": "Login realizado com sucesso"
    }


def verify_password(plain_password, hashed_password):
    """Verifica se a senha está correta"""
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)