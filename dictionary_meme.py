#Matthew Perez
#Meme-classifier

import praw
import time
from datetime import datetime
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
from tabulate import tabulate
#from collections import counter
#from sklearn.feature_extraction.text import TfidTransformer


#Check arguments
if len(sys.argv) != 3:
	print("Please enter argument <window size> <on/off>\n")
	sys.exit()

if sys.argv[2] != "on" and sys.argv[2] != "off":
	print("Please enter 'on' or 'off' as second argument to whether or not rollup should be included.\n")
	sys.exit()

#Database
cnx = mysql.connector.connect(user='mperez14', password='meme', database='memetracker')
cursor = cnx.cursor()

#store answers
meme_combine_arr = []	#meme_combine function, stores meme string. Reduces speed (use like linked list) for combine function
excel_data = dict()	#stores meme_str = key, meme_obj = value

#word window size
k=int(sys.argv[1])
roll_flag = sys.argv[2]

#meme object
class Meme(object):
	text = ""
	date_frequency = {} #dict for frequency/date
	total_frequency = 0 #total frequency
	newest_date = "1/1/1970"
	oldest_date = time.strftime("%m/%d/%Y")

	def add_meme_occurance(self, date):
		if date not in self.date_frequency:
			self.date_frequency[date] = 0
		self.date_frequency[date] += 1 #put in dictionary
		self.total_frequency += 1 #increase total frequency

		# print("in date: ", date)
		# print("old date: ", self.oldest_date)
		# print("new date: ", self.newest_date)
		dt = datetime.strptime(date, "%m/%d/%Y")
		old_date = datetime.strptime(self.oldest_date, "%m/%d/%Y")
		new_date = datetime.strptime(self.newest_date, "%m/%d/%Y")
		#print("compare date < oldest_date", (dt<old_date))
		if (dt<old_date):
			self.oldest_date = date
		if (dt>new_date):
			self.newest_date = date
		# 	dt = self.oldest_date
		#if(datetime()<self.lowest_date)

	def __repr__(self):
		return str((self.text, self.total_frequency, self.date_frequency, self.newest_date, self.oldest_date))

def makeMeme(text):
	my_meme = Meme()
	my_meme.text = text
	my_meme.date_frequency = {} #dict for frequency/date
	my_meme.total_frequency = 0 #total frequency
	my_meme.newest_date = "1/1/1970"
	my_meme.oldest_date = time.strftime("%m/%d/%Y")
	return my_meme




def normalize_text(text):
	text = text.lower()	#lowercase
	text = re.sub("[^\P{P}.?!]+", "", text)	#strip all punctuation except '.?!'
	text = re.sub('[<>]', '', text)
	return text

def rollup_memes(comment_id, parent_id, arr):
	#given array, roll up common memes found in array
	i=0
	memebuilder = arr[i]
	for i in range(0,len(arr)-1):
		if arr[i].split(" ", 1)[1] == arr[i+1].rsplit(" ", 1)[0]: #combine and return
			memebuilder=memebuilder+" "+arr[i+1].rsplit(" ", 1)[1]
		else:
			meme_tup = (comment_id, parent_id, memebuilder)
			meme_arr.append(meme_tup)

			#reset memebuilder
			memebuilder = arr[i+1]

def roll_helper(meme, i, comment_id, parent_id, arr):
	if meme.rsplit(" ", 1)[1] == arr[i].rsplit(" ", 1)[0]:#combine and return
		memebuilder=memebuilder+str2.rsplit(" ", 1)[1]
	else:
		#build meme tup and add to array
		meme_tup = (comment_id, parent_id, memebuilder)
		meme_arr.append(meme_tup)

		#reset memebuilder
		memebuilder = arr[i]

