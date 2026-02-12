from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def autenticar():
    """
    Rota padrão para autenticação de usuário. Todas as rotas de pedidos precisam de autenticação.
    """
    return {'mensagem': 'autenticação de usuário', 'status': False}