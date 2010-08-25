#!/usr/bin/python
#pylint: disable-msg=E1103

"""
_Create_

Class for creating SQLite specific schema for persistent messages.

"""

__revision__ = ""
__version__ = ""
__author__ = "mnorman@fnal.gov"

import logging
import threading

from WMCore.Database.DBCreator import DBCreator

class Create(DBCreator):
    """
    _Create_
    
    Class for creating SQLite specific schema for persistent messages.
    """
    
    
    
    def __init__(self):
        myThread = threading.currentThread()
        DBCreator.__init__(self, myThread.logger, myThread.dbi)
        self.create = {}
        self.constraints = {}
        msg = """
A ms_type table stores information on message types.

Fields:

 typeid   id
 name     message name
        """
        logging.debug(msg)
#Lines disabled because sql claims that AUTOCOMMIT is enabled by default
# and doesn't give a good way to disable it
#        self.create['taa'] = """      
#SET AUTOCOMMIT = 0; """
        #self.create['taa'] = """      """
        self.create['00ta_ms_type'] = """      CREATE TABLE ms_type
        (
             typeid INTEGER PRIMARY KEY,
             name varchar(255) NOT NULL default '',
             UNIQUE (name)
        )
"""
        msg =  """ 
A ms_process table stores information on components.
                                                                                
Fields:
                                                                                
procid   id
name     component name
host     host name
pid      process id in host name 
"""
        logging.debug(msg)
        self.create['01tb_ms_process'] = """
CREATE TABLE ms_process (
   procid INTEGER PRIMARY KEY,
   name varchar(255) NOT NULL default '',
   host varchar(255) NOT NULL default '',
   pid int(11) NOT NULL default '0',
   UNIQUE (name)
   ) 
"""
        
        msg = """
A ms_history table stores information on the complete message history.
                                                                                
Fields:
                                                                                
 messageid   id
 type        message type id
 source      source component id
 dest        target component id
 payload     message payload
 time        time stamp
"""
        logging.debug(msg)
        self.create['02tc_ms_history'] = """
CREATE TABLE ms_history (
    messageid INTEGER PRIMARY KEY,
    type int(11) NOT NULL default '0',
    source int(11) NOT NULL default '0',
    dest int(11) NOT NULL default '0',
    payload text NOT NULL,
    time timestamp NOT NULL default CURRENT_TIMESTAMP,
    delay varchar(50) NOT NULL default '00:00:00',

    FOREIGN KEY(type) references ms_type(typeid),
    FOREIGN KEY(source) references ms_process(procid),
    FOREIGN KEY(dest) references ms_process(procid)
    ) 
"""

        
        self.create['03tca_ms_history_buffer'] = """
CREATE TABLE ms_history_buffer (
    messageid int(11) PRIMARY KEY NOT NULL,
    type int(11) NOT NULL default '0',
    source int(11) NOT NULL default '0',
    dest int(11) NOT NULL default '0',
    payload text NOT NULL,
    time timestamp NOT NULL default CURRENT_TIMESTAMP ,
    delay varchar(50) NOT NULL default '00:00:00',

    FOREIGN KEY(type) references ms_type(typeid),
    FOREIGN KEY(source) references ms_process(procid),
    FOREIGN KEY(dest) references ms_process(procid)
    ) 
"""
        self.create['04td_ms_history_priority'] = """
CREATE TABLE ms_history_priority (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

    FOREIGN KEY(type) references ms_type(typeid),
    FOREIGN KEY(source) references ms_process(procid),
    FOREIGN KEY(dest) references ms_process(procid)
    ) 
"""
        self.create['05tda_ms_history_priority_buffer'] = """
CREATE TABLE ms_history_priority_buffer (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

    FOREIGN KEY(type) references ms_type(typeid),
    FOREIGN KEY(source) references ms_process(procid),
    FOREIGN KEY(dest) references ms_process(procid)
    ) 
"""
        
        msg = """
A ms_message table stores information on the messages to be delivered.
                                                                                
Fields:
                                                                                
 messageid   id
 type        message type id
 source      source component id
 dest        target component id
 payload     message payload
 time        time stamp
"""
        logging.debug(msg)
        self.create['06te_ms_message'] = """
CREATE TABLE ms_message (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
   ) 
"""
        msg = """
ms_message_buffer_in: an input buffer for the message queue
to prevent inserting messages one, by one in the message queu.
"""
        logging.debug(msg)
        self.create['07tf_ms_message_buffer_in'] = """
CREATE TABLE ms_message_buffer_in (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
   ) 
   """
       
        msg = """
ms_message_buffer_out: an output buffer for the message queue
to prevent removing message one by one, out of a potential large queue.
"""
        logging.debug(msg)
        #Done because SQLite doesn't support ENUM
        self.create['08tg_ms_message_buffer_out_enum'] = """
CREATE TABLE ms_message_buffer_out_enum (
        value varchar(20)       PRIMARY KEY  NOT NULL
        )"""

        self.create['08tg_ms_message_buffer_out_enum_insert1'] = """
INSERT INTO ms_message_buffer_out_enum VALUES('wait')
"""
        
        self.create['08tg_ms_message_buffer_out_enum_insert2'] = """
INSERT INTO ms_message_buffer_out_enum VALUES('processing')
"""

        self.create['08tg_ms_message_buffer_out_enum_insert3'] = """
INSERT INTO ms_message_buffer_out_enum VALUES('finished')
"""
        
        self.create['09tg_ms_message_buffer_out'] = """ 
CREATE TABLE ms_message_buffer_out (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',
   state varchar(20) NOT NULL default 'wait',

   FOREIGN KEY(state) references ms_message_buffer_out_enum(value),
   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
)  
"""
        msg = """
ms_priority_message: a table for priority messages.
The message service will first examine this table before
looking at the other messages.
"""
        logging.debug(msg)
        self.create['10th_ms_priorty_message'] = """
CREATE TABLE ms_priority_message (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
   ) 
"""
        self.create['11ti_ms_priority_message_buffer_in'] = """
CREATE TABLE ms_priority_message_buffer_in (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',

   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
   ) 
"""
        self.create['12tj_ms_priority_message_buffer_out'] = """
CREATE TABLE ms_priority_message_buffer_out (
   messageid int(11) PRIMARY KEY NOT NULL,
   type int(11) NOT NULL default '0',
   source int(11) NOT NULL default '0',
   dest int(11) NOT NULL default '0',
   payload text NOT NULL,
   time timestamp NOT NULL default CURRENT_TIMESTAMP ,
   delay varchar(50) NOT NULL default '00:00:00',
   state varchar(20) NOT NULL default 'wait',

   FOREIGN KEY(state) references ms_message_buffer_out_enum(value),
   FOREIGN KEY(type) references ms_type(typeid),
   FOREIGN KEY(source) references ms_process(procid),
   FOREIGN KEY(dest) references ms_process(procid)
   ) 
"""
        msg = """

A ms_subscription table stores information on the message subscriptions.
                                                                                
Fields:

 subid   id
 procid  component id
 typeid  message type id
"""
        logging.debug(msg)
        self.create['13tk_ms_subscription'] = """
CREATE TABLE ms_subscription (
   subid INTEGER PRIMARY KEY,
   procid int(11) NOT NULL default '0',
   typeid int(11) NOT NULL default '0',
   UNIQUE (procid,typeid),
   FOREIGN KEY(procid) references ms_process(procid),
   FOREIGN KEY(typeid) references ms_type(typeid)
   ) 
"""
        self.create['14tl_ms_subscription_priority'] = """
CREATE TABLE ms_subscription_priority (
   subid INTEGER PRIMARY KEY,
   procid int(11) NOT NULL default '0',
   typeid int(11) NOT NULL default '0',
   UNIQUE (procid,typeid),
   FOREIGN KEY(procid) references ms_process(procid),
   FOREIGN KEY(typeid) references ms_type(typeid)
   ) 
"""
        self.create['15tm_ms__available'] = """
CREATE TABLE ms_available (
  procid int(11) NOT NULL,
  status varchar(20) NOT NULL default 'not_there',	
  UNIQUE (procid),
  FOREIGN KEY(procid) references ms_process(procid),
  FOREIGN KEY(status) references ms_there_notthere_enum(value)
   ) 
"""
        self.create['15tm_ms__available_enum'] = """
CREATE TABLE ms_there_notthere_enum (
        value varchar(20)       PRIMARY KEY  NOT NULL
        )"""

        self.create['15tm_ms__available_enum_insert1'] = """
INSERT INTO ms_there_notthere_enum VALUES('there')
"""
        
        self.create['15tm_ms__available_enum_insert2'] = """
INSERT INTO ms_there_notthere_enum VALUES('not_there')
"""

        
        self.create['16tn_ms_available_priority'] = """
CREATE TABLE ms_available_priority (
  procid int(11) NOT NULL,
  status varchar(20) NOT NULL default 'not_there',	
  UNIQUE (procid),
  FOREIGN KEY(procid) references ms_process(procid),
  FOREIGN KEY(status) references ms_there_notthere_enum(value)
   ) 
"""

        self.create['17to_ms_checkbuffer_enum'] = """
CREATE TABLE ms_checking_notchecking_enum (
        value varchar(20)       PRIMARY KEY  NOT NULL
        )"""

        self.create['17to_ms_checkbuffer_enum_insert1'] = """
INSERT INTO ms_checking_notchecking_enum VALUES('checking')
"""
        
        self.create['17to_ms_checkbuffer_enum_insert2'] = """
INSERT INTO ms_checking_notchecking_enum VALUES('not_checking')
"""
        
        self.create['17to_ms_checkbuffer'] = """
CREATE TABLE ms_check_buffer (
  buffer varchar(100) NOT NULL,
  status varchar(20) NOT NULL default 'not_checking',
  FOREIGN KEY(status) references ms_checking_notchecking_enum(value),
   UNIQUE (buffer)
   ) 
"""





