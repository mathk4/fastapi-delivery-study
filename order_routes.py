from fastapi import APIRouter

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def pedidos():
    """
    Rota padrão para pedidos de usuário.
    """
    return {'mensagem': 'lista de pedidos'}