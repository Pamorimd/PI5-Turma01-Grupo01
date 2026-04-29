from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, ExpressionWrapper, F, FloatField, IntegerField, OuterRef, Subquery, TextField, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import FilmeForm
from .models import Filme, Filme_assistido, Filme_favoritos, Filme_avaliacao, Filme_visualizacao

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


def _formatar_duracao(minutos):
    if not minutos:
        return 'Duracao nao informada'

    horas = minutos // 60
    minutos_restantes = minutos % 60

    if horas and minutos_restantes:
        return f'{horas}h{minutos_restantes:02d}min'
    if horas:
        return f'{horas}h'
    return f'{minutos_restantes}min'


def _safe_next_url(request, fallback):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and next_url.startswith('/'):
        return next_url
    return fallback


# ----------------------------
# Áreas Gerais
# ----------------------------

def index_view(request):
    favoritos_ids = _get_favoritos_ids(request.user)

    context = {
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
    query = request.GET.get('q', '').strip()
    url = f"{reverse('home')}?modo=favoritos"
    if query:
        url = f"{url}&q={query}"
    return redirect(url)


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
    query = request.GET.get('q', '').strip()
    modo = request.GET.get('modo', 'meus-filmes').strip()
    status_filtro = request.GET.get('status', 'todos').strip()  # 'todos', 'assistidos', 'nao-assistidos'
    ordenacao = request.GET.get('ordem', '-data_cadastro').strip()  # '-data_cadastro', 'titulo', '-media_nota'
    favoritos_ids = _get_favoritos_ids(request.user)

    avaliacao_usuario = Filme_avaliacao.objects.filter(
        user=request.user,
        filme=OuterRef('pk')
    )

    filmes = (
        Filme.objects.all()
        .annotate(
            media_nota=Coalesce(Avg('avaliacoes__nota'), Value(0.0)),
            minha_nota=Subquery(avaliacao_usuario.values('nota')[:1], output_field=IntegerField()),
            meu_comentario=Subquery(avaliacao_usuario.values('comentario')[:1], output_field=TextField()),
        )
        .annotate(
            media_percentual=ExpressionWrapper(
                F('media_nota') * Value(20.0),
                output_field=FloatField(),
            ),
            minha_nota_percentual=ExpressionWrapper(
                Coalesce(F('minha_nota'), Value(0)) * Value(20.0),
                output_field=FloatField(),
            ),
        )
    )

    if query:
        filmes = filmes.filter(titulo__icontains=query)

    assistidos_count = 0
    nao_assistidos_count = 0

    if modo == 'recomendacoes':
        filmes = filmes.order_by('-media_nota', '-data_cadastro')
        titulo_home = 'Recomenda\u00e7\u00f5es'
    elif modo == 'avaliados':
        filmes = (
            filmes
            .filter(avaliacoes__user=request.user)
            .order_by('-avaliacoes__data_criacao', '-data_cadastro')
            .distinct()
        )
        titulo_home = 'Avaliados'
    elif modo == 'favoritos':
        filmes = filmes.filter(id__in=favoritos_ids).order_by('-data_cadastro')
        titulo_home = 'Favoritos'
    else:
        modo = 'meus-filmes'
        titulo_home = 'Meus Filmes'
        
        # Separar por status de assistido/não assistido
        assistidos_ids = set(
            Filme_assistido.objects.filter(user=request.user).values_list('filme_id', flat=True)
        )
        
        assistidos_count = len(assistidos_ids)
        total_filmes = filmes.count()
        nao_assistidos_count = total_filmes - assistidos_count
        
        # Filtrar por status
        if status_filtro == 'assistidos':
            filmes = filmes.filter(id__in=assistidos_ids)
        elif status_filtro == 'nao-assistidos':
            filmes = filmes.exclude(id__in=assistidos_ids)
        
        # Aplicar ordenação
        if ordenacao == 'titulo':
            filmes = filmes.order_by('titulo')
        elif ordenacao == '-media_nota':
            filmes = filmes.order_by('-media_nota', '-data_cadastro')
        else:  # '-data_cadastro' é o padrão
            filmes = filmes.order_by('-data_cadastro')

    page_num = request.GET.get('page', 1)
    paginator = Paginator(filmes, 6)

    try:
        page_obj = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    sender_page = {
        'pagina': {
            'name': titulo_home,
            'code': 'home',
            'intro': False,
        },
        'filmes': page_obj.object_list,
        'page_obj': page_obj,
        'incluir_favoritos': favoritos_ids,
        'q': query,
        'modo': modo,
        'titulo_home': titulo_home,
        'status_filtro': status_filtro,
        'ordenacao': ordenacao,
        'assistidos_count': assistidos_count,
        'nao_assistidos_count': nao_assistidos_count,
    }

    return render(request, Area_usuario + 'home.html', sender_page)


@login_required
def meus_filmes(request):
    user = request.user
    query = request.GET.get('q', '')

    filmes_qs = Filme.objects.filter(user=user).order_by('-data_criacao')

    if query:
        filmes_qs = filmes_qs.filter(titulo__icontains=query)
    
    page_num = request.GET.get('page', 1)
    paginator = Paginator(filmes_qs, 6)
    
    try:
        page_obj = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, Area_usuario + 'meus_filmes.html', {
        'pagina': {
            'name': 'Meus Filmes',
            'code': 'meus_filmes'
        },
        'button_info': {
            'text': 'Editar filme',
            'url': 'editar_filme'
        },
        'filmes_meus': page_obj.object_list,
        'page_obj': page_obj,
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

@login_required(login_url='login')
def filme_detalhe(request, id):
    filme = get_object_or_404(Filme, id=id)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'avaliar':
            nota = request.POST.get('nota')
            comentario = (request.POST.get('comentario') or '').strip()

            if nota and nota.isdigit() and 1 <= int(nota) <= 5:
                Filme_avaliacao.objects.update_or_create(
                    user=request.user,
                    filme=filme,
                    defaults={
                        'nota': int(nota),
                        'comentario': comentario,
                    },
                )

        elif acao == 'status':
            status = request.POST.get('status')
            if status == 'assistido':
                Filme_assistido.objects.get_or_create(user=request.user, filme=filme)
            else:
                Filme_assistido.objects.filter(user=request.user, filme=filme).delete()

        return redirect('home')

    Filme_visualizacao.objects.create(
        user=request.user,
        filme=filme,
    )

    avaliacao_usuario = Filme_avaliacao.objects.filter(
        user=request.user,
        filme=filme,
    ).first()
    resumo_avaliacoes = filme.avaliacoes.aggregate(
        media=Coalesce(Avg('nota'), Value(0.0)),
        total=Count('id'),
    )
    media_nota = resumo_avaliacoes['media'] or 0
    favoritos_ids = _get_favoritos_ids(request.user)

    return render(request, Area_usuario + 'filme_detalhe.html', {
        'pagina': {
            'name': filme.titulo,
            'code': 'filme_detalhe',
            'intro': False,
        },
        'filme': filme,
        'incluir_favoritos': favoritos_ids,
        'is_favorito': filme.id in favoritos_ids,
        'is_assistido': Filme_assistido.objects.filter(user=request.user, filme=filme).exists(),
        'minha_avaliacao': avaliacao_usuario,
        'media_nota': media_nota,
        'media_percentual': media_nota * 20,
        'total_avaliacoes': resumo_avaliacoes['total'],
        'duracao_label': _formatar_duracao(filme.duracao_minutos),
    })


@login_required(login_url='login')
def cadastro_de_filme(request):
    if request.method == 'POST':
        form = FilmeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FilmeForm()

    return render(request, Area_usuario + 'cadastro_de_filme.html', {
        'pagina': {
            'name': 'Cadastro de filme',
            'code': 'cadastro_de_filme'
        },
        'form': form,
    })


@login_required(login_url='login')
def editar_filme(request, id):
    filme = get_object_or_404(Filme, id=id)

    if request.method == 'POST':
        form = FilmeForm(request.POST, instance=filme)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FilmeForm(instance=filme)

    return render(request, Area_usuario + 'cadastro_de_filme.html', {
        'pagina': {
            'name': 'Editar filme',
            'code': 'editar_filme'
        },
        'filme': filme,
        'form': form,
    })


# ----------------------------
# Login, perfil, configurações
# ----------------------------

def cadastro(request):
    if request.method == 'POST':
        nome = (request.POST.get('nome') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = (request.POST.get('senha') or '').strip()
        username = email

        if not nome or not email or not password:
            return render(request, Area_login + 'register.html', {
                'form_err': 'Nome, email e senha são obrigatórios.'
            })

        if password != request.POST.get('senha_confirmada'):
            return render(request, Area_login + 'register.html', {
                'form_err': 'As senhas não coincidem.'
            })

        if (
            CustomUser.objects.filter(username__iexact=username).exists()
            or CustomUser.objects.filter(email__iexact=email).exists()
        ):
            return render(request, Area_login + 'register.html', {
                'form_err': 'Email já cadastrado.'
            })

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            nome=nome,
            email=email,
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

        if user is None:
            user_by_email = CustomUser.objects.filter(email__iexact=username).first()
            if user_by_email is not None:
                user = authenticate(
                    request,
                    username=user_by_email.get_username(),
                    password=password,
                )

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
            pass

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
        fallback_url = request.META.get('HTTP_REFERER', '/')
        next_url = _safe_next_url(request, fallback_url)

        if len(dados) != 2:
            return redirect(next_url)

        filme_id = dados[0]
        adicionar = dados[1] == 'True'

        if adicionar:
            filme = get_object_or_404(Filme, id=filme_id)
            Filme_favoritos.objects.get_or_create(user=user, filme=filme)
            if request.POST.get('next'):
                return redirect(next_url)
            return redirect(f"{reverse('home')}?modo=favoritos")
        else:
            Filme_favoritos.objects.filter(user=user, filme__id=filme_id).delete()

        return redirect(next_url)

    return render(request, '404.html', status=404)
