from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.index_view, name='index'),
    path('homeuser/', views.home_user, name='home_user'),
    path('home/', views.dashboard, name='home'),
    path('base/', views.base_view, name='base'),
    path('baseUser/', views.base_Usuario_view, name='user_base'),

    # Páginas de conta/login
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),

    # Páginas pessoais
    path('dashboard/', views.dashboard, name='dashboard'),
    path('friends/', views.amigos, name='amigos'),
    path('favoritos/', views.favoritos, name='favoritos'),
    path('config/', views.configuracoes, name='configuracoes'),

    # Páginas de filmes
    path('cadastro-filme/', views.cadastro_de_filme, name='cadastro_de_filme'),
    path('filmes/editar-anuncio/<uuid:id>/', views.editar_filme, name='editar_filme'),
    path('meus_filmes/', views.meus_filmes, name='meus_filmes'),
    path('filmes/<uuid:id>/', views.filme_detalhe, name='filme_detalhe'),
    path('filmes/editar/<uuid:id>/', views.editar_filme, name='editar_filme'),

    # Funções do front para o back
    path('executar/', views.favoritar, name='favoritar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)