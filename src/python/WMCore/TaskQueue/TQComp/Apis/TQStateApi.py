#!/usr/bin/env python
"""
API to query the TQ queue about its state.

It inherits the ability to connect to the TQ database 
from TQComp.Apis.TQApi.
"""

__all__ = []
__revision__ = "$Id: TQStateApi.py,v 1.3 2009/06/01 09:57:08 delgadop Exp $"
__version__ = "$Revision: 1.3 $"

#import logging
import threading
import time

from TQComp.Apis.TQApi import TQApi
from TQComp.Apis.TQApiData import TASK_FIELDS, PILOT_FIELDS


class TQStateApi(TQApi):
    """
    API to query the TQ queue about its state.
    """

    def __init__(self, logger, tqRef, dbIface = None):
        """
        Constructor. Refer to the constructor of parent TQApi.
        """
        # Call our parent to set everything up
        TQApi.__init__(self, logger, tqRef, dbIface)


    def getTasks(self, filter={}, fields=[], limit=None, asDict=False):
        """
        Returns the filtered contents of the tasks DB.
        
        The filter argument can be used to select the type of tasks to 
        retrieve. It must be a dict containing fields as keys and the values
        they should have. If any of the keys does not correspond to an 
        existing field, it will be ignored.

        The optional argument fields may contain a list of fields to return.
        Otherwise, all are returned. The optional argument limit can be used
        to limit the maximum number of records returned.

        If the optional argument 'asDict' is True, the result is a dict with
        field names as keys; otherwise, the result is a list of field values.
        """
        
#        self.logger.debug('%s: Starting' % ('getTasks'))
        
        return self.__getTable__(filter, fields, limit, asDict, 'tq_tasks', \
                     TASK_FIELDS, 'getTasks', self.queries.getTasksWithFilter)



    def getPilots(self, filter={}, fields=[], limit=None, asDict=False):
        """
        Returns the filtered contents of the pilots DB.
        
        The filter argument can be used to select the type of pilots to 
        retrieve. It must be a dict containing fields as keys and the values
        they should have. If any of the keys does not correspond to an 
        existing field, it will be ignored.

        The optional argument fields may contain a list of fields to return.
        Otherwise, all are returned. The optional argument limit can be used
        to limit the maximum number of records returned.

        If the optional argument 'asDict' is True, the result is a dict with
        field names as keys; otherwise, the result is a list of field values.
        """

#        self.logger.debug('%s: Starting' % ('getPilots'))
        
        return self.__getTable__(filter, fields, limit, asDict, 'tq_pilots', \
                  PILOT_FIELDS, 'getPilots', self.queries.getPilotsWithFilter)


    def __getTable__(self, filter, fields, limit, asDict, table, fList, \
                     caller, method):
        """
        Internal. For use of getTasks and getPilots.
        """
        
#        self.logger.debug('%s: Starting' % ('__getTable__'))
        filter2 = {}
        for key in filter.keys():
            if key in fList:
                filter2[key] = filter[key]
                
        fields2 = []
        for field in fields:
            if field in fList:
                fields2.append(field)
               
        if filter and (not filter2):
            self.logger.error('%s: Filter keys not valid: %s' % (caller, filter))
            self.logger.error('%s: Refusing to dump all entries' % (caller))
            return None
            
        if fields and (not fields2):
            self.logger.error('%s: No valid field requested: %s' % (caller, fields))
            self.logger.error('%s: Aborting query' % (caller))
            return None
           
        if len(filter2) < len(filter):
            self.logger.warning('%s: Not all filter keys valid: %s' % \
                            (caller, filter))
            self.logger.warning('%s: Using filter: %s' % (caller, filter2))
        else:
            self.logger.debug('%s: Using filter: %s' % (caller, filter2))

        if len(fields2) < len(fields):
            self.logger.warning('%s: Not all fields valid: %s' % (caller, fields))
            self.logger.warning('%s: Requesting fields: %s' % (caller, fields2))
        else:
            self.logger.debug('%s: Requesting fields: %s' % (caller, fields2))

        # Perform query
#        self.transaction.begin()
        result = method(filter2, fields2, limit, asDict)
        return result
#        self.transaction.commit()


    def getDataPerHost(self, hostPattern = "%"):
        """
        Returns a dict with pairs (se, host) as keys and list of 
        files (names) as values. Only hosts matching the provided 
        pattern are returned (all by default).
        """
        res = self.queries.getDataPerHost(hostPattern)

#        self.logger.debug("res: %s" % res)
        d = {}
        prev = ""
        for row in res:
            if (row[0], row[1]) == prev:
                d[(row[0], row[1])].append(row[2])
            else:
                d[(row[0], row[1])] = [row[2]]
            prev = (row[0], row[1])

        return d
        
    def getPilotsPerHost(self, hostPattern = "%"):
        """
        Returns a dict with pairs (se, host) as keys and list of pilots 
        (ids) as values. Only hosts matching the provided pattern are 
        returned (all by default).
        """
        res = self.queries.getPilotsPerHost(hostPattern)

#        self.logger.debug("res: %s" % res)
        d = {}
        prev = ""
        for row in res:
            if (row[0], row[1]) == prev:
                d[(row[0], row[1])].append(row[2])
            else:
                d[(row[0], row[1])] = [row[2]]
            prev = (row[0], row[1])

        return d
        



    def getPilotsAtHost(self, host, se, asDict=False):
        """ 
        Returns the pilots that are present in a given host (and se)
        and the cache directory for each of them.

        If the optional argument 'asDict' is True, the result is returned as 
        a list with field names as keys; otherwise, result is a list of field
        values.
        """
#        self.transaction.begin()
        return self.queries.getPilotsAtHost(host, se, asDict)
#        self.transaction.commit()


    def countRunning(self):
        """
        Returns the number of tasks in the Running state
        """
        self.logger.debug('Getting number of running tasks')

        # Perform query
#        self.transaction.begin()
        result = self.queries.countRunning()
        return result
#        self.transaction.commit()


    def countQueued(self):
        """
        Returns the number of tasks in the Queued state
        """
        self.logger.debug('Getting number of queued tasks')

        # Perform query
#        self.transaction.begin()
        result = self.queries.countQueued()
        return result
#        self.transaction.commit()
