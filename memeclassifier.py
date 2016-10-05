#Matthew Perez
#Meme-classifier

import praw
import time
import mysql.connector
import sys
from pprint import pprint
import urllib2

cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

def parent_child_check(text, id):
	return 0
	#recursive call


#Main

#get all posts
cursor.exectue("select * from post")
post_list = cursor.fetchall()


for post in post_list:
	print(post)