def meme_combine(data):
	#Go through linked list objects and combine sentences that are matching and multiple frequencies
	for index, memes in enumerate(meme_combine_arr):
		if index < len(meme_combine_arr)-1:	#dont check last elem

			meme1 = meme_combine_arr[index]
			meme2 = meme_combine_arr[index+1]
			# if meme1 == 'it is very easy to get the':
			# 	print "meme1: ", meme1
			# 	print "meme2: ", meme2
			# 	print "m1 in data: ", meme1 in data
			# 	print "m2 in data: ", meme2 in data
			# 	print "string comp: ", string_compare(meme1, meme2)
			# 	print "m1 date_frequency: ", getattr(data[meme1], 'date_frequency')
			# 	print "m2 date_frequency: ", getattr(data[meme2], 'date_frequency'), "\n"
			# 	print "date freq compare: ", getattr(data[meme1], 'date_frequency')==getattr(data[meme2], 'date_frequency'), "\n"

			# print "meme1: ", meme1
			# print "meme2: ", meme2
			#check meme1 and meme2 in data, total freq >1, strings are off by 1, and date frequency is same
			if meme1 in data and meme2 in data and getattr(data[meme1], 'total_frequency')>1 and string_compare_for(meme1, meme2) and getattr(data[meme1], 'date_frequency')==getattr(data[meme2], 'date_frequency'):
				#combine strings and delete meme2
				s1w = re.findall('\w+', meme1.lower())	#put in dictionary
				s2w = re.findall('\w+', meme2.lower())

				# if s1w == 'it is very easy to get the':
				# 	print "s1: ", s1w
				# 	print "s2: ", s2w
				# 	print "meme1 last: ", s1w[len(s1w)-1]
				# 	print "meme2 last: ", s2w[len(s2w)-2]
					
				if s1w[len(s1w)-1] == s2w[len(s2w)-2]:
					new_str = meme1 + " " + s2w[len(s2w)-1]
					#print "rollup: ", new_str

					excel_data[new_str] = excel_data[meme1]	#replace dictionary
					excel_data[new_str].text = new_str #change string
					del excel_data[meme1]
					del excel_data[meme2]
					meme_combine_arr[index+1] = new_str	#replace next item in linked list with new obj
					# print "next: ", meme_combine_arr[index+1]
					# print "next next: ", meme_combine_arr[index+2]

				elif s2w[len(s2w)-1] == s1w[len(s1w)-2]:	#should never happen due to linked list array
					print "meme1: ", meme1
					print "meme2: ", meme2
					print "next: ", meme_combine_arr[index+2]
					new_str = meme2 + " " +s1w[len(s1w)-1]
					print "rollup 2: ", new_str

					excel_data[new_str] = excel_data[meme1]	#replace dictionary
					del excel_data[meme1]
					del excel_data[meme2]


def string_compare(str1, str2):
	s1w = re.findall('\w+', str1.lower())	#put in dictionary
	s2w = re.findall('\w+', str2.lower())
	common = set(s1w).union(s2w)	#get intersection of two strings. Problem if multiple same words (union doesnt account)
	unique1 = set(s1w)
	unique2 = set(s2w)
	# print ("unique1: ", unique1)
	# print ("unique2: ", unique2)

	max_len = max(len(unique1), len(unique2))

	if len(common) <= max_len+1: #common should only have 1 extra word differing (ex. 'abc', 'bcd' -> 'abcd') abcde + bcdeb
		# print "s1: ", s1w
		# print "s2: ", s2w
		# print "common: ", common
		return True
	else:
		return False

def string_compare_for(str1, str2):
	s1w = re.findall('\w+', str1.lower())	#put in dictionary
	s2w = re.findall('\w+', str2.lower())
	s1_size = len(s1w)
	s2_size = len(s2w)
	# print ("unique1: ", unique1)
	# print ("unique2: ", unique2)

	min_len = min(s1_size, s2_size)
	for x in range(0, min_len-2):
		if s1w[s1_size-1-x] != s2w[s2_size-2-x]:
			return False
	return True
	#abcd cde -> 5 in common

def table_format(data):
	#get size of row (dates)
	time_arr = get_list_of_dates(data)
	meme_arr = create_meme_row(data, time_arr)

	master_table = []
	time_arr = ["Meme/Date"] + time_arr #append header to beginning
	master_table.append(time_arr)
	for memes in meme_arr:
		master_table.append(memes)
	#print tabulate(master_table)

	import codecs

#write data to output file
	text_file = "output_memes_"+str(k)+"_"+str(roll_flag)+".txt"
	outfile = codecs.open(text_file, 'w', 'utf-8')
	outfile.write(tabulate(master_table))


