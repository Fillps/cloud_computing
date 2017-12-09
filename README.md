# [Cloud computing](https://stormy-plains-13611.herokuapp.com/)

Projeto de desenvolvimento para a disciplina Engenharia de Software N - 2017/2

# Rodando o projeto

Para rodar o projeto localmente clone ou baixe o conteúdo desse repositório em uma pasta. Utilize o [pipenv](https://pypi.python.org/pypi/pipenv) para criar o ambiente virtual e instalar as dependências:

```bash
pipenv --three
pipenv install
pipenv shell
```

Com o [heroku](https://devcenter.heroku.com/articles/heroku-cli), rode o aplicativo localmente e acesse o endereço informado na linha de comando:

```bash
export DATABASE_URL=$(heroku config:get DATABASE_URL -a stormy-plains-13611)
heroku local web
```

Para rodar localmente sem o [heroku](https://devcenter.heroku.com/articles/heroku-cli):

```bash
export DATABASE_URL=postgres://smpsmnkhtfugpw:d70650378be28a64671e1d5cc320ac7189a1bbcd7a3566c1d5022cd8ed875b5f@ec2-54-235-90-125.compute-1.amazonaws.com:5432/d4o6b2ii9q94ip
python runserver.py
```

Para rodar os testes é necessário ter o [PostgresSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) instalado e criar um banco de dados chamado 'cloud_computing_tests'. Para iniciar os testes basta digitar o comando:
```bash
py.test
```
