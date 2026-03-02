from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from dependences import pegar_sessao, verificar_token
from schemas import PedidoSchema
from models import Pedido, Usuario

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verificar_token)])

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

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id_usuario != pedido.usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")

    pedido.status = "CANCELADO"
    session.commit()
    return {
        'mensagem': f'pedido {pedido.id_pedido} cancelado com sucesso!',
        'pedido': pedido
        }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Autorização negada")
    else:
        pedidos = session.query(Pedido).all()
        return {
            'pedidos': pedidos
        }