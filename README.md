# SAM-TI

Sistema web para avaliação de maturidade de TI, desenvolvido em Django, com banco MariaDB/MySQL.

## Visão Geral

O projeto permite cadastrar empresas, organizar um banco de questões por categoria, criar avaliações, responder questionários com evidências ou providências, gerar relatórios de maturidade e consultar auditoria das respostas.

Perfis disponíveis:
- `Administrador`
- `Consultor/Governança`
- `Diretoria/Stakeholder`

## Requisitos Do Sistema

Para executar o projeto fora de Docker:
- Python `3.12+`
- pip
- virtualenv
- MariaDB ou MySQL disponível
- bibliotecas de compilação compatíveis com `mysqlclient`

Dependências Python do projeto:
- `django==6.0.3`
- `mysqlclient==2.2.7`

## Variáveis De Ambiente

Variáveis obrigatórias para o banco:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Variáveis opcionais:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_APP_PORT`

Exemplo:

```bash
export DB_NAME=sam_ti
export DB_USER=sam_ti_user
export DB_PASSWORD=sam_ti_pass
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
export DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost
export DJANGO_APP_PORT=2332
```

## Como Rodar Com Docker

O ambiente Docker já sobe a aplicação e o banco MariaDB.

```bash
docker compose up --build
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:2332/login/
```

Serviços:
- `web`: aplicação Django
- `db`: banco MariaDB

Para subir em segundo plano:

```bash
docker compose up -d --build
```

Para derrubar os containers:

```bash
docker compose down
```

## Como Rodar Sem Docker

1. Crie e ative a virtualenv.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências.

```bash
pip install -r requirements.txt
```

3. Exporte as variáveis de ambiente do banco.

```bash
export DB_NAME=sam_ti
export DB_USER=sam_ti_user
export DB_PASSWORD=sam_ti_pass
export DB_HOST=127.0.0.1
export DB_PORT=3306
```

4. Aplique as migrações.

```bash
python manage.py migrate
```

5. Crie o usuário administrador.

```bash
python manage.py createsuperuser
```

6. Inicie o servidor.

```bash
python manage.py runserver
```

URL padrão:

```text
http://127.0.0.1:2332/login/
```

## Criar Usuário Administrador

O acesso inicial ao sistema é feito pelo usuário criado com:

```bash
python manage.py createsuperuser
```

Esse usuário poderá:
- acessar `/admin`
- entrar no sistema pela tela de login
- visualizar e operar telas administrativas

Observação:
- o superusuário do Django não substitui o papel de negócio sozinho
- o sistema usa o modelo `Profile` para controlar o perfil funcional do usuário

Depois de criar o usuário, ajuste o perfil em `/admin`:
- abra `Profile`
- associe o usuário ao papel desejado
- use `ADMIN` para administrador completo

## Perfis E Permissões

### Administrador

Pode:
- acessar dashboard
- cadastrar empresas
- cadastrar categorias
- cadastrar e editar questões
- criar avaliações
- visualizar qualquer avaliação
- responder avaliações às quais tenha acesso
- concluir avaliações
- consultar auditoria
- acessar relatórios

### Consultor/Governança

Pode:
- acessar dashboard
- cadastrar empresas
- criar avaliações
- visualizar avaliações sob sua responsabilidade ou nas quais participa
- responder questões dessas avaliações
- concluir avaliações pelas quais é responsável
- consultar auditoria das avaliações pelas quais é responsável
- acessar relatórios das avaliações às quais tem acesso

### Diretoria/Stakeholder

Pode:
- acessar dashboard
- visualizar avaliações nas quais participa
- responder questões dessas avaliações
- visualizar relatórios das avaliações às quais tem acesso

Não pode:
- cadastrar empresas
- criar avaliações
- cadastrar categorias
- cadastrar questões
- concluir avaliações
- consultar auditoria gerencial

## Fluxo Básico De Uso

1. Criar um usuário administrador.
2. Entrar em `/admin`.
3. Ajustar o `Profile` dos usuários.
4. Cadastrar categorias de questões.
5. Cadastrar questões.
6. Cadastrar empresas.
7. Criar uma avaliação.
8. Definir consultor responsável e participantes.
9. Responder o questionário.
10. Gerar relatório.
11. Concluir a avaliação quando o ciclo terminar.

## Regras De Negócio Importantes

Na resposta do questionário:
- `SIM` exige evidência em texto ou arquivo
- `NÃO` exige providência

Nas avaliações:
- avaliações concluídas não aceitam novas alterações
- cada questão tem uma única resposta por avaliação
- toda resposta gera registro de auditoria

## Telas Disponíveis

### Autenticação

- `/login/`
  Tela de login do sistema.

- `/logout/`
  Encerramento de sessão.

### Painel Inicial

- `/`
  Dashboard com resumo do perfil, empresas, questões e avaliações recentes.

### Empresas

- `/empresas/`
  Lista de empresas cadastradas.

- `/empresas/nova/`
  Cadastro de nova empresa.

### Categorias

- `/categorias/`
  Lista de categorias de questões.

- `/categorias/nova/`
  Cadastro de categoria.

### Questões

- `/questoes/`
  Lista do banco de questões.

- `/questoes/nova/`
  Cadastro de nova questão.

- `/questoes/<id>/editar/`
  Edição de questão existente.

### Avaliações

- `/avaliacoes/`
  Lista de avaliações visíveis ao usuário autenticado.

- `/avaliacoes/nova/`
  Cadastro de nova avaliação.

- `/avaliacoes/<id>/`
  Detalhes da avaliação, progresso e acesso às respostas.

- `/avaliacoes/<avaliacao_id>/questoes/<questao_id>/`
  Tela para responder uma questão da avaliação.

- `/avaliacoes/<id>/relatorio/`
  Relatório consolidado da maturidade.

- `/avaliacoes/<id>/auditoria/`
  Log de auditoria das respostas.

- `/avaliacoes/<id>/concluir/`
  Endpoint de conclusão da avaliação, acionado por `POST`.

### Administração Django

- `/admin/`
  Painel administrativo padrão do Django.

## Estrutura Funcional Do Projeto

- `avaliacao/models.py`
  Modelos de domínio e regras principais.

- `avaliacao/views.py`
  Fluxos das telas, permissões e ações do sistema.

- `avaliacao/forms.py`
  Formulários do sistema.

- `avaliacao/services.py`
  Cálculo de score, classificação e geração de relatório.

- `templates/`
  Templates HTML.

- `static/`
  Arquivos estáticos da interface.

- `sam_ti/settings.py`
  Configuração principal do Django e conexão com banco.

## Operações Úteis

Aplicar migrações:

```bash
python manage.py migrate
```

Criar superusuário:

```bash
python manage.py createsuperuser
```

Coletar estáticos:

```bash
python manage.py collectstatic
```

Abrir shell do Django:

```bash
python manage.py shell
```

## Solução De Problemas

### Erro de conexão com banco

Verifique:
- se o MariaDB/MySQL está ativo
- se `DB_HOST` e `DB_PORT` estão corretos
- se `DB_NAME`, `DB_USER` e `DB_PASSWORD` existem no banco

### Erro de CSRF

Verifique:
- se está acessando a URL correta
- se `DJANGO_ALLOWED_HOSTS` contém o host usado
- se `DJANGO_CSRF_TRUSTED_ORIGINS` contém a origem usada
- se a aplicação foi reiniciada após alterar variáveis de ambiente

### Usuário entra mas não acessa telas esperadas

Verifique o papel do usuário em:

```text
/admin
```

O acesso funcional depende do `Profile.role`.
