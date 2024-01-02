"""
Módulo para remover silencio de arquivos de áudio
ffmpeg -i caminho/para/com_silence.mp3 \
    -af silenceremove=stop_periods=-1\
    :stop_duration=1\
    :stop_threshold=-30dB \
    camiho/para/sem_silenciao.mp3
"""
import logging
import logging.config
import subprocess
from os import path

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


class ExecutorException(Exception):
    pass


def run_local_command(cmd):
    try:
        logger.debug("Executing local command: %s", cmd)
        ret = subprocess.run(cmd, shell=True, check=False, capture_output=True)
        if ret.stderr:
            return ret.stderr.decode(errors="ignore")
        return ret.stdout.decode(errors="ignore")
    except FileNotFoundError as fex:
        raise ExecutorException("Cancelling command execution %s" % fex)


def ffmpeg_command(origin, output, decibels=-30, periods=1):
    bin_path = settings.FFMPEG_BIN
    if not path.exists(bin_path):
        logger.error("FFMPEG binary not found in '%s'", bin_path)
        return False
    try:
        logger.info("Removendo silencio do arquivo: %s", origin)
        stop_periods = f"stop_periods=-{periods}"
        stop_duration = f"stop_duration={periods}"
        stop_threshold = f"stop_threshold={decibels}dB"
        ffmpeg_args = "-y -i {} -af silenceremove={}:{}:{} {}"
        ffmpeg_args = ffmpeg_args.format(
            origin, stop_periods, stop_duration, stop_threshold, output
        )
        command = f"{bin_path} {ffmpeg_args}"
        logger.debug("Executing cmd: '%s'", command)
        ffmpeg_output = run_local_command(command)
        logger.debug(
            "Remove silcence from file '%s'. Output: %s", origin, ffmpeg_output
        )
        return True
    except ExecutorException as exc:
        logger.error("Fail to run command to remove silences")
        logger.exception(exc)
        return False


def remove_silence(filename, output, decibels=-30):
    if not path.exists(filename):
        logger.warning("File not found: '%s'", filename)
        return False
    return ffmpeg_command(filename, output, decibels=decibels)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="FFMPEG Silence Ripper",
        description="Remove silences from record audio",
    )
    parser.add_argument("filename", help="Original filename")
    parser.add_argument("output", help="The output filename")
    parser.add_argument("-d", "--decibels", default=-30, help="Decibels")
    args = parser.parse_args()
    remove_silence(args.filename, args.output, decibels=args.decibels)
