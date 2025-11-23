# Checkout com Upsell (Django)

Este projeto demonstra um fluxo simples de checkout com oferta de upsell e downsell usando Django.

## Passos iniciais
1. Criar e ativar um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Instalar dependências (é necessário acesso à internet para baixar o Django):
   ```bash
   pip install -r requirements.txt
   ```
3. Criar o banco de dados e tabelas:
   ```bash
   python manage.py migrate
   ```
4. Executar o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

Acesse `http://localhost:8000/checkout/` para visualizar o fluxo de checkout.

## Observação
Caso o ambiente não permita baixar pacotes da internet, a instalação do Django poderá falhar. Nesse caso, adicione manualmente o pacote ao ambiente ou configure o proxy corretamente.
