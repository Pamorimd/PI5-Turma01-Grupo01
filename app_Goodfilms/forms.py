from django import forms
from django.contrib.auth import get_user_model

from .models import Filme

User = get_user_model()

class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'nome', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class FilmeForm(forms.ModelForm):
    classificacao = forms.ChoiceField(
        choices=Filme.CLASSIFICACAO_CHOICES,
        required=True,
        error_messages={'required': 'Informe a classificacao do filme.'},
    )
    duracao_minutos = forms.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'required': 'Informe a duracao do filme.',
            'min_value': 'A duracao deve ser maior que zero.',
        },
    )

    class Meta:
        model = Filme
        fields = [
            'titulo',
            'genero',
            'duracao_minutos',
            'classificacao',
            'diretor',
            'ano_lancamento',
            'sinopse',
        ]
        error_messages = {
            'titulo': {'required': 'Informe o titulo do filme.'},
            'genero': {'required': 'Informe o genero do filme.'},
            'duracao_minutos': {'required': 'Informe a duracao do filme.'},
            'classificacao': {'required': 'Informe a classificacao do filme.'},
        }
