# Cloud computing

Projeto de desenvolvimento para a disciplina Engenharia de Software N - 2017/2

# Rodando o projeto

Para rodar o projeto localmente clone ou baixe o conteúdo desse repositório em uma pasta. Utilize o [virtualenv](https://virtualenv.pypa.io/en/stable/):

```bash
mkdir env
virtualenv -p python3 env
source env/bin/activate
```

Em seguida instale o projeto com edição habilitada:

```bash
pip install -e .
```

Exporte a variável de aplicação do Flask:

```bash
export FLASK_APP=cloud_computing
```

Rode o aplicativo e acesse o endereço informado na linha de comando:

```bash
flask run
```
