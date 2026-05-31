from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from app_Goodfilms.models import CustomUser, Filme_avaliacao, Filme_favoritos
from app_Goodfilms.tests.helpers import create_filme, create_user


class ModelTests(TestCase):
    def setUp(self):
        self.user = create_user("model_user@example.com")
        self.filme = create_filme(user=self.user)

    def test_create_user_sem_username_gera_erro(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="", password="123")

    def test_filme_duracao_deve_ser_maior_que_zero(self):
        filme = create_filme(duracao_minutos=0, user=self.user)

        with self.assertRaises(ValidationError) as ctx:
            filme.full_clean()

        self.assertIn("duracao_minutos", ctx.exception.message_dict)

    def test_avaliacao_nota_fora_do_intervalo_e_invalida(self):
        avaliacao = Filme_avaliacao(
            user=self.user,
            filme=self.filme,
            nota=6,
            comentario="Comentario",
        )

        with self.assertRaises(ValidationError) as ctx:
            avaliacao.full_clean()

        self.assertIn("nota", ctx.exception.message_dict)

    def test_avaliacao_mesmo_usuario_filme_nao_pode_duplicar(self):
        Filme_avaliacao.objects.create(user=self.user, filme=self.filme, nota=4)

        with self.assertRaises(IntegrityError):
            Filme_avaliacao.objects.create(user=self.user, filme=self.filme, nota=5)

    def test_favorito_mesmo_usuario_filme_nao_pode_duplicar(self):
        Filme_favoritos.objects.create(user=self.user, filme=self.filme)

        with self.assertRaises(IntegrityError):
            Filme_favoritos.objects.create(user=self.user, filme=self.filme)
