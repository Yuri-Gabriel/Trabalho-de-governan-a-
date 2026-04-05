from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .decorators import role_required
from .forms import AvaliacaoForm, CadastroForm, EmpresaForm, QuestaoForm, RespostaForm
from .models import (
    Avaliacao,
    AvaliacaoStatus,
    CategoriaQuestao,
    Empresa,
    LogAuditoriaResposta,
    Questao,
    Resposta,
    UserRole,
)
from .services import gerar_relatorio, progresso_avaliacao, registrar_log_resposta

def _usuario_acessa_avaliacao(usuario, avaliacao):
    perfil = getattr(usuario, "profile", None)
    if not perfil:
        return False

    if perfil.role == UserRole.ADMIN:
        return True

    if perfil.role == UserRole.CONSULTOR:
        return (
            avaliacao.consultor_responsavel_id == usuario.id
            or avaliacao.participantes.filter(id=usuario.id).exists()
        )

    return avaliacao.participantes.filter(id=usuario.id).exists()


def _usuario_pode_gerenciar_empresas(usuario):
    perfil = getattr(usuario, "profile", None)
    if not perfil:
        return False
    return perfil.role in {UserRole.ADMIN, UserRole.CONSULTOR, UserRole.DIRETORIA}


def _empresas_visiveis_usuario(usuario):
    perfil = getattr(usuario, "profile", None)
    if perfil and perfil.role in {UserRole.ADMIN, UserRole.CONSULTOR}:
        return Empresa.objects.all()
    return Empresa.objects.filter(owner=usuario)


