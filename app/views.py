from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.utils import simplejson
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import auth
from google.appengine.api import images 
from google.appengine.ext import db
from django.template.defaultfilters import slugify
from models import Employee ,Trend

import nltk
from nltk.probability import FreqDist, ELEProbDist
from nltk.classify.util import apply_features,accuracy
import logging as log
from datetime import datetime
from classifier.bayes import BayesianClassifier
from classifier.nltksent import SentimentAnalyzer
from twitter import *
from django.utils import simplejson as json
import urllib, urllib2
import xml.etree.ElementTree as ET
import data.db as db
from google.appengine.api import memcache
from BeautifulSoup import BeautifulSoup
from google.appengine.api import urlfetch

import os, sys, datetime, copy, logging, settings
import datetime


stopSet = set(['yahoo!', 'an', 'a', 'the' ,'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])

def check_word(  word ):

		if word in stopSet \
			or len(word) < 3 \
			or word[0] == "@" \
			or word[0] == "&" \
			or word[0] == "#" \
			or word[:4] == "http":
				return False
		else:
			return True



# Change everything in this! Makes things pretty fast and easy
# so the basic info about the site is ubiquitous. 
class globvars():
  pages = [
      {'name':'Home', 'url':'../../'}, #Make a "the elements" section
      {'name':'About', 'url':'../../about'}, #Make a Contact section here
      {'name':'NLTK Bayes Classifier ', 'url':'../../nltksentiment'}, #Make a Contact section here
      {'name':'Bayes Classifier ', 'url':'../../twitgraph'}, #Make a Contact section here
      {'name':'Most Frequent  Words ', 'url':'../../mostfrequent/?q=google'} #Make a Contact section here

    ]
  proj_name = "Hot Trends"
  founders = [
    {'name':'Alex Rattray',
       'email':'rattray@wharton.upenn.edu',
       'url':'',
       'blurb':'I\'m Alex. I like webdev and most things Seattle.',
       'picture':'http://profile.ak.fbcdn.net/hprofile-ak-ash2/273392_515004220_1419119046_n.jpg'},
    {'name':'Greg Terrono',
       'email':'gterrono@seas.upenn.edu',
       'url':'',
       'blurb':'I\'m Greg. I like webdev and most things Boston. (??)',
       'picture':'http://chucknorri.com/wp-content/uploads/2011/03/Chuck-Norris-14.jpg'},
    ]
  proj_description = "Sentiment analysis of trending topics."
  context = {
      'pages': pages,
      'proj_name': proj_name,
      'founders': founders,
      'proj_description': proj_description,
      }
  
def index(request):
  e = Employee(name="John",
               role="manager",
               email='mick@gus.edu')
  e.hire_date = datetime.datetime.now().date()
  #e.put()
  day1 = datetime.timedelta(days=1)
  trendslist=[]
  gtrendslist=[]
  yesterday = datetime.date.today()-day1
  query = Trend.all().filter('created >= ', yesterday).order('-created')
  results = query.fetch(100)
  for p in results:
    trendslist.append(p.title)
 
  
        
  gv = globvars
  context = {
    'thispage':'Home',
    'trends':trendslist,
    'gtrends':gtrendslist,
      }
  context = dict(context, **gv.context) #combines the 'local' context with the 'global' context
  return render_to_response('index.html', context)

def about(request):
  gv = globvars
  context = {
    'thispage':'About'
      }
  context = dict(context, **gv.context)
  return render_to_response('about.html', context)


def load(request):
  ###load twitter ####
  
  url = "http://api.twitter.com/1/trends/2450022.json"
  req = urllib2.Request(url)
  req.add_header('User-Agent', 'Safari 3.2')
  response = urllib2.urlopen(req)
  output_json = json.load(response)
  for x in output_json:
      for y in x['trends']:
         s = Trend.get_or_insert(y['name'], title=y['name'],source="twitter")




  ###laod Google ####
  gurl = "http://www.google.com/trends/hottrends/atom/hourly"
  data =urllib2.urlopen(gurl)

  tree = ET.parse(data)
  root = tree.getroot()
     

  for child in root:      
        grandchildren = child.getchildren() 
        for grandchild in grandchildren:
            if grandchild.text:           
             soup = BeautifulSoup(grandchild.text)
             hottrends = []          
             for ht in soup('li'):
                  gkeyword = ht.a.string
                  s = Trend.get_or_insert(gkeyword, title=str(gkeyword),source="google")
                  


  return HttpResponse("loaded twitter and google") 



def mostfrequent(request):
     query='Google'
     if(request.GET.has_key('q')):
        query = request.GET['q']    

     search = urllib.urlopen("http://search.twitter.com/search.json?result_type=recent&rpp=100&lang=en&q="+query)
     dict = simplejson.loads(search.read())
     tweetstring = " "
     newlin=" "
     for result in dict["results"]: # result is a list of dictionaries
         try:
           #print " ",result["text"],"\n"    
           positive = "".join(word[:] for word in result["text"].lower()).split()
           for word in positive: 
              if check_word( word ):
               newlin+=word+" "
           tweetstring+= newlin
           
         except UnicodeEncodeError:
             pass
             
     words = [w for w in tweetstring.split()]
     freq_dist = nltk.FreqDist(words)

     tokens = freq_dist.keys()

     #50 most frequent
     most_frequent = tokens[:50]
     responsetext= most_frequent[0] +"   --- "+most_frequent[1]  +"   --- "+most_frequent[2] +"   --- "+most_frequent[3]  +"   --- "+most_frequent[4] \
     +"   --- "+most_frequent[5] +"   --- "+most_frequent[6] +"   --- "+most_frequent[7]  +"   --- "+most_frequent[8] +"   --- "+most_frequent[9] \
     +"   --- "+most_frequent[10] +"   --- "+most_frequent[11]+"   --- "+most_frequent[12]
     return HttpResponse(responsetext) 






def resources(request):
  gv = globvars
  context = {
    'thispage':'More Resources'
      }
  context = dict(context, **gv.context)
  return render_to_response('resources.html', context)

def tutorial(request):
  gv = globvars
  context = {
    'thispage':'Setup Tutorial'
      }
  context = dict(context, **gv.context)
  return render_to_response('tutorial.html', context)

def guestbook(request):
  gv = globvars
  context = {
    'thispage': 'Sample Guestbook App'
    }
  context = dict(context, **gv.context)
  return render_to_response('guestbook.html', context)

def django(request):
  gv = globvars
  context = {
    'thispage': 'Django Tutorial'
    }
  context = dict(context, **gv.context)
  return render_to_response('django.html', context)


def nltkshow(request):
    
    def get_words_in_tweets(tweets):
        all_words = []
        for (words, sentiment) in tweets:
          all_words.extend(words)
        return all_words
        
    def get_word_features(wordlist):
        wordlist = FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features

     
    pos_tweets=[('I love this car','positive'), 
    ('This view is amazing','positive'),
    ('I feel great this morning','positive'),
    ('I am so excited about the concert','positive'),
    ('He is my best friend','positive')]

    neg_tweets=[('I do not like this car','negative'),
    ('This view is horrible','negative'),
    ('I feel tired this morning','negative'),
    ('I am not looking forward to the concert','negative'),
    ('He is my enemy','negative')]
    
    tweets=[]
    for(words,sentiment)in pos_tweets+neg_tweets:
      words_filtered=[e.lower() for e in words.split() if len(e)>=3]
      tweets.append((words_filtered,sentiment))

    test_pos_tweets=[('I feel happy this morning','positive'), 
    ('Larry is my friend','positive')]

    test_neg_tweets=[('I do not like that man','negative'),
    ('This view is horrible','negative'),
    ('The house is not great','negative'),
    ('Your song is annoying','negative')]

    test_tweets=[]
    for(test_words,test_sentiment)in test_pos_tweets+test_neg_tweets:
      test_words_filtered=[e.lower() for e in test_words.split() if len(e)>=3]
      test_tweets.append((test_words_filtered,test_sentiment))
      
       
    word_features = get_word_features(get_words_in_tweets(tweets))

    def extract_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
          features['contains(%s)' % word] = (word in document_words)
        return features   
        
    training_set = apply_features(extract_features, tweets)

    test_training_set=apply_features(extract_features, test_tweets)
     
    classifier = nltk.classify.NaiveBayesClassifier.train(training_set)
    
    tweet = 'Your song is horrible'
    clas= classifier.classify(extract_features(tweet.split()))
    '''  
    classifier.show_most_informative_features(5)

    + clas +"    "+ class2
    class2 nltk.classify.util.accuracy(classifier,test_training_set)
    '''
    now = datetime.datetime.now()
    html = clas + "<html><body>It is 555 now %s.</body></html>" % now
    
    return HttpResponse(html)



def twitgraph(request):    
    bayesname='bayesdata'
    srch = 'happy'
    tag = 'n'
    c = BayesianClassifier()
    if not memcache.get('bayesdata'):       
        c.save()#laod form local file system
    c.load()#load picke from memecache
    '''q=request.get_all("q")'''
    if(request.GET.has_key('q')):
        srch = request.GET['q']    

    tag = c.classify(srch)
    html =  "<html><body>sentiment is %s </body></html>"  % tag
    #return HttpResponse(html)
    gv = globvars
    context = {
      'thispage':'Sentiment',
       'the_tweet':srch,
       'sentmnt':tag
        }
    context = dict(context, **gv.context)
    return render_to_response('sentiment.html', context)
  
 
 
def nltksentiment(request): 
    srch = 'happy'
    if(request.GET.has_key('q')):
        srch = request.GET['q']    

    analyzer = SentimentAnalyzer()
    result = analyzer.analyzetweet( srch)   
    gv = globvars
    context = {
      'thispage':'Sentiment',
       'the_tweet':srch,
       'sentmnt':result
        }
    context = dict(context, **gv.context)
    return render_to_response('sentiment.html', context)
 
  
    
