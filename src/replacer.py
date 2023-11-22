import asyncio
import logging
import logging.config
import sys

import boto3
from botocore.exceptions import ClientError

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


async def put_in_queue(queue, obj):
    """
    Coloca os itens na fila
    """
    original_key = obj.key
    new_key = original_key.replace("\\", "/")
    await queue.put({"from": original_key, "to": new_key})


async def producer(prefix, queue, resource):
    """
    Preenche a fila com os itens do bucket
    """
    bucket = resource.Bucket(settings.S3_BUCKET)
    objs = bucket.objects.filter(Prefix=prefix)
    for obj in objs:
        await put_in_queue(queue, obj)
    await queue.put(None)


def move(client, bucket, item):
    """
    Copia e remove o arquivo no bucket
    """
    bucket.copy({"Bucket": settings.S3_BUCKET, "Key": item["from"]}, item["to"])
    logger.info("File %s copied to %s", item["from"], item["to"])

    delete_response = client.delete_object(
        Bucket=settings.S3_BUCKET,
        Key=item["from"],
    )
    logger.info(
        "Arquivo %s deletado: %s",
        item["from"],
        delete_response.get("ResponseMetadata", {}).get("HTTPStatusCode", 400),
    )


async def consumer(queue, client, resource):
    """
    Consome os itens da fila
    """
    try:
        bucket = resource.Bucket(settings.S3_BUCKET)
        while True:
            item = await queue.get()
            if item is None:
                sys.exit()
            await asyncio.to_thread(move, client, bucket, item)
    except ClientError as e:
        if "ExpiredToken" in str(e):
            logger.warning(
                "Token da sessão expirado. Por favor, gerar outro via console aws!"
            )
            sys.exit()
        logger.error(e)


def replace():
    """
    Renomeia arquivos com as barras contrarias na chave para
    coloca-las na estrutura de diretórios
    """
    try:
        client = boto3.client("s3")
        resource = boto3.resource("s3")
        bucket = resource.Bucket(settings.S3_BUCKET)
        response = client.list_objects(
            Bucket=settings.S3_BUCKET, MaxKeys=1000, Prefix="2022\\"
        )
        contents = response.get("Contents", [])
        for content in contents:
            original_key = content.get("Key")
            new_key = original_key.replace("\\", "/")
            bucket.copy({"Bucket": settings.S3_BUCKET, "Key": original_key}, new_key)
            logger.info("File %s copied to %s", original_key, new_key)

            delete_response = client.delete_object(
                Bucket=settings.S3_BUCKET,
                Key=original_key,
            )
            logger.info(
                "Arquivo %s deletado: %s",
                original_key,
                delete_response.get("ResponseMetadata", {}).get("HTTPStatusCode", 400),
            )
    except ClientError as e:
        if "ExpiredToken" in str(e):
            logger.warning(
                "Token da sessão expirado. Por favor, gerar outro via console aws!"
            )
            sys.exit()
        logger.error(e)


async def main():
    """
    Executa a rotina
    """
    queue = asyncio.Queue(maxsize=1000)
    client = boto3.client("s3")
    resource = boto3.resource("s3")
    tasks = [
        asyncio.create_task(consumer(queue, client, resource)) for _ in range(0, 10)
    ]
    await asyncio.gather(
        producer("2022\\", queue, resource), *tasks, return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (SystemExit, KeyboardInterrupt):
        logger.info("Parando o replacer")
