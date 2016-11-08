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
import operator
import json
import os.path
#from sklearn.feature_extraction.text import TfidTransformer


#Check arguments
if len(sys.argv) != 2:
	print("Please enter argument <window size>\n")
	sys.exit()

print("arg:", sys.argv[1])

#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

#store answers
meme_arr = []

#word window size
k=int(sys.argv[1])

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
	for comment in comment_list:
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

				#put possible_meme in dict
				if possible_meme not in meme_dict:
					meme_dict[possible_meme] = 0
				meme_dict[possible_meme] += 1

			#roll up memes_found in sentence_arr
			#after each sentence, add sentence_Arr to meme_arr and clear sentence_arr
			#if sentence_arr:
			#	rollup_memes(comment[0], parent_id, sentence_arr)

			#for each sentence check about rolling up
		parent_child_check(comment[6], 't1_' + comment[0]) 		#recursive call


#Main
#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id limit 10")
post_list = cursor.fetchall()
meme_dict = {}
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



	#if meme_dict bigger than certain # of elems, clear bottom half

	max_dict_size = 1000
	if len(meme_dict) > max_dict_size:
		# get median val, delete all items in dict that have median or lower values
		val_arr = []
		for w in sorted(meme_dict, key=meme_dict.get):
			val_arr.append(meme_dict[w])
	 		# print w, meme_dict[w]
	 	median = 0
	 	if len(val_arr) > 0:	#find median
	 		median = val_arr[len(val_arr)/2]
	 		print "median: ", median
	 	for x in range(1, median+1):	#remove all elements in dictionary with value less than or equal to median
	 		meme_dict = {k: v for k, v in meme_dict.iteritems() if v != x}

	 	#print "memedict: ", meme_dict
	# 	meme_dict_list = sorted(meme_dict.items(), key = operator.itemgetter(1))
	# 	for  x in range(max_dict_size/2):
	# 		print(x)
	# 		del 
	# 	print("dict: ", meme_dict_list[0])
	# 	for x in meme_dict_2[0]:
	# 		#del
	# 		print(x)
	#meme_dict = sorted(meme_dict)
meme_dict = sorted(meme_dict.items(), key = operator.itemgetter(1))
print meme_dict

write data to output file
text_file = "output_memes_"+str(k)+".txt"
if os.path.isfile(text_file):
	#read and write
	print("do this")

else:
	#create and write
	with open(text_file, 'w') as outfile:
		json.dump(meme_dict, outfile)



