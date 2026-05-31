from django.test import TestCase

from app_Goodfilms.forms import FilmeForm


class FormTests(TestCase):
    def test_filme_form_valido(self):
        form = FilmeForm(
            data={
                "titulo": "Interestelar",
                "genero": "Ficcao cientifica",
                "duracao_minutos": 169,
                "classificacao": "12 anos",
                "diretor": "Christopher Nolan",
                "ano_lancamento": 2014,
                "sinopse": "Viagem espacial.",
            }
        )

        self.assertTrue(form.is_valid())

    def test_filme_form_campos_obrigatorios(self):
        form = FilmeForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)
        self.assertIn("genero", form.errors)
        self.assertIn("duracao_minutos", form.errors)
        self.assertIn("classificacao", form.errors)
