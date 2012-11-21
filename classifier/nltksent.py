#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf-8 -*-
"""
sentiment_analyzer.py

Created by Elvar Orn Unnthorsson on 07-12-2011
Copyright (c) 2011 ellioman inc. All rights reserved.
"""

import sys
import os
import nltk
from nltk.classify import NaiveBayesClassifier
import codecs
import re
import cPickle
import pickle
from google.appengine.api import memcache
from nltk.probability import FreqDist, ELEProbDist
from nltk.classify.util import apply_features,accuracy
import random

MEMCACHE_MAX_ITEM_SIZE = 900 * 1024


def setmeme(key, value):
  pickled_value = pickle.dumps(value)

  # delete previous entity with the given key
  # in order to conserve available memcache space.
  #delete(key)

  pickled_value_size = len(pickled_value)
  chunk_keys = []
  for pos in range(0, pickled_value_size, MEMCACHE_MAX_ITEM_SIZE):
    # TODO: use memcache.set_multi() for speedup, but don't forget
    # about batch operation size limit (32Mb currently).
    chunk = pickled_value[pos:pos + MEMCACHE_MAX_ITEM_SIZE]

    # the pos is used for reliable distinction between chunk keys.
    # the random suffix is used as a counter-measure for distinction
    # between different values, which can be simultaneously written
    # under the same key.
    chunk_key = '%s%d%d' % (key, pos, random.getrandbits(31))

    is_success = memcache.set(chunk_key, chunk)
    if not is_success:
      return False
    chunk_keys.append(chunk_key)
  return memcache.set(key, chunk_keys)
  
def getmeme(key):
  chunk_keys = memcache.get(key)
  if chunk_keys is None:
    return None
  chunks = []
  for chunk_key in chunk_keys:
    # TODO: use memcache.get_multi() for speedup.
    # Don't forget about the batch operation size limit (currently 32Mb).
    chunk = memcache.get(chunk_key)
    if chunk is None:
      return None
    chunks.append(chunk)
  pickled_value = ''.join(chunks)
  try:
    return pickle.loads(pickled_value)
  except Exception:
    return None  
    


class SentimentAnalyzer:
	
	"""
	SentimentAnalyzer trains a Naive Bayes classifier so that it can determine whether a tweet
	is positive, negative or neutral. It uses training data that was manually categorized by
	the author. The analyze function should be used to classify a list of tweets to analyze.
	"""
	
	def __init__( self ):
		"""
		Constructs a new SentimentAnalyzer instance.
		"""		
		self.results = { "positive": 0, "negative": 0, "neutral": 0}
		self.data = {}
		self.min_word_length = 3
		
		#self.stopSet = set(stopwords.words('english'))
		self.stopSet = set(['an', 'a', 'the' ,'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

		extra_stopwords = ["he's", "she's", "RT" ]
		for stopword in extra_stopwords: self.stopSet.add( stopword )


		if not memcache.get('nltkclassifier'):
			self.classifier = cPickle.load(open(os.path.join(os.path.dirname(__file__), "my_nltk_classifier.pickle")))
			setmeme('nltkclassifier', self.classifier )

		#if not memcache.get('nltkclassifier'):			
		#self.classifier = cPickle.load(open(os.path.join(os.path.dirname(__file__), "my_nltk_classifier.pickle")))
		#setmem('nltkclassifier', self.classifier )
		self.classifier =getmeme('nltkclassifier')
		
		

		# Naive Bayes initialization
		#self.__init_naive_bayes()




	def analyze(self, data):
		"""
		analyze(self, data):
		Input: data. A list of tweets to analyze.
		Takes a list of tweets and uses sentiment analysis to determine whether 
		each tweet is positive, negative or neutral.
		Return: The tweets list with each tweet categorized with the proper sentiment value.
		"""
		return self.__analyse_using_naive_bayes( data )
	
	def analyzetweet(self, data):
		"""
		analyze(self, data):
		Input: data. A list of tweets to analyze.
		Takes a list of tweets and uses sentiment analysis to determine whether 
		each tweet is positive, negative or neutral.
		Return: The tweets list with each tweet categorized with the proper sentiment value.
		"""
		
		return self.__analyze_tweet( data )
	
	
	
	def get_analysis_result(self, data_to_get):
		"""
		get_analysis_result(self, data_to_get):
		Input: data_to_get. The statistic that the function should get from the results dictionary.
		Gets the count of either positive, negative or neutral from the results dictionary after 
		doing an analysis. 
		Return: The count of positive, negative or positive tweets found during the analysis.
		"""		
		return self.results[data_to_get]




	def __strip_non_ascii(string):
		stripped = (c for c in string if 0 < ord(c) < 127)
		return ''.join(stripped)

	def show_most_informative_features( self, amount ):
		"""
		show_most_informative_features( self, amount ):
		Input: amount. How many features should the function display.
		Displays the most informative features in the classifier used
		to classify each tweet.
		"""		
		self.classifier.show_most_informative_features( amount )	
		
	
	def __check_word( self, word ):
		"""
		__check_word( self, word ):
		Input: word. The word to check.
		Looks at a word and determines whether that should be used in the classifier.
		Return: True if the word should be used, False if not.
		"""
		if word in self.stopSet \
			or len(word) < self.min_word_length \
			or word[0] == "@" \
			or word[0] == "#" \
			or word[:4] == "http":
				return False
		else:
			return True
	
	
	
	def __analyze_tweet(self, tweet):
		"""
		__analyze_tweet(self, tweet):
		Input: tweet. The tweet that should be analyzed.
		Analyses a tweet using the created Naive Bayes classifier.
		Return: The results fromt the classifier. Possible results: 'pos', 'neg' or 'neu'
		"""
		try:
			tweet_features = dict([ (word, True) 
							for word in tweet.lower().split() 
							if self.__check_word( word ) ] )
			return self.classifier.classify( tweet_features )
		
		except:
			raise Exception ("Unknown error in SentimentAnalyzer::__analyze_tweet")
			return 'err'
	
	


