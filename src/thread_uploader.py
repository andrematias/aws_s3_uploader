import itertools
import logging
import logging.config
import os
import threading
import time
from queue import Queue

from botocore.exceptions import ClientError

import settings
import storage
from s3 import S3
from scheduler import in_work_time

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def producer(q: Queue):
    """
    Adiciona os arquivos na fila de processamento
    :param queue Uma fila
    """

    files_generators = storage.find_pattern(
        settings.STORAGE_ROOT, settings.FILES_PATERNS
    )
    for file in itertools.chain(*files_generators):
        q.put_nowait(file)
        while q.qsize() > (q.maxsize - settings.TOTAL_WORKERS):
            time.sleep(5)


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


def consumer(q):
    """
    Consome a fila criada com os arquivos encontrado no storage
    :param queue Uma fila asyncio
    """
    try:
        s3 = S3()
        while True:
            file = q.get()
            if file is None:
                break
            logger.info("Uploading: %s", file.name)
            upload_to_s3(s3, file)
            q.task_done()
    except ClientError as e:
        logger.error(e)


def main():
    """
    Executa o produtor e consumidor
    """
    if in_work_time(settings.START_TIME, settings.END_TIME):
        logger.info("Iniciando o processo de upload")
        q = Queue(settings.MAX_QUEUE_SIZE)

        for i in range(settings.TOTAL_WORKERS):
            t = threading.Thread(target=consumer, name=f"Worker {i}", args=(q,))
            t.daemon = True
            t.start()

        producer(q)
        q.join()
        logger.info("Storage finalizado")

    else:
        logger.debug("Fora do período de trabalho")


def watch():
    """
    Realiza uma execução do uploader a cada WATCH_SECONDS
    """
    while True:
        main()
        time.sleep(settings.WATCH_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        logger.info("Parando o uploader")
