#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-08-19 15:33:46
# @Author  : OO 
# @Link    : 
# @Version : V0.0.1

from pynnmsg import SURVEY_CLIENT

if __name__ == '__main__':
    _url = "tcp://127.0.0.1:12345"
    _client0 =  SURVEY_CLIENT('c0', _url)
    _client0.nodeRun()
