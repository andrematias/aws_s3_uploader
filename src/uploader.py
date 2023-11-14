import asyncio
import itertools
import logging
import logging.config
import os
import time

from botocore.exceptions import ClientError

import settings
import storage
from s3 import S3
from scheduler import in_work_time

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


async def producer(queue):
    """
    Adiciona os arquivos na fila de processamento
    :param queue Uma fila asyncio
    """
    files_generators = storage.find_pattern(
        settings.STORAGE_ROOT, settings.FILES_PATERNS
    )
    for file in itertools.chain(*files_generators):
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
                if not settings.DEBUG:
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


def runner():
    """
    Executa a rotina dentro do horario estabelecido
    """
    if in_work_time(settings.START_TIME, settings.END_TIME):
        asyncio.run(main())
    else:
        logger.debug("Fora do período de trabalho")


def watch():
    """
    Realiza uma execução do uploader a cada 60 segundos
    """
    while True:
        runner()
        time.sleep(settings.WATCH_SECONDS)


if __name__ == "__main__":
    watch()
