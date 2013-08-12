#!/usr/bin/env python
"""
_GetAndMarkNewFinishedSubscriptions_

MySQL implementation of Subscriptions.GetAndMarkNewFinishedSubscriptions
"""

import time

from WMCore.Database.DBFormatter import DBFormatter

class GetAndMarkNewFinishedSubscriptions(DBFormatter):
    """
    _GetAndMarkNewFinishedSubscriptions_

    Searches for all subscriptions where the fileset is closed,
    the workflow is injected, there are no available files,
    no acquired files, no jobs that are not in state 'cleanout'.
    It marks such subscriptions as finished.
    """
    sql = """UPDATE wmbs_subscription
             SET wmbs_subscription.finished = 1, wmbs_subscription.last_update = :timestamp
             WHERE wmbs_subscription.id IN (
                     SELECT complete_subscription.id FROM (
                        SELECT wmbs_subscription.id
                        FROM wmbs_subscription
                        INNER JOIN wmbs_fileset ON
                            wmbs_fileset.id = wmbs_subscription.fileset
                        INNER JOIN wmbs_workflow ON
                            wmbs_workflow.id = wmbs_subscription.workflow
                        LEFT OUTER JOIN wmbs_sub_files_available ON
                            wmbs_sub_files_available.subscription = wmbs_subscription.id
                        LEFT OUTER JOIN wmbs_sub_files_acquired ON
                            wmbs_sub_files_acquired.subscription = wmbs_subscription.id
                        LEFT OUTER JOIN wmbs_jobgroup ON
                            wmbs_jobgroup.subscription = wmbs_subscription.id
                        LEFT OUTER JOIN wmbs_job ON
                            wmbs_job.jobgroup = wmbs_jobgroup.id AND
                            wmbs_job.state != %d
                        WHERE wmbs_subscription.finished = 0 AND
                              wmbs_fileset.open = 0 AND
                              wmbs_workflow.injected = 1
                        GROUP BY wmbs_subscription.id
                        HAVING COUNT(wmbs_sub_files_available.subscription) = 0 AND
                               COUNT(wmbs_sub_files_acquired.subscription) = 0 AND
                               COUNT(wmbs_job.id) = 0 ) complete_subscription)
             """

    def execute(self, state, conn = None, transaction = False):

        currentTime = int(time.time())
        binds = {'timestamp' : currentTime}

        self.dbi.processData(self.sql % state,
                             binds, conn = conn,
                             transaction = transaction)

        return
