# Script para upload de arquivos de gravações para AWS S3

## Ordem da execução

1. Le a arvore de arquivos em um diretório informado
   1.1. Verifica o tamanho do arquivo. Maiores que 1G não entram no processo
2. Inclui os arquivos em uma estrutura de fila
3. Realiza o upload dos arquivos assincronamente
4. Registra nos logs de info e error
