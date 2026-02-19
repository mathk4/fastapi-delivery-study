from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from dependences import pegar_sessao
from schemas import PedidoSchema
from models import Pedido

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def pedidos():
    """
    Rota padrão para pedidos de usuário.
    """
    return {'mensagem': 'lista de pedidos'}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido =  Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {'mensagem': f'pedido criado com sucesso! ID do pedido: {novo_pedido.id_pedido}'}