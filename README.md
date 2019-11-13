# Sistema Nacional de Cultura
[![Build Status](https://travis-ci.org/culturagovbr/sistema-nacional-cultura.svg?branch=master)](https://travis-ci.org/culturagovbr/sistema-nacional-cultura)  
[![Maintainability](https://api.codeclimate.com/v1/badges/b820f182e3e161f417a3/maintainability)](https://codeclimate.com/github/culturagovbr/sistema-nacional-cultura/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/b820f182e3e161f417a3/test_coverage)](https://codeclimate.com/github/culturagovbr/sistema-nacional-cultura/test_coverage)

O Sistema Nacional de Cultura é um modelo de gestão e promoção de políticas públicas de cultura que pressupõe a ação conjunta dos entes da federação (governos federal, estadual e municipal) para democratização do setor. (http://pt.wikipedia.org/wiki/Sistema_Nacional_de_Cultura)

Este aplicativo cadastra os entes federados e coordena o processo de adesao desses no SNC. Por meio deste cadastro, os estados e municípios podem gerar seus acordos de cooperação técnica para a entrada no SNC, e também manter atualizados os dados de monitoramentos das metas pactuadas no ACT.

## Da Tecnologia
O cadastro do SNC é feito sobre o framework Django, usando Python3, com banco de dados PostgresSQL. É possível rodar em qualquer banco de dados, basta ajustar as settings.
As dependencias de pacotes estão no Pipfile.


## Requisitos

* Python3
* PIP
* python3-virtualenv
* Postgresql
* wkhtmltopdf
* pipenv
* postgresql-server-dev-9.4

## Passos da Instalação para Debian/Ubuntu

1. Instale o PIP que é o instalador de pacotes do python3
    ```
    sudo apt-get install python3-pip python3-dev
    ```

2. Instale o pipenv que é o gerenciador de pacotes e ambiente python
    ```
    pip3 install --user --upgrade pipenv
    ```

3. Instale o PostgreSQL e as bibliotecas de desenvolvimento
    ```
    sudo apt-get install postgresql-9.4 libpq-dev
    ```    

4. Clone o repositório do projeto do github
    ```
    git clone https://github.com/culturagovbr/sistema-nacional-cultura.git snc
    ```

5. Crie o ambiente virtual e instale as dependencias, dentro do diretório da aplicação
    ```
    cd snc
    pipenv install
    ```    
    Você pode instalar as dependencias incluindo as necessárias ao desenvolvimento utilizando:
    ```
    pipenv install --dev
    ```

6. Ative o ambiente virtual
    ```
    pipenv shell
    ```

7. Copie o template de configurações de ambiente e edite conforme necessário
    ```
    cp env.tmpl snc/.env
    ```

8. Configure o banco de dados
    Crie o banco dbsnc no seu serviço de acordo com o settings.py ou seu arquivo .env
    ```
    sudo -u postgres psql
    CREATE DATABASE dbsnc;
    \q
    ```

9. Execute os comandos de criação do banco
    Criação de migração para cada APP
    ```
    ./manage.py makemigrations planotrabalho gestao adesao
    ```

    Comando migrate para criar a estrutura do banco (DDL)
    ```
    ./manage.py migrate
    ```

10. Copie os arquivos estaticos do projeto
    ```
    ./manage.py collectstatic
    ```

11. Execute a aplicação (É preciso ter o ambiente virtual ativado)
    ```
    ./manage.py runserver
    ```

## Utilizando o docker

1. Copie o template de configurações de ambiente e edite conforme necessário
    ```
    cp env.tmpl snc/.env
    ```

2. Execute o serviço do banco de dados em background
    ```
    sudo docker-compose up -d db
    ```

3.  Execute o serviço da aplicação
    ```
    sudo docker-compose up web
    ```

4. Entre no container da aplicação (substitua container_id pelo ID do container)
    ```
    sudo docker exec -it container_id bash
    ```

5. Dentro do container da aplicação, execute o comando migrate para criar a estrutura do banco
    ```
    ./manage.py migrate
    ```

6. Dentro do container da aplicação, copie os arquivos estaticos do projeto
    ```
    ./manage.py collectstatic
    ```

A aplicação estará disponível na porta 8000