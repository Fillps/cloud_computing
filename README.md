# Cloud computing

Projeto de desenvolvimento para a disciplina Engenharia de Software N - 2017/2

# Rodando o projeto

Para rodar o projeto localmente clone ou baixe o conteúdo desse repositório em uma pasta. Utilize o [virtualenv](https://virtualenv.pypa.io/en/stable/):

```bash
mkdir env
virtualenv env
```
Linux
```bash
source env/bin/activate
```
Windows
```bash
env/Scripts/activate
```

Em seguida instale o projeto com edição habilitada:

```bash
pip install -e .
```

Exporte a variável de aplicação do Flask:

Linux
```bash
export FLASK_APP=cloud_computing
```
Windows
```bash
setx FLASK_APP "cloud_computing\__init__.py"
```

Inicialize o banco de dados:

```bash
flask initdb
```

Rode o aplicativo e acesse o endereço informado na linha de comando:

```bash
flask run
```
