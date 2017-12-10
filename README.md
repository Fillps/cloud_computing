# [Cloud computing](https://stormy-plains-13611.herokuapp.com/)

Projeto de desenvolvimento para a disciplina Engenharia de Software N - 2017/2

# Utilizando o projeto

Para rodar o projeto localmente clone ou baixe o conteúdo desse repositório em uma pasta. Utilize o [pipenv](https://pypi.python.org/pypi/pipenv) para criar o ambiente virtual e instalar as dependências:

```bash
pipenv --three
pipenv install
pipenv shell
```

## Selecionando o banco de dados

### Banco de dados local

Para rodar com um banco de dados local é necessário ter o [PostgresSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) instalado e criar um banco de dados chamado 'cloud_computing'. Selecione o arquivo de configuração 'configs/development.py' em 'runserver.py'.

### Banco de dados remoto

Para rodar o aplicativo com o banco de dados remoto de Heroku, exporte a variável do banco de dados da seguinte maneira:

```bash
export DATABASE_URL=$(heroku config:get DATABASE_URL -a stormy-plains-13611)
```

ou sem o Heroku:

```bash
export DATABASE_URL=postgres://smpsmnkhtfugpw:d70650378be28a64671e1d5cc320ac7189a1bbcd7a3566c1d5022cd8ed875b5f@ec2-54-235-90-125.compute-1.amazonaws.com:5432/d4o6b2ii9q94ip
```

## Rodando o app

Com o [heroku](https://devcenter.heroku.com/articles/heroku-cli), rode o aplicativo localmente e acesse o endereço informado na linha de comando:

```bash
heroku local web
```

ou sem o Heroku:

```bash
python runserver.py
```

## Testes

Para rodar os testes é necessário ter o [PostgresSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) instalado e criar um banco de dados chamado 'cloud_computing_tests'. Para iniciar os testes basta digitar o comando:

```bash
py.test
```

# Desenvolvimento

## Padrão de código

Para o desenvolvimento do código utilizamos o padrão [PEP-8](https://www.python.org/dev/peps/pep-0008). Algumas convenções internas são:

### Classes

Letras maiúsculas no início de cada palavra, com todas as palavras concatenadas. Variáveis definidas antes de funções:

```python
class PlanResource:
    backref_plan = 'plan_comps'
    quantity = db.Column(db.Integer)

    @declared_attr
    def plan_id(cls):
        return db.Column(db.Integer, db.ForeignKey('plan.id'),
                         primary_key=True)

    @declared_attr
    def plans(cls):
        return db.relationship('Plan', backref=db.backref(cls.backref_plan))
```

### Funções

Letras minúsculas no início de cada palavra, separadas por underlines:

```python
def show_homescreen():
    plans = Controller.get_plans()
    return render_template('shop-homepage.html', plans=plans)
```
