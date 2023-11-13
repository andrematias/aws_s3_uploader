import logging
import logging.config

import settings
from s3 import S3

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def main():
    """
    Executa a rotina de upload das gravações para a AWS S3
    """
    logger.info("Iniciando o processo de upload")
    s3 = S3()
    object_name = "descartar/file.txt"

    s3.upload_file("../file_to_upload.txt", settings.S3_BUCKET, object_name)
    if s3.check_file("descartar/file.txt"):
        logger.info(
            "Arquivo '%s' confirmado no bucket '%s'", object_name, settings.S3_BUCKET
        )


if __name__ == "__main__":
    main()
