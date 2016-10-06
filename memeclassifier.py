#Matthew Perez
#Meme-classifier

import praw
import time
import mysql.connector
import sys
from pprint import pprint
import urllib2
from boilerpipe.extract import Extractor
import string


#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

#store answers
meme_arr = []

k=3

def normalize_text(text):
	text = text.lower()	#lowercase

	remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
	text = text.translate(remove_punctuation_map)
	#text = text.translate(None, string.punctuation)	#remove punc



	return text

def parent_child_check(parent_text, parent_id):
	cursor.execute("SELECT * FROM comment where comment.parent_id = '" + parent_id + "'")
	comment_list = cursor.fetchall()

	parent_text = normalize_text(parent_text)	#normalize text

	for comment in comment_list:
		for index, word in enumerate(parent_text.split()):	#go through parent_text and formulate possible memes
			possible_meme = "" #reset possible meme
			if index >= (len(parent_text.split()) - (k-1)):	#go to last possible meme that can be constructed (stop at kth element from last)
				break
			for i in range(index, index+k):	#construct possible meme
				possible_meme = possible_meme +" "+ parent_text.split()[i]

			#print("poss meme: "+possible_meme+"\nBody Search: "+ comment[6]+"\n\n")
			#check if possible meme is in comment body
			if possible_meme in normalize_text(comment[6]):
				#win! store off tuple <post_id, parent_id, possible_meme>
				meme_tup = (comment[0], parent_id, possible_meme)
				meme_arr.append(meme_tup)

		parent_child_check(comment[6], 't1_' + comment[0]) 		#recursive call


#Main
#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id limit 10")
post_list = cursor.fetchall()

for post in post_list:
	meme_arr = []	# Reset common memes found
	if post[4] is not u'':	#check if post is composed of selftext
		text = post[4]
	elif post[10] is not u'':	#if not, use boilerpipe to extract text
		extractor = Extractor(extractor='ArticleExtractor', html=post[10])
		text = extractor.getText()
	else:
		text = u''
	parent_child_check(text, "t3_" + post[0])
	print("Title: " + post[2] + "\nArray: ")
	if not meme_arr:
		print "No common words found"
	else:
		for p in meme_arr: print p
	print("\n")
