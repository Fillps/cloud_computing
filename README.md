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

Exporte as variáveis de aplicação do Flask e do Banco de Dados com Heroku (é necessário estar logado no heroku):

Linux
```bash
export FLASK_APP=cloud_computing
export DATABASE_URL=$(heroku config:get DATABASE_URL -a stormy-plains-13611)
```
Windows
```bash
setx FLASK_APP "cloud_computing\__init__.py"
setx DATABASE_URL (heroku config:get DATABASE_URL -a stormy-plains-13611)
```
Caso não tenha o Heroku instalado é necessário armazenar a URL do banco de dados manualmente, mas a URL muda periodicamente, precisando ser atualizada. No momento a URL pode ser exportada assim: 
```bash
export DATABASE_URL=postgres://smpsmnkhtfugpw:d70650378be28a64671e1d5cc320ac7189a1bbcd7a3566c1d5022cd8ed875b5f@ec2-54-235-90-125.compute-1.amazonaws.com:5432/d4o6b2ii9q94ip
```


Rode o aplicativo e acesse o endereço informado na linha de comando:

```bash
flask run
```
