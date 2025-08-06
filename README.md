# Script para upload de arquivos de gravações para AWS S3 ou Oralce S3

## Ordem da execução

1. Le a arvore de arquivos em um diretório informado
   1.1. Verifica o tamanho do arquivo. Maiores que 1G não entram no processo
2. Inclui os arquivos em uma estrutura de fila
3. Realiza o upload dos arquivos assincronamente
4. Registra nos logs de info e error

## Dependencias

- [Python3](https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe)

## Instalação de dependências

Abra um terminal, CMD ou Powershell e execute o comando abaixo:

```powershell
python3 -m pip install -r requirements.txt

```

## Configuração do uploader

Modifique os valores no arquivo `src/settings.py`

```python
# Chaves de acesso ao S3
ACCESS_KEY_ID = ""
SECRET_ACCESS_KEY = ""

# Para compatibilidade com Oracle OCI
OCI_COMPATIBLE = True
OCI_NAMESPACE = ""
OCI_REGION = ""

# Nome do bucket no s3
S3_BUCKET = ""

# Origem dos arquivos locais
STORAGE_ROOT = "D:\Record\\"

# Local dos logs
INFO_LOGGER_FILE = f"D:\\info.{today.day}.log"
ERROR_LOGGER_FILE = "D:\\error.log"

```

## Manuseio do serviço

### Instalação

python service.py install

### Start:

python service.py start

### Instalar com autostart:

python service.py --startup delayed install

### Debug:

python service.py debug

### Stop:

python service.py stop

### Remover:

python service.py remove

## Referencias

- [Oracle compatible url](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/s3compatibleapi.htm)
- [Boto3 Lib](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
