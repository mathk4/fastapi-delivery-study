from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types import ChoiceType

# Conexão com o banco de dados
db = create_engine('sqlite:///database/delivery.db', echo=True)

# Base do banco de dados
Base = declarative_base()

# Classe/tabelas do banco de dados
# Usuario
class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column("id_usuario", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

# Pedido
class Pedido(Base):
    __tablename__ = 'pedidos'

    # STATUS_PEDIDOS = (
    #     ("PENDENTE", "PENDENTE"),
    #     ("CANCELADO", "CANCELADO"),
    #     ("FINALIZADO", "FINALIZADO")
    # )

    id_pedido = Column("id_pedido", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String, nullable=False)
    usuario = Column("id_usuario", ForeignKey("usuarios.id_usuario"), nullable=False)
    preco = Column("preco", Float)
    #itens =

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco

# ItensPedidos
class ItensPedido(Base):
    __tablename__ = 'pedido_itens'

    id_item = Column("id_item", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer, nullable=False)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("id_pedido", ForeignKey("pedidos.id_pedido"), nullable=False)

    def __init__(self, pedido, quantidade, sabor, tamanho, preco_unitario):
        self.pedido = pedido
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario