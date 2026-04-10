from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required

from .models import Filme, Filme_favoritos, Filme_avaliacao, Filme_visualizacao

CustomUser = get_user_model()

Area_usuario = 'area_usuario/'
Area_login = 'login/'


# ----------------------------
# Funções auxiliares
# ----------------------------

def _get_favoritos_ids(user):
    if not user.is_authenticated:
        return []

    # Ajuste "filme_id" se no seu model o FK tiver outro nome
    return list(
        Filme_favoritos.objects.filter(user=user).values_list('filme_id', flat=True)
    )


# ----------------------------
# Áreas Gerais
# ----------------------------

def index_view(request):
    filmes = Filme.objects.all().order_by('-data_cadastro')
    favoritos_ids = _get_favoritos_ids(request.user)

    context = {
        'filmes': filmes,
        'incluir_favoritos': favoritos_ids,
    }

    return render(request, 'index.html', context)

def base_view(request):
    return render(request, 'base.html')


def base_Usuario_view(request):
    return render(request, Area_usuario + 'base.html')


# ----------------------------
# Área do Usuário
# ----------------------------

@login_required
def dashboard(request):
    user = request.user

    visualizacoes = Filme_visualizacao.objects.filter(user=user).count()
    total_favoritos = Filme_favoritos.objects.filter(user=user).count()
    total_avaliacoes = Filme_avaliacao.objects.filter(user=user).count()

    return render(request, Area_usuario + 'dashboard_user.html', {
        'pagina': {
            'name': 'Painel de Controle',
            'code': 'dashboard'
        },
        'visualizacoes': visualizacoes,
        'total_favoritos': total_favoritos,
        'total_avaliacoes': total_avaliacoes,
    })

@login_required
def favoritos(request):
    user = request.user
    query = request.GET.get('q', '')

    favoritos_qs = Filme_favoritos.objects.filter(user=user).select_related('filme').order_by('-data_criacao')

    if query:
        favoritos_qs = favoritos_qs.filter(filme__titulo__icontains=query)

    filmes_favoritos = [fav.filme for fav in favoritos_qs]

    return render(request, Area_usuario + 'favoritos.html', {
        'pagina': {
            'name': 'Favoritos',
            'code': 'favoritos'
        },
        'filmes_favoritos': filmes_favoritos,
        'incluir_favoritos': _get_favoritos_ids(request.user),
        'q': query
    })


@login_required
def amigos(request):
    return render(request, Area_usuario + 'amigos.html', {
        'pagina': {
            'name': 'Amizades',
            'code': 'amigos'
        },
    })


@login_required
def home_user(request):
    query = request.GET.get('q', '')

    if query:
        filmes = Filme.objects.filter(titulo__icontains=query).order_by('-data_criacao')
    else:
        filmes = Filme.objects.all().order_by('-data_criacao')

    sender_page = {
        'filmes': filmes,
        'incluir_favoritos': _get_favoritos_ids(request.user),
        'q': query
    }

    return render(request, Area_usuario + 'home.html', sender_page)


@login_required
def meus_filmes(request):
    user = request.user
    query = request.GET.get('q', '')

    filmes_qs = Filme.objects.filter(user=user).order_by('-data_criacao')

    if query:
        filmes_qs = filmes_qs.filter(titulo__icontains=query)

    return render(request, Area_usuario + 'meus_filmes.html', {
        'pagina': {
            'name': 'Meus Filmes',
            'code': 'meus_filmes'
        },
        'button_info': {
            'text': 'Editar filme',
            'url': 'editar_filme'
        },
        'filmes_meus': filmes_qs,
        'incluir_favoritos': _get_favoritos_ids(request.user),
        'q': query
    })


@login_required
def configuracoes(request):
    return render(request, Area_usuario + 'settings.html', {
        'pagina': {
            'name': 'Configurações',
            'code': 'configuracoes'
        },
    })


# ----------------------------
# Páginas de filmes
# ----------------------------

def filme_detalhe(request, id):
    filme = get_object_or_404(Filme, id=id)
    user = request.user if request.user.is_authenticated else None

    Filme_visualizacao.objects.create(
        user=user,
        filme=filme,
    )

    return render(request, 'filme_detalhe.html', {
        'filme': filme,
        'incluir_favoritos': _get_favoritos_ids(request.user),
    })


@login_required(login_url='login')
def cadastro_de_filme(request):
    user = request.user

    if request.method == 'POST':
        send_filme(request, user)
        return redirect('/home')

    return render(request, Area_usuario + 'cadastro_de_filme.html', {
        'pagina': {
            'name': 'Cadastro de filme',
            'code': 'cadastro_de_filme'
        },
    })


@login_required(login_url='login')
def editar_filme(request, id):
    filme = get_object_or_404(Filme, id=id)

    if request.method == 'POST':
        user = request.user
        send_filme(request, user, filme)
        return redirect('/home')

    return render(request, Area_usuario + 'cadastro_de_filme.html', {
        'pagina': {
            'name': 'Editar filme',
            'code': 'editar_filme'
        },
        'filme': filme
    })


def send_filme(request, user, filme=None):
    form = request.POST.dict()
    imagem_p = request.FILES.get('input_image')

    if imagem_p is not None:
        form['imagem_p'] = imagem_p
    else:
        form.pop('input_image', None)

    form.pop('csrfmiddlewaretoken', None)

    # Dono do filme
    form['user'] = user

    if filme is not None:
        for chave, valor in form.items():
            setattr(filme, chave, valor)
        filme.save()
    else:
        filme = Filme.objects.create(**form)

    return filme


# ----------------------------
# Login, perfil, configurações
# ----------------------------

def cadastro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('senha')

        if password != request.POST.get('senha_confirmada'):
            return render(request, Area_login + 'register.html', {
                'form_err': 'As senhas não coincidem.'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, Area_login + 'register.html', {
                'form_err': 'Usuário já existe.'
            })

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
        )
        user.save()

        return redirect('login')

    return render(request, Area_login + 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = (
            request.POST.get('username')
            or request.POST.get('email')
            or request.POST.get('usuario')
            or ''
        ).strip()

        password = (
            request.POST.get('senha')
            or request.POST.get('password')
            or ''
        ).strip()

        if not username or not password:
            return render(request, Area_login + 'login.html', {
                'form_err': 'Usuário e senha são obrigatórios.'
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if request.POST.get('remember_me') is not None:
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(60 * 60 * 24 * 1)

            return redirect('/home')

        return render(request, Area_login + 'login.html', {
            'form_err': 'Usuário ou senha inválidos.'
        })

    return render(request, Area_login + 'login.html')
def logout_view(request):
    logout(request)
    return redirect('/')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            CustomUser.objects.get(email=email)
            mensagem = 'Se o email estiver correto, enviaremos instruções para redefinir a senha.'
            return render(request, Area_login + 'forgot_password.html', {'mensagem': mensagem})
        except CustomUser.DoesNotExist:
            erro = 'Email não encontrado no sistema.'
            return render(request, Area_login + 'forgot_password.html', {'erro': erro})

    return render(request, Area_login + 'forgot_password.html')


@login_required
def perfil(request):
    user = request.user

    if request.method == 'POST':
        user.nome = request.POST.get('nome') or ""
        user.email = request.POST.get('email')

        imagem_p = request.FILES.get('input_image')
        if imagem_p is not None:
            user.profile_image = imagem_p

        user.save()

        return render(request, Area_login + 'perfil.html', {
            'pagina': {
                'intro': False
            },
            'form_info': {
                'msg': 'Perfil atualizado com sucesso!',
                'type': 'success'
            }
        })

    return render(request, Area_login + 'perfil.html', {
        'pagina': {
            'intro': False
        }
    })


@login_required
def favoritar(request):
    if request.method == "POST" and "favoritar" in request.POST:
        user = request.user
        valor = request.POST.get('favoritar', '')
        dados = valor.split(',')

        if len(dados) != 2:
            return redirect(request.META.get('HTTP_REFERER', '/'))

        filme_id = dados[0]
        adicionar = dados[1] == 'True'

        if adicionar:
            filme = get_object_or_404(Filme, id=filme_id)
            Filme_favoritos.objects.get_or_create(user=user, filme=filme)
        else:
            Filme_favoritos.objects.filter(user=user, filme__id=filme_id).delete()

        return redirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, '404.html', status=404)