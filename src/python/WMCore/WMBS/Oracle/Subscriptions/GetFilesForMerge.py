#!/usr/bin/env python
"""
_GetFilesForMerge_

Oracle implementation of Subscription.GetFilesForMerge
"""

__all__ = []
__revision__ = "$Id: GetFilesForMerge.py,v 1.1 2009/03/09 18:37:00 sfoulkes Exp $"
__version__ = "$Revision: 1.1 $"

from WMCore.WMBS.MySQL.Subscriptions.GetFilesForMerge import GetFilesForMerge as GetFilesForMergeMySQL

class GetFilesForMerge(GetFilesForMergeMySQL):
    """
    This query only differs from the MySQL version in the names of columns:
      file -> fileid
      size -> filesize

    See the MySQL version of this object for a narrative on this query.
    """
    sql = """SELECT wmbs_file_details.id AS file_id,
                    wmbs_file_details.events AS file_events,
                    wmbs_file_details.filesize AS file_size,
                    wmbs_file_details.lfn AS file_lfn,
                    wmbs_file_details.first_event AS file_first_event,
                    wmbs_file_runlumi_map.run AS file_run,
                    wmbs_file_runlumi_map.lumi AS file_lumi,
                    wmbs_jobgroup.id AS group_id
             FROM wmbs_file_details
             INNER JOIN wmbs_file_runlumi_map
               ON wmbs_file_details.id = wmbs_file_runlumi_map.fileid
             INNER JOIN wmbs_fileset_files
               ON wmbs_file_details.id = wmbs_fileset_files.fileid
             INNER JOIN wmbs_jobgroup
               ON wmbs_fileset_files.fileset = wmbs_jobgroup.output
             WHERE wmbs_file_details.id IN
               (SELECT fileid FROM wmbs_fileset_files INNER JOIN wmbs_subscription
                  ON wmbs_fileset_files.fileset = wmbs_subscription.fileset
                WHERE wmbs_subscription.id = :p_1)
               AND wmbs_jobgroup.id IN
                 (SELECT jobgroup FROM
                   (SELECT jobgroup, count(*) AS total_jobs FROM wmbs_job GROUP BY jobgroup) all_jobs
                     INNER JOIN
                       (SELECT jobgroup, count(*) AS complete_jobs FROM wmbs_group_job_complete GROUP BY jobgroup) complete_jobs
                       USING (jobgroup) WHERE total_jobs = complete_jobs)
               AND NOT EXISTS
                 (SELECT * FROM wmbs_sub_files_acquired WHERE
                   wmbs_file_details.id = wmbs_sub_files_acquired.fileid AND
                   :p_1 = wmbs_sub_files_acquired.subscription)
               AND NOT EXISTS
                 (SELECT * FROM wmbs_sub_files_complete WHERE
                   wmbs_file_details.id = wmbs_sub_files_complete.fileid AND
                   :p_1 = wmbs_sub_files_complete.subscription)
               AND NOT EXISTS
                 (SELECT * FROM wmbs_sub_files_failed WHERE
                   wmbs_file_details.id = wmbs_sub_files_failed.fileid AND
                   :p_1 = wmbs_sub_files_failed.subscription)
             """