#It's trigger time!
#SQLite doesn't appear to support the "on update CURRENT_TIMESTAMP" value for time
#Also doesn't enforce FOREIGN KEY constraints.
#Also doesn't support ENUM
#Have to do triggers for all of them



        self.create["20TR_tc_ms_history"]="""
CREATE TRIGGER TR_tc_ms_history BEFORE UPDATE ON ms_history
       FOR EACH ROW
             BEGIN
                  UPDATE ms_history SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""

        self.create['20TR_tc_ms_history_type'] = """
CREATE TRIGGER TR_ms_history_type BEFORE INSERT ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['20TR_tc_ms_history_source'] = """
CREATE TRIGGER TR_ms_history_source BEFORE INSERT ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['20TR_tc_ms_history_dest'] = """
CREATE TRIGGER TR_ms_history_dest BEFORE INSERT ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['20TR_tc_ms_history_typeu'] = """
CREATE TRIGGER TR_ms_history_typeu BEFORE UPDATE ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['20TR_tc_ms_history_sourceu'] = """
CREATE TRIGGER TR_ms_history_sourceu BEFORE UPDATE ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['20TR_tc_ms_history_destu'] = """
CREATE TRIGGER TR_ms_history_destu BEFORE UPDATE ON ms_history
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        

        #ms_history_buffer

        self.create["21TR_tca_ms_history_buffer"]="""
