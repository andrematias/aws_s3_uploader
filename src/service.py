import multiprocessing
import os
import os.path
import sys

import servicemanager
import win32service
import win32serviceutil

from uploader import runner


class ProcessService(win32serviceutil.ServiceFramework):
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
        self.proc = multiprocessing.Process(target=runner)
        self.proc.start()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.SvcDoRun()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

    def SvcDoRun(self):
        self.proc.join()


def start():
    if len(sys.argv) == 1:
        import win32traceutil

        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ProcessService)
        servicemanager.StartServiceCtrlDispatcher()
    elif "--fg" in sys.argv:
        runner()
    else:
        win32serviceutil.HandleCommandLine(ProcessService)


if __name__ == "__main__":
    try:
        start()
    except (SystemExit, KeyboardInterrupt):
        raise
    except:
        import traceback

        traceback.print_exc()
