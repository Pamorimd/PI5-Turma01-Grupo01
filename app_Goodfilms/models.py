#! Bibliotecas do Django
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

#! Bibliotecas do Python
import uuid 

# ----------------------------
# Modelo de Usuário Customizado (Mantido)
# ----------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O campo 'username' é obrigatório.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class CustomUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='perfil', blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        db_table = 'Usuarios'

    def __str__(self):
        return self.username

# ----------------------------
# Modelo de Filme (Antigo Servico)
# ----------------------------
class Filme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    titulo_original = models.CharField(max_length=255, blank=True, null=True)
    genero = models.CharField(max_length=255, help_text="Ex: Drama, Sci-Fi") 
    sinopse = models.TextField(blank=True, null=True)
    diretor = models.CharField(max_length=255, blank=True, null=True)
    ano_lancamento = models.IntegerField(null=True, blank=True)
    duracao_minutos = models.IntegerField(default=0)
    
    # Armazenar metadados extras (elenco, prêmios, etc)
    metadados = models.JSONField(blank=True, null=True) 
    
    poster = models.ImageField(upload_to='filmes/posters', blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filmes'

    def __str__(self):
        return f"{self.titulo} ({self.ano_lancamento})"

# ----------------------------
# Visualização de Filmes
# ----------------------------
class Filme_visualizacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        related_name='filmes_vistos',
        null=True, blank=True
    )
    filme = models.ForeignKey(
        Filme, 
        on_delete=models.CASCADE, 
        related_name='visualizacoes'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    data_visualizacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_visualizacao'

# ----------------------------
# Avaliação de Filme (Crucial para Recomendação)
# ----------------------------
class Filme_avaliacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='avaliacoes_feitas'
    )
    filme = models.ForeignKey(
        Filme, 
        on_delete=models.CASCADE, 
        related_name='avaliacoes'
    )
    # Nota de 1 a 5 (ou 1 a 10, dependendo da sua lógica de SVD)
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_avaliacao'
        unique_together = ('user', 'filme') # Garante que o usuário avalie o filme apenas uma vez

    def __str__(self):
        return f"{self.user.username} - {self.filme.titulo}: {self.nota}"

# ----------------------------
# Lista de Assistidos / Histórico
# ----------------------------
class Filme_assistido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='historico_assistidos'
    )
    filme = models.ForeignKey(
        Filme, 
        on_delete=models.CASCADE, 
        related_name='usuarios_que_assistiram'
    )
    data_finalizacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_assistidos'

# ----------------------------
# Filmes Favoritos
# ----------------------------
class Filme_favoritos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='favoritos'
    )
    filme = models.ForeignKey(
        Filme, 
        on_delete=models.CASCADE, 
        related_name='favoritado_por'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_favoritos'
        unique_together = ('user', 'filme')