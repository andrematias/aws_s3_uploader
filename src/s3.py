import logging
import logging.config
import os
import sys
import threading

import aioboto3
import boto3
from botocore.exceptions import ClientError

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


class ExpiredTokenException(Exception):
    def __init__(self):
        super().__init__(
            "Token da sessão expirado. Por favor, gerar outro via console aws!"
        )


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


class S3:
    """
    Realiza os processos de upload e relacionados ao AWS s3
    """

    def __init__(self):
        self.__client = boto3.client("s3")

    def upload_file(self, file_name, bucket, object_name=None, force=False):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        if object_name is None:
            object_name = os.path.basename(file_name)
        object_name = object_name.replace("\\", "/")
        try:
            if not self.check_file(object_name) or force:
                self.__client.upload_file(
                    file_name,
                    bucket,
                    object_name,
                    Callback=ProgressPercentage(file_name),
                )
                return True

        except ClientError as e:
            if "ExpiredToken" in str(e):
                raise ExpiredTokenException() from e
        logger.info("Arquivo '%s' já existe no bucket", object_name)
        return False

    def check_file(self, object_name):
        """
        Verifica se existe um arquivo com o nome informado no s3
        :param object_name Nome do arquivo salvo no bucket
        """
        try:
            response = self.__client.list_objects(
                Bucket=settings.S3_BUCKET, MaxKeys=1, Prefix=object_name
            )
            return response.get("Contents") is not None
        except ClientError as e:
            if "ExpiredToken" in str(e):
                raise ExpiredTokenException() from e
            return False

    def token_is_valid(self):
        """
        Faz uma requisição simples para testar a sessão
        """
        try:
            self.check_file("unkown")
            return True
        except ExpiredTokenException:
            return False


class S3AcyncIo:
    """
    Realiza os processos de upload asyncrono e relacionados ao AWS s3
    """

    def __init__(self) -> None:
        self._session = aioboto3.Session()

    async def upload_file(self, file, bucket, object_name=None, force=False):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        async with self._session.client("s3") as s3:
            try:
                checked_file = await self.check_file(object_name)
                if not checked_file or force:
                    with file.open("rb") as spfp:
                        logger.info("Uploading %s to s3", object_name)
                        await s3.upload_fileobj(
                            spfp,
                            bucket,
                            object_name,
                            Callback=ProgressPercentage(file),
                        )
                        return True
            except ClientError as e:
                if "ExpiredToken" in str(e):
                    logger.warning(
                        "Token da sessão expirado. Por favor, gerar outro via console aws!"
                    )
                    sys.exit()
                logger.error(e)
            except Exception as e:
                logger.error("Unable to s3 upload %s: %s (%s)", object_name, e, type(e))
                sys.exit()
            logger.info("Arquivo '%s' já existe no bucket", object_name)
            return False

    async def check_file(self, object_name):
        """
        Verifica se existe um arquivo com o nome informado no s3
        :param object_name Nome do arquivo salvo no bucket
        """
        try:
            async with self._session.client("s3") as s3:
                response = await s3.get_object(
                    Bucket=settings.S3_BUCKET, Key=object_name
                )
                return (
                    response.get("ResponseMetadata", {}).get("HTTPStatusCode", 404)
                    == 200
                )
        except ClientError as e:
            if "ExpiredToken" in str(e):
                logger.warning(
                    "Token da sessão expirado. Por favor, gerar outro via console aws!"
                )
                sys.exit()
            return False
        except Exception as e:
            logger.error(
                "Unable to check if file exists %s: %s (%s)", object_name, e, type(e)
            )
        return False
