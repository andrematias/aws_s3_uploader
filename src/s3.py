import logging
import logging.config
import os
import sys
import threading

import boto3
from botocore.exceptions import ClientError

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


class ProgressPercentage:
    """
    Esta classe é utilizada como callback para
    acompanhar o progresso de upload do arquivo
    """

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            logger.info(
                "%s  %s / %s  (%.2f%%)",
                self._filename,
                self._seen_so_far,
                self._size,
                percentage,
            )
            sys.stdout.flush()


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(
            file_name, bucket, object_name, Callback=ProgressPercentage(file_name)
        )
    except ClientError as e:
        logger.error(e)
        return False
    return True
