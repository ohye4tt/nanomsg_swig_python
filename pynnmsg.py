#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-08-19 15:33:46
# @Author  : OO 
# @Link    : 
# @Version : V0.0.1

import sys
import PY_NANOMSG
import time

class SURVEY_NODE(object):
    """
    nanomsg survey mode
    """
    
    nodeType = None
    nodeName = None
    nodeUrl = None
    uniqName = None
    #store all node buffer for nodes
    nodePtrRecvBuf = {}
    bufferSize = 2*1024

    def __init__(self, nodeName, nodeUrl, nodeType):
        """
        node initialize
        """
        self.nodeType = nodeType
        self.nodeName = nodeName
        self.nodeUrl = nodeUrl
        self.uniqName = self.nodeType+'_'+self.nodeName
        self.nodeInit()

    def getCurTime(self):
        _format = '%Y-%m-%d %X'    
        return time.strftime(_format, time.localtime())
    
    def nodeInit(self):
        print '%s node initialize %s'%(self.getCurTime(), self.uniqName)
        if self.uniqName not in self.nodePtrRecvBuf:
            self.nodePtrRecvBuf[self.uniqName] = {}
            #for nn_recv
            self.nodePtrRecvBuf[self.uniqName]['recv'] = PY_NANOMSG.malloc_void_p(self.bufferSize)
            #for nn_send
            self.nodePtrRecvBuf[self.uniqName]['send'] = PY_NANOMSG.malloc_void_p(self.bufferSize)
        else:
            print 'error node name is not uniqueness', _name
            sys.exit('error node name is not uniqueness')

    def nodeStop(self):
        for _ptr in self.nodePtrRecvBuf:
            if self.nodePtrRecvBuf[_ptr]:
                PY_NANOMSG.free_void_p(self.nodePtrRecvBuf[_ptr]['recv'])
                PY_NANOMSG.free_void_p(self.nodePtrRecvBuf[_ptr]['send'])
                self.nodePtrRecvBuf[_ptr] = None

    def nodeRun(self):
        print '%s node run %s'%(self.getCurTime(), self.uniqName)

    def nodeSend(self, sockt, string, flag=0):
        PY_NANOMSG.memmove(self.nodePtrRecvBuf[self.uniqName]['send'], string)
        return PY_NANOMSG.nn_send(sockt, self.nodePtrRecvBuf[self.uniqName]['send'], len(string), flag)

    def nodeRecv(self, sockt, flag=0):
        """
        when OK return string;
        when server timeoute return None;
        when client recv nothing return False
        when recv bytes is 0 return 0
        """
        print self.uniqName, 'recv ......'
        _bytes = PY_NANOMSG.nn_recv(sockt, self.nodePtrRecvBuf[self.uniqName]['recv'], self.bufferSize, flag)
        # print self.uniqName, 'recv bytes', _bytes
        if _bytes == PY_NANOMSG.ETIMEDOUT:
            print '%s %s recv bytes %d error is %s'%(self.getCurTime(), self.uniqName, _bytes, \
                                                        PY_NANOMSG.nn_strerror(PY_NANOMSG.nn_errno()))
            return None
        elif _bytes < 0:
            print '%s %s recv bytes %d error is %s'%(self.getCurTime(), self.uniqName, _bytes, \
                                                        PY_NANOMSG.nn_strerror(PY_NANOMSG.nn_errno()))
            return False
        elif _bytes == 0:
            return 0
        else:
            _buf = PY_NANOMSG.cdata(self.nodePtrRecvBuf[self.uniqName]['recv'], _bytes)
            # use my buffer, do not nn_freemsg buffer
            # PY_NANOMSG.nn_freemsg(self.nodePtrRecvBuf[self.uniqName]['recv'])
            return _buf

    def nodeShutdown(self, sockt, flag=0):
        return PY_NANOMSG.nn_shutdown(sockt, flag)


class SURVEY_SERVER(SURVEY_NODE):
    """
    nanomsg survey mode,server node
    """  

    def __init__(self, nodeName, nodeUrl, nodeType='server'):
        """
        node initialize
        """
        super(SURVEY_SERVER,self).__init__(nodeName, nodeUrl, nodeType)

    def nodeInit(self):
        """
        server node initialize
        """
        super(SURVEY_SERVER,self).nodeInit()
        self.nodeSock = PY_NANOMSG.nn_socket(PY_NANOMSG.AF_SP, PY_NANOMSG.NN_SURVEYOR)
        if self.nodeSock >= 0:
            if PY_NANOMSG.nn_bind(self.nodeSock, self.nodeUrl) >= 0:
                time.sleep(1)
        else:
            print 'error nn_socket', self.nodeType, self.nodeName

    def nodeRun(self):
        super(SURVEY_SERVER,self).nodeRun()
        _rc = self.nodeSend(self.nodeSock, self.uniqName+'_hello')
        print '%s node %s send bytes %d'%(self.getCurTime(), self.uniqName, _rc)
        while(True):
            _rc = self.nodeRecv(self.nodeSock)
            if _rc == None:
                break
            elif _rc == False:
                time.sleep(1)
            print '%s node %s recv'%(self.getCurTime(), self.uniqName), _rc
        self.nodeShutdown(self.nodeSock)


class SURVEY_CLIENT(SURVEY_NODE):
    """
    nanomsg survey mode,client node
    """
    
    def __init__(self, nodeName, nodeUrl, nodeType='client'):
        """
        node initialize
        """
        super(SURVEY_CLIENT,self).__init__(nodeName, nodeUrl, nodeType)

    def nodeInit(self):
        """
        client node initialize
        """
        super(SURVEY_CLIENT,self).nodeInit()
        self.nodeSock = PY_NANOMSG.nn_socket(PY_NANOMSG.AF_SP, PY_NANOMSG.NN_RESPONDENT)
        if self.nodeSock >= 0:
           if PY_NANOMSG.nn_connect(self.nodeSock, self.nodeUrl) >= 0:
                time.sleep(1)
        else:
            print 'error nn_socket', self.nodeType, self.nodeName


    def nodeRun(self):
        super(SURVEY_CLIENT,self).nodeRun()
        while(True):
            _rc = self.nodeRecv(self.nodeSock)
            print '%s node %s recv'%(self.getCurTime(), self.uniqName), _rc
            if _rc >= 0:
                _ss = self.nodeSend(self.nodeSock, self.uniqName+'_hello')
                print '%s node %s send bytes %d'%(self.getCurTime(), self.uniqName, _ss)
            else:
                time.sleep(1)
        self.nodeShutdown(self.nodeSock)

if __name__ == '__main__':
    _url = "ipc://pynnmsg"
    _server = SURVEY_SERVER('s0', _url)
    _client0 =  SURVEY_CLIENT('c0', _url)
    time.sleep(1)
    _server.nodeRun()
    _client0.nodeRun()
