# SAM-TI (Django + MySQL)

Aplicação para avaliação de maturidade de TI baseada no documento de requisitos fornecido.

## Arquitetura (MVC no Django)
- Model (`avaliacao/models.py`): domínio, regras de validação de resposta, auditoria e relacionamentos.
- Controller (`avaliacao/views.py`): fluxo da aplicação, permissões por perfil e orquestração das telas.
- View (`templates/` + `static/css/`): interface web responsiva para login, avaliação, relatório e auditoria.
- Services (`avaliacao/services.py`): regras de negócio de score, classificação e progresso.

## Requisitos implementados
- RF01: perfis (`Administrador`, `Consultor/Governança`, `Diretoria/Stakeholder`) com segregação de funções.
- RF02: cadastro de empresas e histórico de avaliações por empresa.
- RF03: banco de questões por categoria de maturidade.
- RF04: workflow com regra obrigatória:
  - `SIM` exige evidência (descrição ou arquivo).
  - `NÃO` exige providência.
  - colaboração via participantes da avaliação.
- RF05: relatório com score por área, score geral (0-100), classificação automática e plano de ação.
- RNF Auditabilidade: log de quem respondeu, quando e qual evidência/providência foi registrada.

## Como executar
```bash
cd /home/yuri/Documentos/governaca_ti
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Acesse: `http://127.0.0.1:2332/login/`

## Como executar com Docker
```bash
cd /home/yuri/Documentos/governaca_ti
docker compose up --build
```

O container aplica as migrações automaticamente na inicialização e expõe a aplicação em `http://127.0.0.1:2332/login/`.

## Observações
- Perfis de usuário podem ser definidos no Django Admin (`/admin`) no cadastro de `Profile`.
- O banco padrão no Docker Compose é MySQL.
- Os dados do MySQL ficam persistidos no volume `mysql_data`, então reiniciar containers não apaga os dados.
