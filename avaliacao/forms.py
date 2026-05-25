from django import forms
from django.contrib.auth import get_user_model

from .models import (
    Avaliacao,
    CategoriaQuestao,
    Empresa,
    MetaIndicador,
    ObjetivoEstrategicoPDTI,
    PDTI,
    PlanoAcao,
    Questao,
    Resposta,
    RiscoAvaliacao,
    UserRole,
)

User = get_user_model()


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nome", "cnpj", "setor"]


class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ["categoria", "texto", "framework_origem", "referencia", "peso", "ativa"]


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


class PlanoAcaoForm(forms.ModelForm):
    class Meta:
        model = PlanoAcao
        fields = [
            "responsavel",
            "data_limite",
            "status",
            "where_local",
            "how",
            "how_much",
            "custo_valor",
            "custo_natureza",
            "custo_recorrencia",
        ]
        widgets = {
            "data_limite": forms.DateInput(attrs={"type": "date"}),
            "how": forms.Textarea(attrs={"rows": 2}),
        }


class PlanoAcaoInlineForm(forms.ModelForm):
    """Form compacto para edição inline na página 5W2H."""

    class Meta:
        model = PlanoAcao
        fields = [
            "responsavel",
            "data_limite",
            "status",
            "where_local",
            "how",
            "how_much",
            "custo_valor",
            "custo_natureza",
            "custo_recorrencia",
        ]
        widgets = {
            "data_limite": forms.DateInput(attrs={"type": "date", "class": "input-compact"}),
            "how": forms.Textarea(attrs={"rows": 2, "class": "input-compact"}),
            "where_local": forms.TextInput(attrs={"class": "input-compact"}),
            "how_much": forms.TextInput(attrs={"class": "input-compact"}),
            "custo_valor": forms.NumberInput(attrs={"class": "input-compact", "step": "0.01"}),
            "custo_natureza": forms.Select(attrs={"class": "input-compact"}),
            "custo_recorrencia": forms.Select(attrs={"class": "input-compact"}),
        }


class RiscoAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = RiscoAvaliacao
        fields = ["titulo", "descricao", "impacto", "probabilidade", "status", "responsavel", "plano_mitigacao"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "plano_mitigacao": forms.Textarea(attrs={"rows": 3}),
        }


class MetaIndicadorForm(forms.ModelForm):
    class Meta:
        model = MetaIndicador
        fields = ["nome_indicador", "unidade", "situacao_atual", "ano_conclusao", "meta_conclusao", "observacoes"]
        widgets = {
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }


class ObjetivoEstrategicoPDTIForm(forms.ModelForm):
    class Meta:
        model = ObjetivoEstrategicoPDTI
        fields = ["objetivo", "resultado_esperado", "ano"]


class PDTIForm(forms.ModelForm):
    class Meta:
        model = PDTI
        fields = [
            "introducao",
            "objetivos_estrategicos_texto",
            "analise_situacional",
            "diagnostico_samti",
            "analise_de_riscos",
            "estrutura_governanca",
            "roadmap_evolucao",
            "visao_de_futuro",
            "conclusao",
        ]
        widgets = {
            "introducao": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "objetivos_estrategicos_texto": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "analise_situacional": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "diagnostico_samti": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "analise_de_riscos": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "estrutura_governanca": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "roadmap_evolucao": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "visao_de_futuro": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
            "conclusao": forms.Textarea(attrs={"rows": 4, "style": "width: 100%;"}),
        }
