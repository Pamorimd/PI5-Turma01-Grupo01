from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O campo 'username' e obrigatorio.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
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


class Filme(models.Model):
    CLASSIFICACAO_CHOICES = [
        ('Livre', 'Livre'),
        ('10 anos', '10 anos'),
        ('12 anos', '12 anos'),
        ('14 anos', '14 anos'),
        ('16 anos', '16 anos'),
        ('18 anos', '18 anos'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='filmes',
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=255)
    genero = models.CharField(max_length=255, help_text="Ex: Drama, Sci-Fi")
    sinopse = models.TextField(blank=True, null=True)
    diretor = models.CharField(max_length=255, blank=True, null=True)
    ano_lancamento = models.IntegerField(null=True, blank=True)
    duracao_minutos = models.IntegerField(validators=[MinValueValidator(1)])
    classificacao = models.CharField(
        max_length=20,
        choices=CLASSIFICACAO_CHOICES,
        default='Livre',
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filmes'

    def __str__(self):
        return f"{self.titulo} ({self.ano_lancamento})"


class Filme_avaliacao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas',
    )
    filme = models.ForeignKey(
        Filme,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
    )
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_avaliacao'
        unique_together = ('user', 'filme')

    def __str__(self):
        return f"{self.user.username} - {self.filme.titulo}: {self.nota}"


class Filme_assistido(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='historico_assistidos',
    )
    filme = models.ForeignKey(
        Filme,
        on_delete=models.CASCADE,
        related_name='usuarios_que_assistiram',
    )
    data_finalizacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_assistidos'


class Filme_favoritos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favoritos',
    )
    filme = models.ForeignKey(
        Filme,
        on_delete=models.CASCADE,
        related_name='favoritado_por',
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Filme_favoritos'
        unique_together = ('user', 'filme')
