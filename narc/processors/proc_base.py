import os

class ProcBase:
    def task_started(self, task):
        # pylint: disable=unused-argument
        pass

    def task_completed(self, task, aresult):
        # pylint: disable=unused-argument,no-self-use
        try:
            os.mkdir("outputs")
        except FileExistsError:
            pass

    def task_instance_started(self, task, host):
        # pylint: disable=unused-argument
        pass

    def task_instance_completed(self, task, host, mresult):
        # pylint: disable=unused-argument
        pass

    def subtask_instance_started(self, task, host):
        # pylint: disable=unused-argument
        pass

    def subtask_instance_completed(self, task, host, mresult):
        # pylint: disable=unused-argument
        pass
