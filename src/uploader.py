import logging
import logging.config

import settings
from s3 import upload_file

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def main():
    """
    Executa a rotina de upload das gravações para a AWS S3
    """
    logger.info("Iniciando o processo de upload")
    upload_file(
        "../file_to_upload.txt", settings.S3_BUCKET, object_name="descartar/file.txt"
    )


if __name__ == "__main__":
    main()
