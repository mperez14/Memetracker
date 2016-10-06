#Matthew Perez
#Meme-classifier

import praw
import time
import mysql.connector
import sys
from pprint import pprint
import urllib2
from boilerpipe.extract import Extractor


#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

def parent_child_check(txt, id):
	return 0
	#recursive call


#Main

#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id")
post_list = cursor.fetchall()

var text
for post in post_list:
	if post.selftext:	#check if post is composed of selftext
		text = post.selftext
	else:	#if not, use boilerpipe to extract text
		extractor = Extractor(extractor='ArticleExtractor', url=post.url)
		text = extractor.getText()


	parent_child_check(text, post.id)
	print(post)