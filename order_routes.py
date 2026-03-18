from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from dependences import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItensPedido
from typing import List

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
    if not usuario.admin and usuario.id_usuario != pedido.usuario:
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

@order_router.post("/pedido/adicionar_item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id_usuario != pedido.usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")
    
    item_pedido = ItensPedido(id_pedido, item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario)

    session.add(item_pedido)
    pedido.calcular_preco_total()

    
    session.commit()
    return {
        'mensagem': "item adicionado ao pedido com sucesso!",
        'id_item': item_pedido.id_item,
        'preço_pedido_total': pedido.preco
        }

@order_router.post("/pedido/remover_item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItensPedido).filter(ItensPedido.id_item == id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id_pedido == item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item do pedido não encontrado")
    if not usuario.admin and usuario.id_usuario != pedido.usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")
    
    session.delete(item_pedido)
    pedido.calcular_preco_total()

    session.commit()
    return {
        'mensagem': "item removido do pedido com sucesso!",
        'preço_pedido_total': pedido.preco
        }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id_usuario != pedido.usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")
    
    pedido.status = "FINALIZADO"
    session.commit()

    return {
        'mensagem': f"pedido {pedido.id_pedido} finalizado com sucesso!",
        'preço_pedido_total': pedido
        }

@order_router.get("/pedido/{id_pedido}")
async def vizualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id_usuario != pedido.usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")
    
    return {
        'quantidade_itens': len(pedido.itens),
        'pedido': pedido
    }

@order_router.get("/listar/pedido_usuario/{id_usuario}", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(id_usuario: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin and usuario.id_usuario != id_usuario:
        raise HTTPException(status_code=401, detail="Autorização negada")
    else:
        pedidos = session.query(Pedido).filter(Pedido.usuario == id_usuario).all()
        return pedidos