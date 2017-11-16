# Sistema Nacional de Cultura
O Sistema Nacional de Cultura é um modelo de gestão e promoção de políticas públicas de cultura que pressupõe a ação conjunta dos entes da federação (governos federal, estadual e municipal) para democratização do setor. (http://pt.wikipedia.org/wiki/Sistema_Nacional_de_Cultura)

Este aplicativo cadastra os entes federados e coordena o processo de adesao desses no SNC. Por meio deste cadastro, os estados e municípios podem gerar seus acordos de cooperação técnica para a entrada no SNC, e também manter atualizados os dados de monitoramentos das metas pactuadas no ACT.

#Da Tecnologia
O cadastro do SNC é feito sobre o framework Python-Django, Python3, com banco de dados Postgres. É possível rodar em qualquer banco de dados, basta ajustar as settings.
As dependencias de pacotes estão no requirements.txt


## Requisitos

* Python3
* PIP
* python3-virtualenv
* Postgresql
* wkhtmltopdf
* postgresql-server-dev-9.4

## Passos da Instalação para Debian/Ubuntu

1. Instale o PIP que é o instalador de pacotes do python3

    Baixe o arquivo get-pip.py que é um arquivo instalador executado pelo Python. O arquivo se encontra no link https://bootstrap.pypa.io/get-pip.py.
O arquivo pode ser baixado de forma direta e rápida utilizando o comando wget -c. A opção -c tem a função de continuar o download em caso de perda de conexão.

    ```
    wget -c https://bootstrap.pypa.io/get-pip.py

    sudo python3 get-pip.py
    ```

2. Instale o construtor de ambiente virtual
    ```
    sudo apt-get install python3-virtualenv python3-venv
    ```

3. Instale o wkhtmltopdf que é o aplicativo para renderizar html em pdf
    ```
    sudo apt-get install wkhtmltopdf
    ```

4. Instale o PostgreSQL e as bibliotecas de desenvolvimento
    ```
    sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4

    ```    
5. Crie o ambiente virtual
    ```
    pyvenv /caminho/para/o/ambiente/virtual

    ```    
    E depois entre no diretório
     ```
     cd  /caminho/para/o/ambiente/virtual

     ```
6. Clone o repositório do projeto do github
    ```
    git clone https://github.com/culturagovbr/sistema-nacional-cultura.git snc

    ```

7. Ative o ambiente virtual
    ```
    source /caminho/para/o/ambiente/virtual/bin/activate

    ```
    E depois entre no diretório do projeto
     ```
     cd  /caminho/para/o/ambiente/virtual/snc/

     ```

8. Instale as dependências python do projeto
    ```
    pip3 install -r requirements.txt
    sudo apt-get install python3-dev
    ```
    OBS: Caso a dependência ```django-smart-selects==1.1.1``` dê erro, utilize
     ```

     pip3 install https://pypi.python.org/packages/source/d/django-smart-selects/django-smart-selects-1.1.1.tar.gz

     ```
     E novamente
     ```
     pip3 install -r requirements.txt
    ```
9. Instale a biblioteca drf-hal-json
    1. Clone o repositório [drf-hal-json](https://github.com/Artory/drf-hal-json)
    2. Entre no diretório do repositório clonado
     ```
     cd  drf-hal-json/

     ```
    3. Copie a pasta drf_hal_json/ para o core de packages do python do ambiente virtual
    ```
     cp -r drf_hal_json/ /caminho/para/o/ambiente/virtual/lib/python3.5/site-packages

     ```
10. Configure o arquivo settings.py e altere o caminho para ele no ``` manage.py``` e no ```wsgi.py``` usando a  linha abaixo:
```
  os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snc.config.settings.local")
```

11. Configure o banco de dados
Crie o banco dbsnc no seu serviço de acordo com o settings.py.
```
sudo -u postgres psql
CREATE DATABASE dbsnc;
\q
```

12. Execute os comandos de criação do banco

Criação de migração para cada APP
```
python3 manage.py makemigrations planotrabalho
python3 manage.py makemigrations gestao
python3 manage.py makemigrations adesao
```
Comando migrate para criar a estrutura do banco (DDL)
```
python3 manage.py migrate
```

Exclua as tabelas de controle do DJANGO geradas automaticamente

```
delete from auth_permission;
delete from django_content_type;
```

Comando de importação da base atual
OBS:o arquivo dump.json não é fornecido e deverá ser criado a partir dos registros existentes no banco de dados, caso
```
python3 manage.py loaddata dump.json
```
Obs.: caso seu dump não possua as mesmas colunas do código atual, adicione -i no loaddata

13. Copie os arquivos estaticos do projeto
```
python3 manage.py collectstatic
```

14. Execute a aplicação (É preciso ter o ambiente virtual ativado)
    ```
    python3 manage.py runserver

    ```
