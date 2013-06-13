import urllib
import urllib2
import string
import sys
import time
from BeautifulSoup import BeautifulSoup

def getNextBusHTTP(stopNumber):
	try:
		url = "http://www.transitdb.ca/nextbus/%s/" % stopNumber
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
			
		the_page = response.read()
		pool = BeautifulSoup(the_page)

		# get the h1
		result = pool.findAll('h1')[0]
		result = result.findAll('span')[0]
		statement = '%s. ' % result.findAll(text=True)[0]

		# get the bus links and table...
		results = pool.findAll('td')
		isFirst = True
		dicBus = {}
		
		for result in results:
			# this will come in pairs...
			# first is time, second is bus	
			if isFirst == True:
				busTime = result.findAll(text=True)[0].replace(":"," ")
				isFirst = False
			else:
				busName = result.findAll(text=True)[0]
				if dicBus.has_key(busName):
					pass
				else:
					dicBus[busName] = busTime
				isFirst = True

		# build statement from the dictionary
		for key in dicBus.keys():
			statement += '\n%s at %s' % (key, dicBus[key])
			
		# breakout abbrvs..
		dicAbbrv = {}
		dicAbbrv['AV'] = 'Avenue'
		dicAbbrv['STN'] = 'Station'
		dicAbbrv['ST'] = 'Street'
		dicAbbrv['NB'] = 'North Bound'
		dicAbbrv['SB'] = 'South Bound'
		dicAbbrv['FS'] = 'Far Side'
		dicAbbrv['00'] = 'hundred'

		for key in dicAbbrv.keys():
			statement = statement.replace(key,dicAbbrv[key])
	
	except:
		statement = sys.exc_info()[0]
		
	# return the statement
	return statement
