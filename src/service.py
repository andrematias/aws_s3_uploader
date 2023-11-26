import logging
import logging.config
import multiprocessing
import os
import os.path
import sys
import traceback

import servicemanager
import win32service
import win32serviceutil

import settings
from uploader import main

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("extensive")


class ProcessService(win32serviceutil.ServiceFramework):
    """
    Cria um serviço no Windows
    """

    _svc_name_ = "S3Uploader"
    _svc_display_name_ = "AWS S3 Uploader"
    _svc_description_ = (
        "Realiza o upload de arquivos no diretório informado para o serviço AWS S3"
    )
    _exe_name_ = sys.executable
    _exe_args_ = '-u -E "' + os.path.abspath(__file__) + '"'

    proc = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.proc:
            self.proc.terminate()

    def SvcRun(self):
        self.proc = multiprocessing.Process(target=main)
        self.proc.start()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.SvcDoRun()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

    def SvcDoRun(self):
        if self.proc:
            self.proc.join()


def start():
    """
    Inicia o serviço em foreground, instala, remove, start, stop
    """
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ProcessService)
        servicemanager.StartServiceCtrlDispatcher()
    elif "--fg" in sys.argv:
        main()
    else:
        win32serviceutil.HandleCommandLine(ProcessService)


if __name__ == "__main__":
    try:
        start()
    except (SystemExit, KeyboardInterrupt):
        logger.info("Parando o serviço")
    except Exception as e:
        logger.info(e)
        if settings.DEBUG:
            traceback.print_exc()
