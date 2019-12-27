#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: An abstract base class for other processors.
"""

import os


class ProcBase:
    """
    Represents an abstract processor object. Serves as a parent
    class for concrete processors to handle different output styles.
    Defines stub methods to reduce copy/paste burden on children.
    """

    def task_started(self, task):
        """
        Runs when a task begins.
        """
        pass

    def task_completed(self, task, aresult):
        """
        Runs when a task ends and provides access to the final
        AggregatedResult.
        """
        # pylint: disable=unused-argument,no-self-use
        try:
            os.mkdir("outputs")
        except FileExistsError:
            pass

    def task_instance_started(self, task, host):
        """
        Runs when an individual host begins running a task.
        """
        pass

    def task_instance_completed(self, task, host, mresult):
        """
        Runs when an individual host finishes running a task and
        provides access to the host-specific MultiResult.
        """
        pass

    def subtask_instance_started(self, task, host):
        """
        Runs when subtasks start running for a given host.
        """
        pass

    def subtask_instance_completed(self, task, host, mresult):
        """
        Runs when subtasks finish running for a given host and
        provides access to the host-specific MultiResult.
        """
        pass
