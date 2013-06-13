#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  getNextBus.py
#  
#  Copyright 2012 gloyncod <gloyncod@YVRL2199>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import android
import urllib
import urllib2
import string
import sys
import time
from BeautifulSoup import BeautifulSoup
import getNextBusHTTP

# code body
droid = android.Android()

params = droid.getIntent().result[u'extras']
for key in params.keys():
	if key.startswith('%'):
		exec key.lstrip('%') + '="' + params[key] + '"'

if TLINKSTOP:
	msg = getNextBusHTTP.getNextBusHTTP(TLINKSTOP)
	print msg
	#droid.ttsSpeak(msg)
	
