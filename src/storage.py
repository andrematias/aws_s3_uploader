import logging
import logging.config
import os
import shutil
from contextlib import suppress
from pathlib import Path

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def recursive_dir(dir_path):
    """
    Recupera em uma lista com o caminho dos arquivos
    :param dir_path Um diretório raiz
    """
    logger.info("Buscando arquivos recursivamente na raiz: %s", dir_path)
    root = Path(dir_path)
    if root.exists():
        return root.rglob("*")
    return []


def find_pattern(dir_path, pattern):
    """
    Procura um arquivo em um diretório
    :param dir_path: Diretorio raiz
    :param pattern: Padrão com o nome do arquivo
    """
    path = Path(dir_path)
    if path.resolve():
        patterns = pattern.split(",")
        for p in patterns:
            yield path.rglob(p)


def remove_tree(root):
    """
    Remove a arvore de diretórios e arquivos a partir da raiz
    :param root Um diretório raiz
    """
    if root != settings.STORAGE_ROOT:
        logger.info("Remove a raiz: %s", root)
        shutil.rmtree(root, ignore_errors=True)


def purge_empty_dir(root):
    """
    Remove diretórios vazios a partir da raiz
    :param root Um diretório raiz
    """
    logger.info("Apagando diretórios vazios na raiz: %s", root)
    for directory, _, _ in os.walk(root):
        with suppress(OSError):
            if directory != settings.STORAGE_ROOT:
                os.removedirs(directory)


def remove_file(filepath):
    """
    Remove o arquivo informado
    :param filename Caminho para o arquivo
    """
    with suppress(FileNotFoundError):
        p = Path(filepath)
        if p.resolve():
            logger.info("Apagando o arquivo local: %s", filepath)
            p.unlink()
