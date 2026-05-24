from collections import defaultdict

from .models import LogAuditoriaResposta, Questao, Resposta, RespostaEscolha


MATURIDADE_INFO = {
    "Artesanal (Reativo)": {
        "descricao": "A TI opera de forma reativa, dependente de esforço manual e com baixa padronização.",
        "implicacoes": "O ambiente tende a sofrer com urgências frequentes, baixa previsibilidade e conhecimento concentrado em poucas pessoas.",
        "recomendacoes": [
            "Centralizar o atendimento e o registro de incidentes.",
            "Documentar processos críticos, ativos e responsáveis.",
            "Definir prioridades de curto prazo para estabilização operacional.",
        ],
    },
    "Eficiente (Proativo)": {
        "descricao": "A TI já possui processos básicos definidos e começa a agir preventivamente sobre riscos e incidentes.",
        "implicacoes": "Há ganho de controle operacional, mas ainda existem lacunas de integração, governança e padronização completa.",
        "recomendacoes": [
            "Ampliar monitoramento e indicadores de desempenho.",
            "Formalizar políticas e rotinas recorrentes.",
            "Expandir automações com foco em escala e consistência.",
        ],
    },
    "Eficaz (Otimizado)": {
        "descricao": "A TI opera com processos maduros, monitoramento estruturado e forte alinhamento com objetivos do negócio.",
        "implicacoes": "A operação é estável e mensurável, permitindo melhorar eficiência e reduzir riscos com mais previsibilidade.",
        "recomendacoes": [
            "Refinar métricas ligadas a resultado de negócio.",
            "Aprimorar governança, gestão de risco e melhoria contínua.",
            "Priorizar iniciativas de inovação com retorno mensurável.",
        ],
    },
    "Estratégico": {
        "descricao": "A TI atua como habilitadora estratégica do negócio, com alto nível de integração, resiliência e inovação.",
        "implicacoes": "A área deixa de ser apenas suporte e passa a influenciar diretamente decisões, crescimento e diferenciação competitiva.",
        "recomendacoes": [
            "Preservar a governança e revisar continuamente os indicadores estratégicos.",
            "Investir em inovação, escalabilidade e vantagem competitiva.",
            "Disseminar a cultura de colaboração entre TI e áreas de negócio.",
        ],
    },
}


def calcular_classificacao(score_geral: float) -> str:
    if score_geral <= 49:
        return "Artesanal (Reativo)"
    if score_geral <= 79:
        return "Eficiente (Proativo)"
    if score_geral <= 90:
        return "Eficaz (Otimizado)"
    return "Estratégico"


def _calcular_score_ponderado(respostas):
    total_peso = 0
    total_peso_sim = 0

    for r in respostas:
        peso = r.questao.peso if r.questao and r.questao.peso else 1
        total_peso += peso
        if r.resposta == RespostaEscolha.SIM:
            total_peso_sim += peso

    score = round((total_peso_sim / total_peso) * 100, 2) if total_peso else 0
    return score, total_peso, total_peso_sim


def _benchmark_setor(avaliacao):
    if not avaliacao.empresa.setor:
        return None

    # Benchmark simples: média de score ponderado das avaliações concluídas do mesmo setor
    # (exceto a avaliação atual)
    avaliacoes_setor = (
        avaliacao.__class__.objects.filter(
            empresa__setor=avaliacao.empresa.setor,
            status="CONCLUIDA",
        )
        .exclude(id=avaliacao.id)
        .select_related("empresa")
    )

    scores = []
    for av in avaliacoes_setor:
        respostas_av = (
            Resposta.objects.filter(avaliacao=av)
            .select_related("questao")
        )
        score_av, _, _ = _calcular_score_ponderado(respostas_av)
        scores.append(score_av)

    if not scores:
        return None

    media = round(sum(scores) / len(scores), 2)
    return {
        "setor": avaliacao.empresa.setor,
        "media_setor": media,
        "amostra": len(scores),
    }


def _historico_empresa(avaliacao):
    historico = (
        avaliacao.__class__.objects.filter(empresa=avaliacao.empresa)
        .exclude(id=avaliacao.id)
        .order_by("criada_em")
    )

    itens = []
    for av in historico:
        respostas_av = (
            Resposta.objects.filter(avaliacao=av)
            .select_related("questao")
        )
        score_av, _, _ = _calcular_score_ponderado(respostas_av)
        itens.append(
            {
                "id": av.id,
                "nome": av.nome,
                "criada_em": av.criada_em,
                "score": score_av,
                "status": av.status,
            }
        )
    return itens


def gerar_relatorio(avaliacao):
    respostas = (
        Resposta.objects.filter(avaliacao=avaliacao)
        .select_related("questao__categoria", "questao", "plano_acao")
        .order_by("questao__categoria__nome")
    )

    total = respostas.count()
    total_sim = respostas.filter(resposta=RespostaEscolha.SIM).count()

    score_geral, total_peso, total_peso_sim = _calcular_score_ponderado(respostas)
    classificacao = calcular_classificacao(score_geral)
    explicacao = MATURIDADE_INFO[classificacao]

    por_categoria = defaultdict(lambda: {"total": 0, "sim": 0, "peso_total": 0, "peso_sim": 0})
    plano_acao = []

    for r in respostas:
        categoria = r.questao.categoria.nome
        peso = r.questao.peso if r.questao and r.questao.peso else 1

        por_categoria[categoria]["total"] += 1
        por_categoria[categoria]["peso_total"] += peso

        if r.resposta == RespostaEscolha.SIM:
            por_categoria[categoria]["sim"] += 1
            por_categoria[categoria]["peso_sim"] += peso

        if r.resposta == RespostaEscolha.NAO and r.providencia:
            plano_acao.append(r)

    score_categoria = []
    for categoria, dados in por_categoria.items():
        score = round((dados["peso_sim"] / dados["peso_total"]) * 100, 2) if dados["peso_total"] else 0
        score_categoria.append(
            {
                "categoria": categoria,
                "score": score,
                "total": dados["total"],
                "peso_total": dados["peso_total"],
            }
        )

    benchmark = _benchmark_setor(avaliacao)
    historico = _historico_empresa(avaliacao)

    return {
        "total_respondido": total,
        "total_sim": total_sim,
        "score_geral": score_geral,
        "classificacao": classificacao,
        "descricao_maturidade": explicacao["descricao"],
        "implicacoes_maturidade": explicacao["implicacoes"],
        "recomendacoes_maturidade": explicacao["recomendacoes"],
        "score_categoria": sorted(score_categoria, key=lambda x: x["categoria"]),
        "plano_acao": plano_acao,
        "total_peso": total_peso,
        "total_peso_sim": total_peso_sim,
        "benchmark": benchmark,
        "historico": historico,
    }


def registrar_log_resposta(resposta: Resposta, usuario):
    nome_arquivo = resposta.evidencia_arquivo.name if resposta.evidencia_arquivo else ""
    LogAuditoriaResposta.objects.create(
        resposta_registro=resposta,
        usuario=usuario,
        resposta=resposta.resposta,
        evidencia_descricao=resposta.evidencia_descricao,
        evidencia_arquivo_nome=nome_arquivo,
        providencia=resposta.providencia,
    )


def progresso_avaliacao(avaliacao):
    total_questoes = Questao.objects.filter(ativa=True).count()
    respondidas = avaliacao.total_respostas()
    percentual = round((respondidas / total_questoes) * 100, 1) if total_questoes else 0
    return {"total_questoes": total_questoes, "respondidas": respondidas, "percentual": percentual}