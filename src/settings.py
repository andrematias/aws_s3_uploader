"""
Define o tempo em que um novo processo de upload se inicia
"""
WATCH_SECONDS = 60 * 60  # 1h

"""
Define se o script esta em modo debug, caso True os arquivos não serão removidos após o  upload
"""
DEBUG = False

"""
Define se usará a biblioteca boto3 não oficial ou oficial
"""
USE_AIOBOTO = True

"""
Define o horario de inicio e fim que o script pode ser executado
"""
START_TIME = "09:00:00"
END_TIME = "23:59:59"

"""
True para verificar após o upload se existe o arquivo no bucket
"""
DOUBLE_CHECK_UPLOAD = False

"""
Define a raiz do storage de gravações
"""
STORAGE_ROOT = "../storage/"

"""
Define as extensões para upload
"""
FILES_PATERNS = "*.txt,*.mp3,*.wav"

"""
Define o tamanho maximo do arquivo, caso maiores serão desconsiderados
"""
MAX_FILE_SIZE = 1024 * 100000  # 100 Mb

"""
Define se o upload acontece mesmo se já existir o arquivo
"""
FORCE_UPLOAD = False

"""
Define o nome do bucket s3
"""
S3_BUCKET = "gravacoesmutant-prd"

"""
Define o tamanho do lote que será incluso na fila de upload
"""
MAX_QUEUE_SIZE = 100

"""
Define a quantidade de tarefas assincronas consumirá a fila
"""
TOTAL_WORKERS = 10

"""
Configura o logger
"""
INFO_LOGGER_FILE = "../logs/info.log"
ERROR_LOGGER_FILE = "../logs/error.log"
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
        "info_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": INFO_LOGGER_FILE,
            "mode": "a",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": INFO_LOGGER_FILE,
            "mode": "a",
            "maxBytes": 10485760,
            "backupCount": 5,
        },
    },
    "formatters": {
        "detailed": {
            "format": "%(asctime)s %(module)-17s line:%(lineno)-4d "
            "%(levelname)-8s %(message)s",
        },
    },
    "loggers": {
        "extensive": {
            "level": "DEBUG",
            "handlers": [
                "console",
                "info_file",
                "error_file",
            ],
        },
    },
}