def cadastro(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("dashboard")
    else:
        form = CadastroForm()
    return render(request, "auth/cadastro.html", {"form": form})


@login_required
def dashboard(request):
    perfil = getattr(request.user, "profile", None)
    if not perfil:
        messages.error(request, "Seu usuário não possui perfil definido.")
        return redirect("logout")

    avaliacoes = Avaliacao.objects.select_related("empresa", "consultor_responsavel")
    if perfil.role != UserRole.ADMIN:
        avaliacoes = avaliacoes.filter(participantes=request.user) | avaliacoes.filter(
            consultor_responsavel=request.user
        )

    context = {
        "perfil": perfil,
        "empresas_total": Empresa.objects.count(),
        "questoes_total": Questao.objects.filter(ativa=True).count(),
        "avaliacoes": avaliacoes.distinct()[:10],
    }
    return render(request, "avaliacao/dashboard.html", context)


@login_required
def empresa_list(request):
    if not _usuario_pode_gerenciar_empresas(request.user):
        messages.error(request, "Você não tem permissão para acessar empresas.")
        return redirect("dashboard")
    empresas = _empresas_visiveis_usuario(request.user).order_by("nome")
    return render(request, "avaliacao/empresa_list.html", {"empresas": empresas})


@login_required
def empresa_create(request):
    if not _usuario_pode_gerenciar_empresas(request.user):
        messages.error(request, "Você não tem permissão para cadastrar empresas.")
        return redirect("dashboard")

    if request.method == "POST":
        form = EmpresaForm(request.POST)
        if form.is_valid():
            empresa = form.save(commit=False)
            if empresa.owner_id is None:
                empresa.owner = request.user
            empresa.save()
            messages.success(request, "Empresa cadastrada.")
            return redirect("empresa_list")
    else:
        form = EmpresaForm()
    return render(request, "avaliacao/form.html", {"form": form, "titulo": "Nova Empresa"})


@role_required(UserRole.ADMIN)
def questao_list(request):
    questoes = Questao.objects.select_related("categoria").all().order_by("categoria__nome")
    return render(request, "avaliacao/questao_list.html", {"questoes": questoes})


@role_required(UserRole.ADMIN)
def categoria_list(request):
    categorias = CategoriaQuestao.objects.all().order_by("nome")
    return render(request, "avaliacao/categoria_list.html", {"categorias": categorias})


@role_required(UserRole.ADMIN)
@require_http_methods(["GET", "POST"])
def categoria_create(request):
    if request.method == "POST":
        form = CategoriaQuestaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Categoria cadastrada.")
            return redirect("categoria_list")
    else:
        form = CategoriaQuestaoForm()
    return render(request, "avaliacao/form.html", {"form": form, "titulo": "Nova Categoria"})


@role_required(UserRole.ADMIN)
@require_http_methods(["GET", "POST"])
def questao_create(request):
    if request.method == "POST":
        form = QuestaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão cadastrada.")
            return redirect("questao_list")
    else:
        form = QuestaoForm()
    return render(request, "avaliacao/form.html", {"form": form, "titulo": "Nova Questão"})


@role_required(UserRole.ADMIN)
@require_http_methods(["GET", "POST"])
def questao_update(request, questao_id):
    questao = get_object_or_404(Questao, id=questao_id)
    if request.method == "POST":
        form = QuestaoForm(request.POST, instance=questao)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão atualizada.")
            return redirect("questao_list")
    else:
        form = QuestaoForm(instance=questao)
    return render(request, "avaliacao/form.html", {"form": form, "titulo": "Editar Questão"})


@login_required
def avaliacao_list(request):
    perfil = getattr(request.user, "profile", None)
    if not perfil:
        messages.error(request, "Seu usuário não possui perfil definido.")
        return redirect("logout")

    avaliacoes = Avaliacao.objects.select_related("empresa", "consultor_responsavel")

    if perfil.role == UserRole.ADMIN:
        pass
    elif perfil.role == UserRole.CONSULTOR:
        avaliacoes = avaliacoes.filter(
            Q(consultor_responsavel=request.user) | Q(participantes=request.user)
        ).distinct()
    else:
        avaliacoes = avaliacoes.filter(participantes=request.user).distinct()

    return render(request, "avaliacao/avaliacao_list.html", {"avaliacoes": avaliacoes})


@role_required(UserRole.ADMIN, UserRole.CONSULTOR)
@require_http_methods(["GET", "POST"])
def avaliacao_create(request):
    if request.method == "POST":
        form = AvaliacaoForm(request.POST)
        form.fields["empresa"].queryset = _empresas_visiveis_usuario(request.user)
        if form.is_valid():
            avaliacao = form.save()
            avaliacao.participantes.add(avaliacao.consultor_responsavel)
            messages.success(request, "Avaliação criada.")
            return redirect("avaliacao_detail", avaliacao_id=avaliacao.id)
    else:
        form = AvaliacaoForm(initial={"consultor_responsavel": request.user})
        form.fields["empresa"].queryset = _empresas_visiveis_usuario(request.user)
    return render(request, "avaliacao/form.html", {"form": form, "titulo": "Nova Avaliação"})


@login_required
def avaliacao_detail(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if not _usuario_acessa_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem acesso a esta avaliação.")
        return redirect("dashboard")

    questoes = Questao.objects.select_related("categoria").filter(ativa=True).order_by("categoria__nome", "id")
    respostas = {
        resposta.questao_id: resposta
        for resposta in Resposta.objects.filter(avaliacao=avaliacao).select_related("respondido_por")
    }

    return render(
        request,
        "avaliacao/avaliacao_detail.html",
        {
            "avaliacao": avaliacao,
            "questoes": questoes,
            "respostas": respostas,
            "progresso": progresso_avaliacao(avaliacao),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def responder_questao(request, avaliacao_id, questao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    questao = get_object_or_404(Questao, id=questao_id, ativa=True)

    if not _usuario_acessa_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem acesso para responder esta avaliação.")
        return redirect("dashboard")

    if avaliacao.status == AvaliacaoStatus.CONCLUIDA:
        messages.error(request, "Avaliações concluídas não podem mais receber alterações.")
        return redirect("avaliacao_detail", avaliacao_id=avaliacao.id)

    resposta = Resposta.objects.filter(avaliacao=avaliacao, questao=questao).first()

    if request.method == "POST":
        form = RespostaForm(request.POST, request.FILES, instance=resposta)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.avaliacao = avaliacao
            registro.questao = questao
            registro.respondido_por = request.user
            registro.save()
            registrar_log_resposta(registro, request.user)
            messages.success(request, "Resposta registrada com sucesso.")
            return redirect("avaliacao_detail", avaliacao_id=avaliacao.id)
    else:
        form = RespostaForm(instance=resposta)

    return render(
        request,
        "avaliacao/responder_questao.html",
        {"form": form, "avaliacao": avaliacao, "questao": questao, "resposta": resposta},
    )


@login_required
def relatorio(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if not _usuario_acessa_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem acesso a este relatório.")
        return redirect("dashboard")

    dados = gerar_relatorio(avaliacao)
    return render(request, "avaliacao/relatorio.html", {"avaliacao": avaliacao, **dados})


@login_required
def relatorio_print(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if not _usuario_acessa_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem acesso a este relatório.")
        return redirect("dashboard")

    dados = gerar_relatorio(avaliacao)
    return render(request, "avaliacao/relatorio_print.html", {"avaliacao": avaliacao, **dados})


@role_required(UserRole.ADMIN, UserRole.CONSULTOR)
@require_POST
def concluir_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if not _usuario_gerencia_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem permissão para concluir esta avaliação.")
        return redirect("dashboard")

    if avaliacao.status == AvaliacaoStatus.CONCLUIDA:
        messages.info(request, "A avaliação já estava concluída.")
    else:
        avaliacao.status = AvaliacaoStatus.CONCLUIDA
        avaliacao.save(update_fields=["status"])
        messages.success(request, "Avaliação marcada como concluída.")
    return redirect("avaliacao_detail", avaliacao_id=avaliacao.id)


@role_required(UserRole.ADMIN, UserRole.CONSULTOR)
def auditoria(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if not _usuario_gerencia_avaliacao(request.user, avaliacao):
        messages.error(request, "Você não tem permissão para consultar a auditoria desta avaliação.")
        return redirect("dashboard")

    logs = LogAuditoriaResposta.objects.filter(resposta_registro__avaliacao=avaliacao).select_related(
        "usuario", "resposta_registro__questao"
    )
    return render(request, "avaliacao/auditoria.html", {"avaliacao": avaliacao, "logs": logs})