def create_meme_row(data, times):
	master_arr = []
	for meme in data:
		meme_row_arr = []
		meme_row_arr.append(meme.text)
		for date in times:
			if date in meme.date_frequency.keys():	#meme was posted on this date
				count = meme.date_frequency[date]	#check frequency meme was posted
				meme_row_arr.append(count)
			else:
				meme_row_arr.append(0)
		master_arr.append(meme_row_arr)
	return master_arr


def get_list_of_dates(data):
	dates=[]
	#dates.append("Meme/Date")
	for item in data:
		for date in item.date_frequency:
			if date not in dates:
				dates.append(date)
	#sort date
	dates.sort(key=lambda x: time.mktime(time.strptime(x,"%m/%d/%Y")))
	return dates

def parent_child_check(text, parent_id, time_created):
	cursor.execute("SELECT * FROM comment where comment.parent_id = '" + parent_id + "'")
	comment_list = cursor.fetchall()
	text = normalize_text(text)	#normalize text
	#print "dict size: ", len(excel_data)
	#add all memes from text to dictionary
	for sentence in re.split(r'\.\n|\. |\! |\!\n|\? |\?\n', text):
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

				date_time = time.strftime('%m/%d/%Y', time.localtime(time_created))
				#excel data
				# if possible_meme == 'rating is available when the':
				# 	print "sent:", sentence
				if "http" not in possible_meme: #filter website
					if possible_meme not in meme_combine_arr:
						meme_combine_arr.append(possible_meme)
					if possible_meme not in excel_data:
						#print "making new"
						myMeme = makeMeme(possible_meme)
						excel_data[possible_meme] = myMeme
					#print excel_data[possible_meme]
					#print "poss meme: |"+ possible_meme+"|"
					excel_data[possible_meme].add_meme_occurance(date_time)

	#DFS on comment
	for comment in comment_list:
		parent_child_check(comment[6], 't1_' + comment[0], comment[3]) 		#recursive call


#Main
#join content and posts
cursor.execute("SELECT * FROM post INNER JOIN content on post.id = content.post_id limit 200")
post_list = cursor.fetchall()
meme_dict = {}
progress = 0
meme_combine_arr = []
for post in post_list:
	if post[4] is not u'':	#check if post is composed of selftext
		text = post[4]
	elif post[10] is not u'':	#if not, use boilerpipe to extract text
		extractor = Extractor(extractor='ArticleExtractor', html=post[10])
		text = extractor.getText()
	else:
		text = u''
	parent_child_check(text, "t3_" + post[0], post[5])

	if progress % 5 == 0:
		print progress
	progress+=1
	#combine memes with rollup function
	if roll_flag == "on":
		meme_combine(excel_data)
		meme_combine_arr = []

	#if meme_dict bigger than certain # of elems, clear bottom half
	max_dict_size = 1000
	if len(excel_data) > max_dict_size:
		#print "start scraping"
	 	# get median val, delete all items in dict that have median or lower values
		val_arr = []
		w = sorted(excel_data.values())
		#print "data2: ", w
		w.sort(key=operator.attrgetter('total_frequency'))
		#print "data3: ", w

		# median = 0
		# if len(w) > 0:
	 # 	if len(w) < 2*max_dict_size:	#find median
	 # 		median = getattr(w[len(w)/2], 'total_frequency')
	 # 		#print "median: ", median
	 # 	else:
	 # 		median = getattr(w[max_dict_size/2], 'total_frequency')	#prevents dict from getting to be very large


	 	excel_data = {}
	 	if len(w) < 2*max_dict_size:
			for x in range(len(w)/2, len(w)):	#remove top half of sorted dict all elements in dictionary with value less than or equal to median
		 		excel_data[getattr(w[x], 'text')] = w[x]
		else:
			for x in range(len(w) - max_dict_size/2, len(w)):	#remove more than half of sorted elements. prevents from overflowing dict
		 		excel_data[getattr(w[x], 'text')] = w[x]
	 	#print "done scraping"



sorted_data = sorted(excel_data.values())
sorted_data.sort(key=operator.attrgetter('total_frequency'))
# for item in sorted_data:
# 	print item
table_format(sorted_data)
#print sorted_data



