#!/usr/bin/env python
"""
_DeleteCheckFile_

MySQL implementation of DeleteCheckFile

"""

from WMCore.Database.DBFormatter import DBFormatter

class DeleteCheck(DBFormatter):
    """
    _DeleteCheck_

    This DAO defines how files are deleted in a fileset, this is meant to be
    used only by the TaskArchiver when cleaning up workflows from WMBS. The
    process is as follows:
    - A list of files from a fileset is received. The assumption is that the
      children filesets in the same workflow has already been deleted.
    - We filter the files by selecting only those that are not in any other
      fileset and are not parents of any other file. Since we assume that
      children filesets have been deleted then this condition will hold
      as long as the file is not parent of a file in another workflow.
    - Parent files for the files to be deleted are identified and the parentage
      relation is deleted.
    - Now the filtered files are deleted.
    - Finally, the parent files are deleted if they are not parents of any other
      file and are not part of any other fileset.
    """

    sqlCheck = """SELECT id FROM wmbs_file_details
                   WHERE id = :id AND
                   NOT EXISTS (SELECT fileset FROM wmbs_fileset_files WHERE fileid = :id
                               AND fileset != :fileset) AND
                   NOT EXISTS (SELECT parent FROM wmbs_file_parent WHERE parent = :id)
                   """
    sqlParents = """SELECT parent AS parentid from wmbs_file_parent WHERE child = :id"""

    sqlDeleteParentship = """DELETE FROM wmbs_file_parent WHERE child = :id"""

    sql = """DELETE FROM wmbs_file_details WHERE id = :id"""

    sqlDeleteParents = """DELETE FROM wmbs_file_details WHERE id = :parentid AND
                          NOT EXISTS (SELECT parent FROM wmbs_file_parent WHERE parent = :parentid) AND
                          NOT EXISTS (SELECT fileset FROM wmbs_fileset_files WHERE fileid = :parentid)"""


    def execute(self, file = None,
                fileset = None, conn = None, transaction = False):
        if type(file) == list:
            if len(file) < 1:
                return
            binds = []
            for entry in file:
                binds.append({'id': entry, 'fileset': fileset})
        else:
            binds = {'id': file, 'fileset': fileset}

        filteredList = self.formatDict(self.dbi.processData(self.sqlCheck, binds,
                                                            conn = conn,
                                                            transaction = transaction))
        if len(filteredList) > 0:
            candidateParents = self.formatDict(self.dbi.processData(self.sqlParents,
                                                                    filteredList,
                                                                    conn = conn,
                                                                    transaction = transaction))
            self.dbi.processData(self.sqlDeleteParentship, filteredList,
                                 conn = conn, transaction = transaction)

            self.dbi.processData(self.sql, filteredList,
                                 conn = conn, transaction = transaction)
            if len(candidateParents) > 0:
                self.dbi.processData(self.sqlDeleteParents, candidateParents,
                                     conn = conn, transaction = transaction)

        return True
