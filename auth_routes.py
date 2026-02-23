from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependences import pegar_sessao, verificar_token
from main import bycrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import LoginSchema, UsuarioSchema
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_token = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        return False
    elif not bycrypt_context.verify(senha, usuario.senha):
        return False
    return usuario



@auth_router.get("/")
async def home():
    """
    Rota padrão para autenticação de usuário. Todas as rotas de pedidos precisam de autenticação.
    """
    return {'mensagem': 'autenticação de usuário', 'status': False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):

    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    else:
        senha_criptografada = bycrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {'mensagem': f'conta criada com sucesso {usuario_schema.email}'}
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):

    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais incorretas")
    else:   
        access_token = criar_token(usuario.id_usuario)
        refresh_token = criar_token(usuario.id_usuario, timedelta(days=7))
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
@auth_router.post("/login-form")
async def login(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):

    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais incorretas")
    else:   
        access_token = criar_token(usuario.id_usuario)
        refresh_token = criar_token(usuario.id_usuario, timedelta(days=7))
        return {"access_token": access_token, "token_type": "bearer"}
    
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    #verificar token
    access_token = criar_token(usuario.id_usuario)
    return {"access_token": access_token, "token_type": "bearer"}

