# Checkout com Upsell (Django)

Este projeto demonstra um fluxo simples de checkout com oferta de upsell e downsell usando Django.

## Passos iniciais
1. Criar e ativar um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Verificar se o Django já está disponível (a imagem base geralmente traz a versão 5.2.8):
   ```bash
   python - <<'PY'
import django
print(django.get_version())
PY
   ```
   Se já houver saída com a versão, você pode pular a instalação. Caso contrário, tente instalar as dependências:
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
Caso o ambiente não permita baixar pacotes da internet, a instalação do Django poderá falhar. Nesse caso, utilize o Django que já vem instalado na imagem (verifique com o comando do passo 2) ou adicione os pacotes manualmente ao ambiente.

## Instalação do Django em ambientes restritos
Se o acesso direto ao PyPI estiver bloqueado, use o script auxiliar que tenta múltiplas rotas e aceita wheels locais como fallback (para Django e Pillow, necessário pelo `ImageField`):

```bash
./scripts/install_django.sh  # tenta múltiplas URLs e depois vendor/Django-*.whl e vendor/Pillow-*.whl
```

Etapas cobertas pelo script:
- Verifica se Django já está instalado e encerra cedo se estiver presente.
- PyPI via HTTPS com as configurações padrão de certificado.
- PyPI via HTTP para contornar inspeção TLS.
- Mirror da Tsinghua para uma alternativa de repositório.
- Instalação a partir de wheels locais em `vendor/` (por exemplo, transfira `Django-5.2.8-py3-none-any.whl` e `Pillow-11.1.0-*.whl` para lá).
- Tentativa via `apt-get install python3-django python3-pil` para ambientes onde os repositórios de sistema estejam liberados.

O script retorna falha somente após todas as tentativas. Ajuste a variável de versão passada como argumento (ou a variável de ambiente `PILLOW_VERSION`), caso precise de um release específico.

### Sem acesso à internet
1. Baixe os wheels de Django e Pillow em uma máquina com internet:
   ```bash
   pip download --only-binary=:all: --python-version 312 --implementation cp --abi cp312 --platform manylinux2014_x86_64 django==5.2.8 pillow==11.1.0 -d wheelhouse
   ```
2. Copie os arquivos gerados para a pasta `vendor/` do projeto.
3. Execute o script de instalação para usar os wheels locais:
   ```bash
   ./scripts/install_django.sh
   ```

### Baixar somente o Pillow
Se o Django já estiver disponível mas apenas o Pillow estiver faltando, você pode tentar baixar o wheel diretamente para a pasta `vendor/` com o script dedicado:

```bash
./scripts/download_pillow.sh        # tenta PyPI (https/http), mirror da Tsinghua e depois uma URL direta opcional
PILLOW_WHEEL_URL="https://exemplo.com/Pillow-11.1.0-cp312-cp312-manylinux_2_28_x86_64.whl" ./scripts/download_pillow.sh
```

Caso o ambiente esteja totalmente offline, baixe o wheel em outra máquina (ex.: via `pip download pillow==11.1.0 -d vendor`) e copie o arquivo resultante para `vendor/`. O instalador reconhecerá automaticamente qualquer `Pillow-*.whl` já presente nessa pasta.

#### Comando direto (copiar/colar) via `pip download`
Se preferir rodar o comando manualmente no terminal, use este passo a passo (ajuste `--index-url` se necessário):

```bash
# Baixar o wheel do Pillow para a pasta vendor/ sem dependências
mkdir -p vendor
python -m pip download --only-binary=:all: --no-deps --dest vendor \
  --index-url https://pypi.org/simple --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  pillow==11.1.0

# Instalar a partir do wheel recém-baixado
python -m pip install vendor/Pillow-11.1.0-*.whl
```

Se o proxy bloquear HTTPS, tente forçar HTTP (nem todo mirror aceita):

```bash
python -m pip download --only-binary=:all: --no-deps --dest vendor \
  --index-url http://pypi.org/simple --trusted-host pypi.org \
  pillow==11.1.0
```
