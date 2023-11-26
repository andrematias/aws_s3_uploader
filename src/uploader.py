"""
Módulo responsável pelo upload de arquivos para um bucket s3 AWS
"""

import itertools
import logging
import logging.config
import os
import sys
import threading
import time
from contextlib import suppress
from queue import Queue

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
    while True:
        with suppress(FileNotFoundError):
            files_generators = storage.find_pattern(
                settings.STORAGE_ROOT, settings.FILES_PATERNS
            )
            for file in itertools.chain(*files_generators):
                q.put(file)
                while q.qsize() > (q.maxsize - settings.TOTAL_WORKERS):
                    time.sleep(5)
        logger.info(
            "Storage vazio, aguardando %d minutos para coletar novos arquivos...",
            settings.WATCH_SECONDS / 60,
        )
        time.sleep(settings.WATCH_SECONDS)


def upload_to_s3(s3, file):
    """
    Executa a rotina de upload das gravações para a AWS S3
    :param s3 uma instancia de S3
    :param file um arquivo PosixPath, WindowsPath
    """
    bucket_path = str(file.parent).split(os.sep)
    bucket_path = os.sep.join(bucket_path[2:])
    object_name = os.path.join(bucket_path, file.name)

    if not file.exists():
        return

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


def consumer(s3, q):
    """
    Consome a fila criada com os arquivos encontrado no storage
    :param queue Uma fila asyncio
    """
    try:
        while True:
            file = q.get()
            if file is None:
                break
            logger.info("Uploading: %s", file.name)
            upload_to_s3(s3, file)
            q.task_done()
    except Exception as e:
        logger.error(e)


def main():
    """
    Executa o produtor e consumidor
    """
    if in_work_time(settings.START_TIME, settings.END_TIME):
        logger.info("Iniciando o processo de upload")
        q = Queue(settings.MAX_QUEUE_SIZE)

        s3 = S3()
        if not s3.token_is_valid():
            logger.warning("Sessão AWS expirada")
            sys.exit()

        for i in range(settings.TOTAL_WORKERS):
            t = threading.Thread(target=consumer, name=f"Worker {i}", args=(s3, q))
            t.daemon = True
            t.start()

        try:
            producer(q)
        except (SystemExit, KeyboardInterrupt):
            logger.info("Parando o producer")
            sys.exit()
        q.join()
        logger.info("Storage finalizado")

    else:
        logger.info("Fora do período de trabalho")


if __name__ == "__main__":
    try:
        main()
    except (SystemExit, KeyboardInterrupt):
        logger.info("Parando o uploader")
