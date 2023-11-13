DOUBLE_CHECK_UPLOAD = False
STORAGE_ROOT = "../storage/"
FILES_PATERNS = "*.txt,*.mp3,*.wav"
S3_BUCKET = "gravacoesmutant-prd"
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
