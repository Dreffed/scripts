#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python 2.7
# ======================================================================
# @author:	David Gloyn-Cox
# @created:	2012-06-05
# ======================================================================
# Changelog
#	2012-06-05	Initial creation
#	2012-06-07	Changed print output to simplify output log analysis
#				Added exclusion section to prevent recursive mining
#				Added exclusion to prevent minign into admin reports
#	2012-06-15	Changed comments and function names to bring into line 
#				functionality
# ======================================================================
#
import datetime
import urllib
import urllib2
import string
import sys
import os
import time
import random
from BeautifulSoup import BeautifulSoup
from pysqlite2 import dbapi2 as sqlite
from urlparse import urlparse
import dbUtils


def createSchema(cursor):
	""" This method will check for the schema and will create it is necessary"""
	#cursor.execute("DROP TABLE files")
	if len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sitelog'").fetchall()) == 0:
		cursor.execute('CREATE TABLE sitelog (id INTEGER PRIMARY KEY, url VARCHAR(1024), rUrl VARCHAR(1024), state INTEGER, responseHdr VARCHAR(2048), dateRequest TIMESTAMP, dateLoad TIMESTAMP, dateExit TIMESTAMP, size LONG, sessionDate TIMESTAMP)')

	if len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sitelinks'").fetchall()) == 0:
		cursor.execute('CREATE TABLE sitelinks (id INTEGER PRIMARY KEY, url VARCHAR(1024), dateAdded TIMESTAMP, scancount INTEGER, sessionDate TIMESTAMP)')
		
	if len(cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sitetree'").fetchall()) == 0:
		cursor.execute('CREATE TABLE sitetree (id INTEGER PRIMARY KEY, urlId INTEGER, urlIdParent INTEGER, sessionDate TIMESTAMP)')
	
	
def addLink(sessId, url, cursor):
	""" Will add a link to the table or update the scan count if the link
		already exists
	"""
	try:	
		if len(cursor.execute("SELECT id FROM sitelinks WHERE url = ? AND sessionDate = ?",(url, sessId)).fetchall()) == 0:
			scount = 0
			cursor.execute("INSERT INTO sitelinks (url, scancount, dateAdded, sessionDate) VALUES (?,?,?,?)",(url, 0, datetime.datetime.now(), sessId))
		
		else:
			(scount,) = cursor.execute("SELECT scancount FROM sitelinks WHERE url = ? AND sessionDate = ?",(url, sessId)).fetchone()
			cursor.execute("UPDATE sitelinks SET scancount = ? WHERE url = ? AND sessionDate = ?",((scount+1),url, sessId))
	
		(resp,) = cursor.execute("SELECT id FROM sitelinks WHERE url = ?",[url]).fetchone()
		
	except sqlite.Error, e:	
		print "Error in addLink() %s:" % e.args[0]
					
	return (resp,scount)
	
	
def addTree(sessId, urlIdParent, urlId, cursor):
	""" this will add an entry into the site tree table"""
	try:
		if len(cursor.execute("SELECT urlIdParent, urlId FROM sitetree WHERE urlIdParent = ? AND urlId = ? AND sessionDate = ?",(urlIdParent, urlId, sessId)).fetchall()) == 0:
			cursor.execute("INSERT INTO sitetree (urlIdParent, urlId, sessionDate) VALUES (?,?,?)",(urlIdParent, urlId, sessId))
		
	except sqlite.Error, e:	
		print "Error in addTree() %s:" % e.args[0]
	
	
def addLog(sessId, url, rUrl, responseHdr, dateRequest, dateLoad, dateExit, size, cursor):
	""" this will add an entry in to the log file about the upload and 
	header file"""

	try:
		if len(cursor.execute("SELECT url FROM sitelog WHERE url = ? AND sessionDate = ?",(url, sessId)).fetchall()) == 0:
			cursor.execute("INSERT INTO sitelog (url, rUrl, responseHdr, dateRequest, dateLoad, dateExit, size, sessionDate) VALUES (?,?,?,?,?,?,?,?)",(url, rUrl, responseHdr, dateRequest, dateLoad, dateExit, size, sessId ))
		
	except sqlite.Error, e:	
		print "Error in addLog() %s:" % e.args[0]
	

def excerciseLink(sessId, url, cursor):
	""" This method will load a page and then look for links, for each 
		link it will check for local, then add it to the link queue
	"""
	lId, scanned = addLink(sessId, url, cursor)
	print "--\t[%d]\t(%d)\t%s" % (lId, scanned, url)
	try:
		if str(url).endswith("pdf"):
			print "\t==\tskip\tpdf"
			
		# only scan if the link is new...
		elif scanned <= 1:
			# now we have a link id we can now add the child links...
			user_agent = 'Mozilla/5 (Solaris 10) Gecko'
			headers = { 'User-Agent' : user_agent }

			request = urllib2.Request(url, "", headers)
			startTime = datetime.datetime.now()	
			response = urllib2.urlopen(request)	
			endTime = datetime.datetime.now()

			data = response.read()
			pool = BeautifulSoup(data)

			print "\tTiming:\t%s\t%s" % (startTime, endTime)

			rUrl = response.geturl()
			rHdr = str(response.info())

			if rUrl != url:
				print "\tRedirect:\t%s" % rUrl
				(lId, sCount) = addLink(sessId, rUrl, cursor)

			# update the link
			addLog(sessId, url, rUrl, rHdr, startTime, endTime, endTime, len(data), cursor) 		

			# we now have the page
			href = pool.findAll('a')
			for a in href:
				# check the node has a 'href' attribute
				if a.has_key('href'):
					cUrl = a['href']
					
					# check for self linked pages...
					# relative link is to the site not the calling page
					if cUrl.startswith("/"):
						sAddr = urlparse(rUrl)
						sUrl = "%s://%s" % (sAddr.scheme, sAddr.hostname)
						cUrl = "%s%s" % (sUrl,cUrl)
						rUrl = sUrl
					
					# recurse the call back to get the child links...
					(cId, cCount) = addLink(sessId, cUrl, cursor)
					addTree(sessId, lId, cId, cursor)
					
					# exclude sites with the following link
					if cCount > 0:
						print "\t**\tskip\tscanned\t[%s]" % cUrl
					
					elif "xhprof_html" in cUrl:
						print "\t==\tskip\txprof_html"
						
					elif cUrl.endswith(".pdf"):
						print "\t==\tskip\tpdf"

					# pause for random time...
					elif cUrl.startswith(rUrl):
						print "\t>>\t%s\t%s" % (rUrl, cUrl)
						pTime = random.randint(1, 10)
						time.sleep(pTime)
						excerciseLink(sessId, cUrl, cursor)
						
		else:
			print "\t==\tskip\tsacnned\t%s" % url

	except UnicodeEncodeError as oops:
		print "\tUnicodeError:\t", oops
		print "\t\t%s" % url
		
	except:
		print "\tUnexpected error:\t", sys.exc_info()[0]
		print "\t\t%s" % url


def dumpSlowestSession(sessId, cursor):
	""" this will dump the top 10 slowest pages for this run"""
	rows = cursor.execute("SELECT id, url, (julianday(dateLoad) - julianday(daterequest)) * 100000 as loadTime, dateLoad, dateRequest FROM sitelog WHERE sessionDate = ? ORDER BY (julianday(dateLoad) - julianday(daterequest)) DESC", [sessId]).fetchall()
	count = 0
	for row in rows:
		count += 1
		if count <= 10:
			(urlId, url, urlTime, dateLoad, dateRequest) = row
			if count == 1:
				wId = urlId
				
			print "\t%s\t%s\t%s\t%s\t%s" % row

	return int(wId)


def dumpSlowest(cursor):
	""" this will dump the top 10 slowest pages for all runs"""
	rows = cursor.execute("SELECT id, url, (julianday(dateLoad) - julianday(daterequest)) * 100000 as loadTime, dateLoad, dateRequest FROM sitelog ORDER BY (julianday(dateLoad) - julianday(daterequest)) DESC").fetchall()
	count = 0
	for row in rows:
		count += 1
		if count <= 10:
			(urlId, url, urlTime, dateLoad, dateRequest) = row
			if count == 1:
				wId = urlId
				
			print "\t%s\t%s\t%s\t%s\t%s" % row

	return int(wId)

			
def dumpWorstRecord(urlId, cursor):
	""" this will dump the record from the worst id record """
	rows = cursor.execute("select rUrl, responseHdr, size, sessionDate from sitelog where id = ?",[urlId])
	for row in rows:
		print "\t%s\t%s\t%s\t%s" % row


if __name__ == '__main__':
    # http://blog.dispatched.ch/2009/03/15/webscraping-with-python-and-beautifulsoup/
	"""-- Web Site Excerciser
		This will walk a specified site and navigate the links
		It will load the links and maintain a list of URLs to load
		It will wait for a small period after successful load before
		navigating to a child link.
		For each link clicked it will store a log of the following:
			URL
			RequestTime
			LoadTime
	"""
			
	print "##\tStart\t%s\t##" % datetime.datetime.now()
	try:
		connection = dbUtils.connectDB('seLog.db')
		cursor = connection.cursor()	
		createSchema(cursor)
		
		sessId = datetime.datetime.now()
		url = "<url to scan>"
		excerciseLink(sessId, url, cursor)
		
		print "##\tScanned site %s has been processed." % url
		
		print "##\tWorst pages are this session:"
		dumpSlowestSession(sessId, cursor)

		print "##\tWorst pages are:"
		wId = dumpSlowest(cursor)
	
		print "##\tWorst Page is:\t%d" % wId
		dumpWorstRecord(wId, cursor)
	
	except UnicodeEncodeError as oops:
		print "##\tUnicodeError:\t", oops
		
	except:
		print "##\tUnexpected error:\t", sys.exc_info()[0]
    
	finally:
		print "##\tEnd\t%s\t##" % datetime.datetime.now()
		dbUtils.closeDB(connection)
	