CREATE TRIGGER TR_tca_ms_history_buffer BEFORE UPDATE ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                  UPDATE ms_history_buffer SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['21TR_tca_ms_history_buffer_type'] = """
CREATE TRIGGER TR_ms_history_buffer_type BEFORE INSERT ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['21TR_tca_ms_history_buffer_source'] = """
CREATE TRIGGER TR_ms_history_buffer_source BEFORE INSERT ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_buffer has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['21TR_tca_ms_history_buffer_dest'] = """
CREATE TRIGGER TR_ms_history_buffer_dest BEFORE INSERT ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_buffer has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        self.create['21TR_tca_ms_history_buffer_typeu'] = """
CREATE TRIGGER TR_ms_history_buffer_typeu BEFORE UPDATE ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['21TR_tca_ms_history_buffer_sourceu'] = """
CREATE TRIGGER TR_ms_history_buffer_sourceu BEFORE UPDATE ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_buffer has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['21TR_tca_ms_history_buffer_destu'] = """
CREATE TRIGGER TR_ms_history_buffer_destu BEFORE UPDATE ON ms_history_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_buffer has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        

        #ms_history_priority

        self.create["22TR_td_ms_history_priority"]="""
CREATE TRIGGER TR_td_ms_history_priority BEFORE UPDATE ON ms_history_priority
       FOR EACH ROW
             BEGIN
                  UPDATE ms_history_priority SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""

        self.create['22TR_td_ms_history_priority_type'] = """
