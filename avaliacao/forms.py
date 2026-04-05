from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Avaliacao, CategoriaQuestao, Empresa, Questao, Resposta, UserRole

User = get_user_model()

User = get_user_model()


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "cnpj", "setor"]


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ["categoria", "texto", "ativa"]


class CategoriaQuestaoForm(forms.ModelForm):
    class Meta:
        model = CategoriaQuestao
        fields = ["nome", "descricao"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }


class AvaliacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["consultor_responsavel"].queryset = User.objects.filter(profile__role=UserRole.CONSULTOR)
        self.fields["participantes"].queryset = User.objects.exclude(profile__role=UserRole.ADMIN)

    class Meta:
        model = Avaliacao
        fields = ["empresa", "nome", "consultor_responsavel", "participantes", "status"]
        widgets = {
            "participantes": forms.CheckboxSelectMultiple,
        }


class RespostaForm(forms.ModelForm):
    class Meta:
        model = Resposta
        fields = ["resposta", "evidencia_descricao", "evidencia_arquivo", "providencia"]
        widgets = {
            "evidencia_descricao": forms.Textarea(attrs={"rows": 3}),
            "providencia": forms.Textarea(attrs={"rows": 3}),
        }


class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    empresa_nome = forms.CharField(label="Nome da empresa", max_length=150)
    empresa_cnpj = forms.CharField(label="CNPJ", max_length=18, required=False)
    empresa_setor = forms.CharField(label="Setor", max_length=100, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Empresa.objects.create(
                owner=user,
                nome=self.cleaned_data["empresa_nome"],
                cnpj=self.cleaned_data.get("empresa_cnpj", ""),
                setor=self.cleaned_data.get("empresa_setor", ""),
            )
        return user
