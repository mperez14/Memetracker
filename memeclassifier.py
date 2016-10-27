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
import regex as re

#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

#store answers
meme_arr = []

#word window size
k=3

def normalize_text(text):
	text = text.lower()	#lowercase
	text = re.sub("[^\P{P}.?!]+", "", text)	#strip all punctuation except '.?!'
	return text

def roll_helper(meme, i, comment_id, parent_id, arr):
	if meme.rsplit(" ", 1)[1] == arr[i].rsplit(" ", 1)[0]:#combine and return
		memebuilder=memebuilder+str2.rsplit(" ", 1)[1]
	else:
		#build meme tup and add to array
		meme_tup = (comment_id, parent_id, memebuilder)
		meme_arr.append(meme_tup)

		#reset memebuilder
		memebuilder = arr[i]

def rollup_memes(comment_id, parent_id, arr):
	#given array, roll up common memes found in array
	i=0
	memebuilder = arr[i]
	for i in range(0,len(arr)-1):
		# print("arr[i]:"+arr[i])
		# print("arr[i+1]:"+arr[i+1])
		# print("1:"+arr[i].split(" ", 1)[1])
		# print("2:"+arr[i+1].rsplit(" ", 1)[0])

		if arr[i].split(" ", 1)[1] == arr[i+1].rsplit(" ", 1)[0]:#combine and return
			memebuilder=memebuilder+" "+arr[i+1].rsplit(" ", 1)[1]
		else:
			meme_tup = (comment_id, parent_id, memebuilder)
			meme_arr.append(meme_tup)

			#reset memebuilder
			memebuilder = arr[i+1]


def parent_child_check(parent_text, parent_id):
	cursor.execute("SELECT * FROM comment where comment.parent_id = '" + parent_id + "'")
	comment_list = cursor.fetchall()

	#print("Un-normal text: " + parent_text)
	parent_text = normalize_text(parent_text)	#normalize text
	if re.match(r't3_',parent_id):
		print "# comments: ",len(comment_list)
	for comment in comment_list:
		#for sentence in parent_text.split(".|!|?"):
		#print("Parent Text: "+ parent_text)
		#print("comparative text: "+normalize_text(comment[6]))
		for sentence in re.split(r'\.\n|\. |\! |\!\n|\? |\?\n', parent_text):
			#print("sentence: "+ sentence)
			sentence_arr = []
			for index, word in enumerate(sentence.split()):	#go through parent_text and formulate possible memes
				possible_meme = "" #reset possible meme
				if index >= (len(sentence.split()) - (k-1)):	#go to last possible meme that can be constructed (stop at kth element from last)
					break
				for i in range(index, index+k):	#construct possible meme (k size)
					if not possible_meme:
						possible_meme = sentence.split()[i]
					else:
						possible_meme = possible_meme +" "+ sentence.split()[i]

				#print("poss meme: "+possible_meme+"\nBody Search: "+ comment[6]+"\n\n")
				# #check if possible meme is in comment body
				# if possible_meme in normalize_text(comment[6]):
				# 	#win! store off tuple <post_id, parent_id, possible_meme>
				# 	meme_tup = (comment[0], parent_id, possible_meme)
				# 	meme_arr.append(meme_tup)

				#check if possible_meme in comment
				if possible_meme in normalize_text(comment[6]):
					sentence_arr.append(possible_meme)	#sent_arr stores memes in sentence

			#roll up memes_found in sentence_arr
			#after each sentence, add sentence_Arr to meme_arr and clear sentence_arr
			if sentence_arr:
				rollup_memes(comment[0], parent_id, sentence_arr)

			#for each sentence check about rolling up
		parent_child_check(comment[6], 't1_' + comment[0]) 		#recursive call


#Main
#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id limit 5")
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
	print("Title: " + post[2].encode('utf-8') + "\nArray: ")
	if not meme_arr:
		print "No common words found"
	else:
		#print "words found"
		for p in meme_arr: print p
	print("\n")