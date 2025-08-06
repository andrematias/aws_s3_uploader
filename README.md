# Script para upload de arquivos de gravações para AWS S3 ou Oralce S3

## Ordem da execução

1. Le a arvore de arquivos em um diretório informado
   1.1. Verifica o tamanho do arquivo. Maiores que 1G não entram no processo
2. Inclui os arquivos em uma estrutura de fila
3. Realiza o upload dos arquivos assincronamente
4. Registra nos logs de info e error

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
