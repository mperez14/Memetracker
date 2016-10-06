#Matthew Perez
#Meme-classifier

import praw
import time
import mysql.connector
import sys
from pprint import pprint
import urllib2
from boilerpipe.extract import Extractor

k = 3
#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

meme_arr = []

def normalize_text(text):
	text = text.lower()	#lowercase
	text = text.translate(None, string.punctuation)	#remove punc

def parent_child_check(parent_text, parent_id):
	cursor.execute("SELECT * FROM comment where comment.parent_id = ", parent_id)	#is correct?
	comment_list = cursor.fetchall()

	parent_text = normalize_text(parent_text)	#normalize text

	for comment in comment_list:	#go thru all comments
		for index, word in enumerate(parent_text.split()):	#check each word
			possible_meme = "" #reset poss. meme
			if index >= (len(parent_text.split()) - (k-1)):
				break
			for i = range(index, index+k):	#construct possible meme
				possible_meme = possible_meme + parent_text.split()[i]

			#check if possible meme is in comment
			if possible_meme in comment.body:
				#win! store off tuple <post_id, parent_id, possible_meme>
				meme_tup = (comment.id, parent_id, possible_meme)
				meme_arr.append(meme_tup)

		#down the rabbit hole we go	(DFS recursion)
		parent_child_check(comment.body, comment.id)


#Main
#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id")
post_list = cursor.fetchall()

for post in post_list:
	if post.selftext:	#check if post is composed of selftext
		text = post.selftext
	else:	#if not, use boilerpipe to extract text
		extractor = Extractor(extractor='ArticleExtractor', url=post.url)
		text = extractor.getText()
	#call recursive function to check for meme pairs in comments
	parent_child_check(text, post.id)