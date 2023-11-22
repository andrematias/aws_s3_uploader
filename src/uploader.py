import asyncio
import itertools
import logging
import logging.config
import os
import time

from botocore.exceptions import ClientError

import settings
import storage
from s3 import S3, S3AcyncIo
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


async def io_upload_to_s3(s3, file):
    """
    Executa a rotina de upload assincrono das gravações para a AWS S3
    :param s3 uma instancia de S3
    :param file um arquivo PosixPath, WindowsPath
    """
    bucket_path = str(file.parent).split(os.sep)
    bucket_path = os.sep.join(bucket_path[2:])
    object_name = os.path.join(bucket_path, file.name)

    file_stats = file.stat()
    if file_stats.st_size <= settings.MAX_FILE_SIZE:
        await s3.upload_file(
            file, settings.S3_BUCKET, object_name, force=settings.FORCE_UPLOAD
        )

        if settings.DOUBLE_CHECK_UPLOAD:
            file_exists = await s3.check_file(object_name)
            if file_exists:
                logger.info(
                    "Arquivo '%s' confirmado no bucket '%s'",
                    object_name,
                    settings.S3_BUCKET,
                )
            else:
                logger.info(
                    "Arquivo '%s' não encontrado no bucket '%s'",
                    object_name,
                    settings.S3_BUCKET,
                )

        if not settings.DEBUG:
            await asyncio.to_thread(storage.remove_file, file)
            await asyncio.to_thread(storage.purge_empty_dir, file.parent)


def upload_to_s3(s3, file):
    """
    Executa a rotina de upload das gravações para a AWS S3
    :param s3 uma instancia de S3
    :param file um arquivo PosixPath, WindowsPath
    """
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


async def consumer(queue):
    """
    Consome a fila criada com os arquivos encontrado no storage
    :param queue Uma fila asyncio
    """
    try:
        if settings.USE_AIOBOTO:
            s3 = S3AcyncIo()
        else:
            s3 = S3()
        while True:
            file = await queue.get()
            if file is None:
                break
            if settings.USE_AIOBOTO:
                await io_upload_to_s3(s3, file)
            else:
                await asyncio.to_thread(upload_to_s3, s3, file)
    except ClientError as e:
        logger.error(e)


async def main():
    """
    Executa o produtor e consumidor
    """
    logger.info("Iniciando o processo de upload")
    queue = asyncio.Queue(settings.MAX_QUEUE_SIZE)

    consumer_tasks = [
        asyncio.create_task(consumer(queue)) for _ in range(1, settings.TOTAL_WORKERS)
    ]
    await asyncio.gather(producer(queue), *consumer_tasks)


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
    try:
        watch()
    except (SystemExit, KeyboardInterrupt):
        logger.info("Parando o uploader")
