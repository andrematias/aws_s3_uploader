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
        if len(files) == 0:
            logger.info(
                "Nenhum arquivo com o padrão '%s' encontrado no caminho '%s'",
                settings.FILES_PATERNS,
                settings.STORAGE_ROOT,
            )
            return

        for file in files:
            bucket_path = str(file.parent).split(os.sep)
            bucket_path = os.sep.join(bucket_path[2:])
            object_name = os.path.join(bucket_path, file.name)

            file_stats = file.stat()
            if file_stats.st_size <= settings.MAX_FILE_SIZE:
                s3.upload_file(
                    file, settings.S3_BUCKET, object_name, force=settings.FORCE_UPLOAD
                )

                if settings.DOUBLE_CHECK_UPLOAD and s3.check_file(object_name):
                    logger.info(
                        "Arquivo '%s' confirmado no bucket '%s'",
                        object_name,
                        settings.S3_BUCKET,
                    )
                storage.remove_file(file)
    except ClientError as e:
        logger.error(e)


if __name__ == "__main__":
    main()
