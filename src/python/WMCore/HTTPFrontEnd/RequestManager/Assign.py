#!/usr/bin/env python
""" Main Module for browsing and modifying requests """
import WMCore.RequestManager.RequestDB.Interface.Admin.ProdManagement as ProdManagement
import WMCore.RequestManager.RequestDB.Interface.Request.ChangeState as ChangeState
import WMCore.RequestManager.RequestDB.Interface.Request.GetRequest as GetRequest
from WMCore.HTTPFrontEnd.RequestManager.ReqMgrWebTools import parseSite, saveWorkload, loadWorkload, changePriority, requestsWithStatus, sites, prepareForTable
import WMCore.Lexicon
import logging
import cherrypy
import threading
import types

#from WMCore.WebTools.Page import TemplatedPage
from WMCore.WebTools.WebAPI import WebAPI

class Assign(WebAPI):
    """ Used by data ops to assign requests to processing sites"""
    def __init__(self, config):
        WebAPI.__init__(self, config)
        # Take a guess
        self.templatedir = config.templates
        self.couchUrl = config.couchUrl
        self.configDBName = config.configDBName
        self.sites = sites(config.sitedb)
        self.allMergedLFNBases =  [
            "/store/backfill/1", "/store/backfill/2", 
            "/store/data",  "/store/mc"]
        self.mergedLFNBases = {
             "ReReco" : ["/store/backfill/1", "/store/backfill/2", "/store/data"],
             "MonteCarlo" : ["/store/backfill/1", "/store/backfill/2", "/store/mc"],
             "RelValMC" : ["/store/backfill/1", "/store/backfill/2", "/store/mc"]}             
        self.yuiroot = config.yuiroot
        cherrypy.engine.subscribe('start_thread', self.initThread)

    def initThread(self, thread_index):
        """ The ReqMgr expects the DBI to be contained in the Thread  """
        myThread = threading.currentThread()
        #myThread = cherrypy.thread_data
        # Get it from the DBFormatter superclass
        myThread.dbi = self.dbi

    def validate(self, v, name=''):
        """ Checks if alphanumeric, tolerating spaces """
        try:
            WMCore.Lexicon.identifier(v)
        except AssertionError:
            raise cherrypy.HTTPError(400, "Bad input %s" % name)
        return v

    @cherrypy.expose
    def one(self,  requestName):
        """ Assign a single request """
        self.validate(requestName)
        request =  GetRequest.getRequestByName(requestName)
        request = prepareForTable(request)
        requestType = request["RequestType"]
        # get assignments
        teams = ProdManagement.listTeams()
        assignments = GetRequest.getAssignmentsByName(requestName)
        # might be a list, or a dict team:priority
        if isinstance(assignments, dict):
            assignments = assignments.keys()
        return self.templatepage("Assign", requests=[request], teams=teams, 
                 assignments=assignments, sites=self.sites, mergedLFNBases = self.mergedLFNBases[requestType])

    @cherrypy.expose    
    def index(self):
        """ Main page """
        # returns dict of  name:id
        requests = requestsWithStatus('assignment-approved')
        teams = ProdManagement.listTeams()
        return self.templatepage("Assign", requests=requests, teams=teams,
                 assignments=[], sites=self.sites, mergedLFNBases = self.allMergedLFNBases)

    @cherrypy.expose
    def handleAssignmentPage(self, **kwargs):
        """ handler for the main page """
        # handle the checkboxes
        teams = []
        requests = []
        for key, value in kwargs.iteritems():
            if isinstance(value, types.StringTypes):
                kwargs[key] = value.strip()
            if key.startswith("Team"):
                teams.append(key[4:])
            if key.startswith("checkbox"):
                requestName = key[8:]
                self.validate(requestName)
                requests.append(key[8:])
        
        for requestName in requests:
            if kwargs['action'] == 'Reject':
                ChangeState.changeRequestStatus(requestName, 'rejected') 
            else:
                assignments = GetRequest.getAssignmentsByName(requestName)
                if teams == [] and assignments == []:
                    raise cherrypy.HTTPError(400, "Must assign to one or more teams")
                self.assignWorkload(requestName, kwargs)
                for team in teams:
                    if not team in assignments:
                        ChangeState.assignRequest(requestName, team)
                priority = kwargs.get(requestName+':priority', '')
                if priority != '':
                    changePriority(requestName, priority)
        return self.templatepage("Acknowledge", participle=kwargs['action']+'ed', requests=requests)

    def assignWorkload(self, requestName, kwargs):
        """ Make all the necessary changes in the Workload to reflect the new assignment """
        request = GetRequest.getRequestByName(requestName)
        helper = loadWorkload(request)
        for field in ["AcquisitionEra", "ProcessingVersion"]:
            self.validate(kwargs[field], field)
        helper.setSiteWhitelist(parseSite(kwargs,"SiteWhitelist"))
        helper.setSiteBlacklist(parseSite(kwargs,"SiteBlacklist"))
        helper.setProcessingVersion(kwargs["ProcessingVersion"])
        helper.setAcquisitionEra(kwargs["AcquisitionEra"])
        #FIXME not validated
        helper.setLFNBase(kwargs["MergedLFNBase"], kwargs["UnmergedLFNBase"])
        helper.setMergeParameters(int(kwargs["MinMergeSize"]), int(kwargs["MaxMergeSize"]), int(kwargs["MaxMergeEvents"]))
        saveWorkload(helper, request['RequestWorkflow'])
 