CREATE TRIGGER TR_ms_history_priority_type BEFORE INSERT ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['22TR_td_ms_history_priority_source'] = """
CREATE TRIGGER TR_ms_history_priority_source BEFORE INSERT ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['22TR_td_ms_history_priority_dest'] = """
CREATE TRIGGER TR_ms_history_priority_dest BEFORE INSERT ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        self.create['22TR_td_ms_history_priority_typeu'] = """
CREATE TRIGGER TR_ms_history_priority_typeu BEFORE UPDATE ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['22TR_td_ms_history_priority_sourceu'] = """
CREATE TRIGGER TR_ms_history_priority_sourceu BEFORE UPDATE ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['22TR_td_ms_history_priority_destu'] = """
CREATE TRIGGER TR_ms_history_priority_destu BEFORE UPDATE ON ms_history_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        
        

        #ms_history_priority_buffer

        self.create["23TR_tda_ms_history_priority_buffer"]="""
CREATE TRIGGER TR_tda_ms_history_priority_buffer BEFORE UPDATE ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                  UPDATE ms_history_priority_buffer SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['23TR_tda_ms_history_priority_buffer_type'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_type BEFORE INSERT ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['23TR_tda_ms_history_priority_buffer_source'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_source BEFORE INSERT ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['23TR_tda_ms_history_priority_buffer_dest'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_dest BEFORE INSERT ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        self.create['23TR_tda_ms_history_priority_buffer_typeu'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_typeu BEFORE UPDATE ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['23TR_tda_ms_history_priority_buffer_sourceu'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_sourceu BEFORE UPDATE ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['23TR_tda_ms_history_priority_buffer_destu'] = """
CREATE TRIGGER TR_ms_history_priority_buffer_destu BEFORE UPDATE ON ms_history_priority_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_history_priority_buffer has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""




        #ms_message

        self.create["24TR_te_ms_message"]="""
CREATE TRIGGER TR_te_ms_message BEFORE UPDATE ON ms_message
       FOR EACH ROW
             BEGIN
                  UPDATE ms_message SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['24TR_te_ms_message_type'] = """
CREATE TRIGGER TR_ms_message_type BEFORE INSERT ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['24TR_te_ms_message_source'] = """
CREATE TRIGGER TR_ms_message_source BEFORE INSERT ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['24TR_te_ms_message_dest'] = """
CREATE TRIGGER TR_ms_message_dest BEFORE INSERT ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        self.create['24TR_te_ms_message_typeu'] = """
CREATE TRIGGER TR_ms_message_typeu BEFORE UPDATE ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['24TR_te_ms_message_sourceu'] = """
CREATE TRIGGER TR_ms_message_sourceu BEFORE UPDATE ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['24TR_te_ms_message_destu'] = """
CREATE TRIGGER TR_ms_message_destu BEFORE UPDATE ON ms_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        




        #ms_message_buffer_in

        self.create["25TR_tf_ms_message_buffer_in"]="""
CREATE TRIGGER TR_tf_ms_message_buffer_in BEFORE UPDATE ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                  UPDATE ms_message_buffer_in SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['25TR_tf_ms_message_buffer_in_type'] = """
CREATE TRIGGER TR_ms_message_buffer_in_type BEFORE INSERT ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['25TR_tf_ms_message_buffer_in_source'] = """
CREATE TRIGGER TR_ms_message_buffer_in_source BEFORE INSERT ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['25TR_tf_ms_message_buffer_in_dest'] = """
CREATE TRIGGER TR_ms_message_buffer_in_dest BEFORE INSERT ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        self.create['25TR_tf_ms_message_buffer_in_typeu'] = """
CREATE TRIGGER TR_ms_message_buffer_in_typeu BEFORE UPDATE ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['25TR_tf_ms_message_buffer_in_sourceu'] = """
CREATE TRIGGER TR_ms_message_buffer_in_sourceu BEFORE UPDATE ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['25TR_tf_ms_message_buffer_in_destu'] = """
CREATE TRIGGER TR_ms_message_buffer_in_destu BEFORE UPDATE ON ms_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_in has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""
        



        
        #ms_message_buffer_out

        self.create["26TR_tg_ms_message_buffer_out"]="""
CREATE TRIGGER TR_tg_ms_message_buffer_out BEFORE UPDATE ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                  UPDATE ms_message_buffer_out SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['26TR_tg_ms_message_buffer_out_type'] = """
CREATE TRIGGER TR_ms_message_buffer_out_type BEFORE INSERT ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['26TR_tg_ms_message_buffer_out_source'] = """
CREATE TRIGGER TR_ms_message_buffer_out_source BEFORE INSERT ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['26TR_tg_ms_message_buffer_out_dest'] = """
CREATE TRIGGER TR_ms_message_buffer_out_dest BEFORE INSERT ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['26TR_tg_ms_message_buffer_out_typeu'] = """
CREATE TRIGGER TR_ms_message_buffer_out_typeu BEFORE UPDATE ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['26TR_tg_ms_message_buffer_out_sourceu'] = """
CREATE TRIGGER TR_ms_message_buffer_out_sourceu BEFORE UPDATE ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['26TR_tg_ms_message_buffer_out_destu'] = """
CREATE TRIGGER TR_ms_message_buffer_out_destu BEFORE UPDATE ON ms_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_message_buffer_out has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""




        
        #ms_priority_message

        self.create["28TR_th_ms_priority_message"]="""
CREATE TRIGGER TR_th_ms_priority_message BEFORE UPDATE ON ms_priority_message
       FOR EACH ROW
             BEGIN
                  UPDATE ms_priority_message SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['28TR_th_ms_priority_message_type'] = """
CREATE TRIGGER TR_ms_priority_message_type BEFORE INSERT ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['28TR_th_ms_priority_message_source'] = """
CREATE TRIGGER TR_ms_priority_message_source BEFORE INSERT ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['28TR_th_ms_priority_message_dest'] = """
CREATE TRIGGER TR_ms_priority_message_dest BEFORE INSERT ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['28TR_th_ms_priority_message_typeu'] = """
CREATE TRIGGER TR_ms_priority_message_typeu BEFORE UPDATE ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['28TR_th_ms_priority_message_sourceu'] = """
CREATE TRIGGER TR_ms_priority_message_sourceu BEFORE UPDATE ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['28TR_th_ms_priority_message_destu'] = """
CREATE TRIGGER TR_ms_priority_message_destu BEFORE UPDATE ON ms_priority_message
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""


        



        #ms_priority_message_buffer_in

        self.create["29TR_ti_ms_priority_message_buffer_in"]="""
CREATE TRIGGER TR_ti_ms_priority_message_buffer_in BEFORE UPDATE ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                  UPDATE ms_priority_message_buffer_in SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['29TR_ti_ms_priority_message_buffer_in_type'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_type BEFORE INSERT ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['29TR_ti_ms_priority_message_buffer_in_source'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_source BEFORE INSERT ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['29TR_ti_ms_priority_message_buffer_in_dest'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_dest BEFORE INSERT ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['29TR_ti_ms_priority_message_buffer_in_typeu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_typeu BEFORE UPDATE ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['29TR_ti_ms_priority_message_buffer_in_sourceu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_sourceu BEFORE UPDATE ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['29TR_ti_ms_priority_message_buffer_in_destu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_in_destu BEFORE UPDATE ON ms_priority_message_buffer_in
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_in has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        

        
        #ms_priority_message_buffer_out

        self.create["30TR_tj_ms_priority_message_buffer_out"]="""
CREATE TRIGGER TR_tj_ms_priority_message_buffer_out BEFORE UPDATE ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                  UPDATE ms_priority_message_buffer_out SET time = CURRENT_TIMESTAMP WHERE messageid = NEW.messageid;
             END;"""
        self.create['30TR_tj_ms_priority_message_buffer_out_type'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_type BEFORE INSERT ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_source'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_source BEFORE INSERT ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_dest'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_dest BEFORE INSERT ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_typeu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_typeu BEFORE UPDATE ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.type) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_sourceu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_sourceu BEFORE UPDATE ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has source not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.source) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_destu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_destu BEFORE UPDATE ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has dest not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.dest) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_status'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_status BEFORE INSERT ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has invalid status')
                WHERE (SELECT value FROM ms_message_buffer_out_enum WHERE procid = NEW.state) IS NULL;
             END;"""

        self.create['30TR_tj_ms_priority_message_buffer_out_statusu'] = """
CREATE TRIGGER TR_ms_priority_message_buffer_out_statusu BEFORE UPDATE ON ms_priority_message_buffer_out
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_priority_message_buffer_out has invalid status')
                WHERE (SELECT value FROM ms_message_buffer_out_enum WHERE procid = NEW.state) IS NULL;
             END;"""



        

        #ms_subscription

        self.create['31TR_tk_ms_subscription_typeid'] = """
CREATE TRIGGER TR_ms_subscription_type BEFORE INSERT ON ms_subscription
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.typeid) IS NULL;
             END;"""

        self.create['31TR_tk_ms_subscription_procid'] = """
CREATE TRIGGER TR_ms_subscription_source BEFORE INSERT ON ms_subscription
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""

        self.create['31TR_tk_ms_subscription_typeidu'] = """
CREATE TRIGGER TR_ms_subscription_typeu BEFORE UPDATE ON ms_subscription
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.typeid) IS NULL;
             END;"""

        self.create['31TR_tk_ms_subscription_procidu'] = """
CREATE TRIGGER TR_ms_subscription_sourceu BEFORE UPDATE ON ms_subscription
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""



        #ms_subscription_priority


        self.create['32TR_tl_ms_subscription_priority_typeid'] = """
CREATE TRIGGER TR_ms_subscription_priority_type BEFORE INSERT ON ms_subscription_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription_priority has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.typeid) IS NULL;
             END;"""

        self.create['32TR_tl_ms_subscription_priority_procid'] = """
CREATE TRIGGER TR_ms_subscription_priority_procid BEFORE INSERT ON ms_subscription_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription_priority has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""

        self.create['32TR_tl_ms_subscription_priority_typeidu'] = """
CREATE TRIGGER TR_ms_subscription_priority_typeu BEFORE UPDATE ON ms_subscription_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription_priority has typeid not in ms_type')
                WHERE (SELECT typeid FROM ms_type WHERE typeid = NEW.typeid) IS NULL;
             END;"""

        self.create['32TR_tl_ms_subscription_priority_procidu'] = """
CREATE TRIGGER TR_ms_subscription_priority_procidu BEFORE UPDATE ON ms_subscription_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_subscription_priority has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""



        

        #ms_available_status
        
        self.create['33TR_tm_ms_available_status'] = """
CREATE TRIGGER TR_ms_available_type BEFORE INSERT ON ms_available
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available has invalid status')
                WHERE (SELECT value FROM ms_there_notthere_enum WHERE value = NEW.status) IS NULL;
             END;"""

        self.create['33TR_tm_ms_available_procid'] = """
CREATE TRIGGER TR_ms_available_source BEFORE INSERT ON ms_available
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""

        self.create['33TR_tm_ms_available_statusu'] = """
CREATE TRIGGER TR_ms_available_typeu BEFORE UPDATE ON ms_available
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available has invalid status')
                WHERE (SELECT value FROM ms_there_notthere_enum WHERE value = NEW.status) IS NULL;
             END;"""

        self.create['33TR_tm_ms_available_procidu'] = """
CREATE TRIGGER TR_ms_available_sourceu BEFORE UPDATE ON ms_available
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""



        

        #ms_available_priority_status

        self.create['34TR_tn_ms_available_priority_status'] = """
CREATE TRIGGER TR_ms_available_priority_type BEFORE INSERT ON ms_available_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available_priority has invalid status')
                WHERE (SELECT value FROM ms_there_notthere_enum WHERE value = NEW.status) IS NULL;
             END;"""

        self.create['34TR_tn_ms_available_priority_procid'] = """
CREATE TRIGGER TR_ms_available_priority_source BEFORE INSERT ON ms_available_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available_priority has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""

        self.create['34TR_tn_ms_available_priority_statusu'] = """
CREATE TRIGGER TR_ms_available_priority_typeu BEFORE UPDATE ON ms_available_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available_priority has invalid status')
                WHERE (SELECT value FROM ms_there_notthere_enum WHERE value = NEW.status) IS NULL;
             END;"""

        self.create['34TR_tn_ms_available_priority_procidu'] = """
CREATE TRIGGER TR_ms_available_priority_sourceu BEFORE UPDATE ON ms_available_priority
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_available_priority has procid not in ms_process')
                WHERE (SELECT procid FROM ms_process WHERE procid = NEW.procid) IS NULL;
             END;"""



        #ms_check_buffer_status


        self.create['35TR_to_ms_check_buffer_status'] = """
CREATE TRIGGER TR_ms_check_buffer_status BEFORE INSERT ON ms_check_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_check_buffer has invalid status')
                WHERE (SELECT value FROM ms_checking_notchecking_enum WHERE value = NEW.status) IS NULL;
             END;"""

        self.create['35TR_to_ms_check_buffer_statusu'] = """
CREATE TRIGGER TR_ms_check_buffer_statusu BEFORE UPDATE ON ms_check_buffer
       FOR EACH ROW
             BEGIN
                SELECT RAISE(ROLLBACK, 'insert on table ms_check_buffer has invalid status')
                WHERE (SELECT value FROM ms_checking_notchecking_enum WHERE value = NEW.status) IS NULL;
             END;"""

 
