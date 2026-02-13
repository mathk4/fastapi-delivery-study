from fastapi import APIRouter, Depends
from models import Usuario
from dependences import pegar_sessao
from main import bycrypt_context

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Rota padrão para autenticação de usuário. Todas as rotas de pedidos precisam de autenticação.
    """
    return {'mensagem': 'autenticação de usuário', 'status': False}

@auth_router.post("/criar_conta")
async def criar_conta(email: str, senha: str, nome: str, session = Depends(pegar_sessao)):

    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if usuario:
        return {'mensagem': 'email já cadastrado'}
    else:
        senha_criptografada = bycrypt_context.hash(senha)
        novo_usuario = Usuario(nome, email, senha_criptografada)
        session.add(novo_usuario)
        session.commit()
        return {'mensagem': 'conta criada com sucesso'}