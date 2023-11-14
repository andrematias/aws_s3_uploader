import logging
import logging.config
from datetime import datetime

import settings

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


def is_time_between(begin_time, end_time, check_time=None):
    """
    Verifica se esta entre um intervalo de horas
    :param begin_time objeto time
    :param end_time objeto time
    """
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    return check_time >= begin_time or check_time <= end_time


def in_work_time(start, end):
    """
    Verifica se esta entre um intervalo de horas definidos no
    arquivo de configuração
    """
    try:
        start = datetime.strptime(start, "%H:%M:%S").time()
        end = datetime.strptime(end, "%H:%M:%S").time()
        return is_time_between(start, end, check_time=datetime.now().time())
    except ValueError:
        logger.error(
            "Formato de hora informado com um formato inválido. Tente H:m:s (00:00:00)"
        )
        return False
