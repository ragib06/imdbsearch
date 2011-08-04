#!/usr/bin/env python
# -*- coding: utf-8 -*-
# auther:		Ragib Ahsan
# thanks to:	Sufian Latif, Dhiman Paul
# date:   		June 15, 2011
# libraries:	BeautifulSoup, mechanize

import imdb
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import csv, re, sys, signal, codecs, HTMLParser, time, random

def initiaiteCSV(filename):
	fout = codecs.open(filename, 'wb', 'utf-16')
	header = [u'Title', u'Release', u'Rating', u'Genres', u'Director', u'Stars', u'Runtime']
	fout.write(','.join(header)+'\n')
	fout.flush()
	return fout
	
def dumpToCSV(fout, result):
	for r in result:
		fout.write(','.join(r)+'\n')
		fout.flush()
	fout.close()

#need to check
def sortRating(searchresult):
	"""
	sorts the search result got from 'searchimdb.getMovieInfo' into descending order of rating
	"""

	#cast rating to float type for sorting
	for result in searchresult:
		result[1] = float(result[1])
	#sort results according to descending order of rating
	sortedresult = sorted(searchresult, key=lambda t: t[1], reverse = True)
	#cast rating back to string type
	for result in sortedresult:
		result[1] = unicode(str(result[1]))
	return sortedresult

def unescapehtml(html):
	"""
	unescapes the html code fetched by BeautifulSoup
	"""
	return HTMLParser.HTMLParser().unescape(html)
	
def searchTitle(rawtitle):
	br = Browser()
	# Ignore robots.txt
	br.set_handle_robots( False )
	# Google demands a user-agent that isn't a robot
	br.addheaders = [('User-agent', 'Firefox')]
	
	br.open( "http://www.google.com " )
	br.select_form( 'f' )
	s='imdb'+' + '+' '.join(re.compile('[\.]').split(rawtitle))
	br.form[ 'q' ] = s
	br.submit()

	resp = None
	for link in br.links():
		siteMatch = re.compile( 'www.imdb.com/title/tt[0-9]*/$' ).search( link.url )
		if siteMatch:
		    resp = br.follow_link( link )
		    print link.url
		    break

	soup = BeautifulSoup(resp.get_data())
	
	title = re.sub(' - IMDb','',soup.find('title').string)
	title = re.sub('\([0-9]*\)','',title)
	
	return title


def getMovieInfo(name, pd):
	"""
	fetches the info for movie named 'name' from imdb with debug mode 'pd'
	Usage:
		pd = True => debug prints on
		pd = False => debug prints off
	"""
	
	if(pd == True):	print '**searching movie:',name,'\n'
		
	title = searchTitle(name)
	print 'filtered title: ', unescapehtml(title)
	
	ia = imdb.IMDb()
	print '*',
	s_result = ia.search_movie(title)
	print '*',
	movie = s_result[0]
	print '*',
	ia.update(movie)
	print '*'
	summary = movie.summary().split('\n')
	
	raw_title = re.sub('.*: ','',summary[2]).split('(')
	title = raw_title[0].strip()
	release = re.sub('\)','',raw_title[1].strip())
	genre = re.sub('\.$','',re.sub(', ','|',re.sub('.*: ','',summary[3])) )
	director = re.sub('\.$','',re.sub('.*: ','',summary[4]))
	raw_cast = re.sub('\([^,]*\)','',re.sub('.*: ','',summary[6]))
	cast = re.sub('\.$','',re.sub(' , ','|',raw_cast))
	runtime = re.sub('\.$','',re.sub('.*: ','',summary[7])) 
	rating = re.sub('\(.*\)\.','',re.sub('.*: ','',summary[10])).strip()

	if(pd == True):
		print 'title: ',title
		print 'release: ',release
		print 'rating: ',rating
		print 'runtime: ',runtime
		print 'director: ',director
		print 'genres: ',genre
		print 'cast: ',cast
		print '\n\n'

	return [title.strip(), release.strip(), rating.strip(), genre.strip(), director.strip(), cast.strip(), runtime.strip()]

def main():
	FILEOUT = 'movies@imdb.csv'
	if len(sys.argv)==2:
		FILEOUT = sys.argv[1]
	
	fout = initiaiteCSV(FILEOUT)
	searchresult = []
	for name in sys.stdin:
		name = name.strip()
		try:
			mi = getMovieInfo(name, True)
			if mi!=None:
				fout.write(','.join(mi)+'\n')
				fout.flush()
		except:
			print 'error fetching movie: ***',name
		
	
	

if __name__ == '__main__':
	main()
	


