from app_Goodfilms.models import CustomUser, Filme


def create_user(username, password="senha123", nome="Usuario Teste", email=None):
    if email is None:
        email = username
    return CustomUser.objects.create_user(
        username=username,
        password=password,
        nome=nome,
        email=email,
    )


def create_filme(
    titulo="Filme Teste",
    user=None,
    genero="Drama",
    sinopse="Sinopse",
    diretor="Diretor",
    ano_lancamento=2024,
    duracao_minutos=120,
    classificacao="Livre",
):
    return Filme.objects.create(
        titulo=titulo,
        user=user,
        genero=genero,
        sinopse=sinopse,
        diretor=diretor,
        ano_lancamento=ano_lancamento,
        duracao_minutos=duracao_minutos,
        classificacao=classificacao,
    )
