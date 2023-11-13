import logging
import logging.config
import os

from botocore.exceptions import ClientError

import settings
import storage
from s3 import S3

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def main():
    """
    Executa a rotina de upload das gravações para a AWS S3
    """
    logger.info("Iniciando o processo de upload")

    try:
        s3 = S3()
        files = storage.find_pattern(settings.STORAGE_ROOT, settings.FILES_PATERNS)
        for file in files:
            bucket_path = str(file.parent).split(os.sep)
            bucket_path = os.sep.join(bucket_path[2:])
            object_name = os.path.join(bucket_path, file.name)

            s3.upload_file(file, settings.S3_BUCKET, object_name)
            if settings.DOUBLE_CHECK_UPLOAD and s3.check_file(object_name):
                logger.info(
                    "Arquivo '%s' confirmado no bucket '%s'",
                    object_name,
                    settings.S3_BUCKET,
                )
    except ClientError as e:
        logger.error(e)


if __name__ == "__main__":
    main()
