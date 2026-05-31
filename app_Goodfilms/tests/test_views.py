from django.test import TestCase
from django.urls import reverse

from app_Goodfilms.models import Filme, Filme_avaliacao, Filme_favoritos
from app_Goodfilms.tests.helpers import create_filme, create_user


class ViewTests(TestCase):
    def setUp(self):
        self.user = create_user("user1@example.com", nome="User 1")
        self.other_user = create_user("user2@example.com", nome="User 2")

    def test_rotas_protegidas_redirecionam_sem_login(self):
        filme = create_filme(user=self.user, titulo="Filme Privado")
        rotas = [
            reverse("home"),
            reverse("cadastro_de_filme"),
            f"/filmes/{filme.id}/",
        ]

        for rota in rotas:
            with self.subTest(rota=rota):
                response = self.client.get(rota)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith("/login"))

    def test_cadastro_de_filme_cria_filme_para_usuario_logado(self):
        self.client.force_login(self.user)

        payload = {
            "titulo": "Novo Filme",
            "genero": "Acao",
            "duracao_minutos": 100,
            "classificacao": "14 anos",
            "diretor": "Diretor X",
            "ano_lancamento": 2022,
            "sinopse": "Sinopse do novo filme.",
        }

        response = self.client.post(reverse("cadastro_de_filme"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Filme.objects.filter(titulo="Novo Filme", user=self.user).exists())

    def test_editar_filme_de_outro_usuario_retorna_404(self):
        filme_outro = create_filme(user=self.other_user, titulo="Filme do outro")
        self.client.force_login(self.user)

        response = self.client.get(f"/filmes/editar/{filme_outro.id}/")

        self.assertEqual(response.status_code, 404)

    def test_excluir_filme_do_proprio_usuario(self):
        filme = create_filme(user=self.user, titulo="Filme para excluir")
        self.client.force_login(self.user)

        response = self.client.post(
            f"/filmes/excluir/{filme.id}/",
            data={"next": reverse("home")},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Filme.objects.filter(id=filme.id).exists())

    def test_favoritar_adiciona_e_remove_filme(self):
        filme = create_filme(user=self.other_user, titulo="Filme Favorito")
        self.client.force_login(self.user)

        response_add = self.client.post(
            reverse("favoritar"),
            data={
                "favoritar": f"{filme.id},True",
                "next": reverse("home"),
            },
        )

        self.assertEqual(response_add.status_code, 302)
        self.assertTrue(
            Filme_favoritos.objects.filter(user=self.user, filme=filme).exists()
        )

        response_remove = self.client.post(
            reverse("favoritar"),
            data={
                "favoritar": f"{filme.id},False",
                "next": reverse("home"),
            },
        )

        self.assertEqual(response_remove.status_code, 302)
        self.assertFalse(
            Filme_favoritos.objects.filter(user=self.user, filme=filme).exists()
        )

    def test_filme_detalhe_avaliar_atualiza_avaliacao_existente(self):
        filme = create_filme(user=self.other_user, titulo="Filme Avaliado")
        self.client.force_login(self.user)

        url = f"/filmes/{filme.id}/"

        response_primeiro = self.client.post(
            url,
            data={
                "acao": "avaliar",
                "nota": "5",
                "comentario": "Excelente",
            },
        )

        self.assertEqual(response_primeiro.status_code, 302)
        self.assertEqual(
            Filme_avaliacao.objects.filter(user=self.user, filme=filme).count(),
            1,
        )

        response_segundo = self.client.post(
            url,
            data={
                "acao": "avaliar",
                "nota": "3",
                "comentario": "Mudou minha opiniao",
            },
        )

        self.assertEqual(response_segundo.status_code, 302)
        self.assertEqual(
            Filme_avaliacao.objects.filter(user=self.user, filme=filme).count(),
            1,
        )
        avaliacao = Filme_avaliacao.objects.get(user=self.user, filme=filme)
        self.assertEqual(avaliacao.nota, 3)
        self.assertEqual(avaliacao.comentario, "Mudou minha opiniao")

    def test_home_modo_favoritos_mostra_apenas_filmes_favoritos_do_usuario(self):
        filme_favorito = create_filme(user=self.other_user, titulo="Filme Favorito")
        filme_nao_favorito = create_filme(
            user=self.other_user,
            titulo="Filme Nao Favorito",
        )
        Filme_favoritos.objects.create(user=self.user, filme=filme_favorito)
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"), data={"modo": "favoritos"})

        self.assertEqual(response.status_code, 200)
        filmes_contexto = list(response.context["filmes"])
        self.assertEqual(len(filmes_contexto), 1)
        self.assertEqual(filmes_contexto[0].id, filme_favorito.id)
        self.assertNotIn(filme_nao_favorito.id, [f.id for f in filmes_contexto])
