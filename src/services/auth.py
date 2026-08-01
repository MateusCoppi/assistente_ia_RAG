from services.models import User
from services.database import SessionLocal


def cria_usuario(username, email, password):

    """Cria um usuário no banco de dados"""
    session = SessionLocal()
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    session.add(user)
    session.commit()

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