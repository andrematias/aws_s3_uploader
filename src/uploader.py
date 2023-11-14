import asyncio
import logging
import logging.config
import os

from botocore.exceptions import ClientError

import settings
import storage
from s3 import S3

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


async def producer(queue):
    """
    Adiciona os arquivos na fila de processamento
    :param queue Uma fila asyncio
    """
    files = storage.find_pattern(settings.STORAGE_ROOT, settings.FILES_PATERNS)
    if len(files) == 0:
        logger.info(
            "Nenhum arquivo com o padrão '%s' encontrado no caminho '%s'",
            settings.FILES_PATERNS,
            settings.STORAGE_ROOT,
        )
        await queue.put(None)

    for file in files:
        file_stats = file.stat()
        if file_stats.st_size <= settings.MAX_FILE_SIZE:
            await queue.put(file)
    await queue.put(None)


async def consumer(queue):
    """
    Executa a rotina de upload das gravações para a AWS S3
    :param queue Uma fila asyncio
    """
    try:
        s3 = S3()
        while True:
            file = await queue.get()
            if file is None:
                break

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
                storage.purge_empty_dir(file.parent)
    except ClientError as e:
        logger.error(e)


async def main():
    """
    Executa o produtor e consumidor
    """
    logger.info("Iniciando o processo de upload")
    queue = asyncio.Queue(settings.MAX_QUEUE_SIZE)
    await asyncio.gather(producer(queue), consumer(queue))


if __name__ == "__main__":
    asyncio.run(main())
