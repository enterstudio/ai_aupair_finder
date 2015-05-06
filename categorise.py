__author__ = 'richard'

from bs4 import BeautifulSoup as bs
import requests
import sqlite3
import pickle
import sqlalchemy
import pprint

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.linear_model import LogisticRegression

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import or_
from schema import AuPair, Message, engine, dbsession

from creds import creds

engine = create_engine('sqlite:///aupairs.db',echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
dbsession = Session()

from aupair_world import easy_find, login_page,easy_find_n, easy_find_ll_n
from bs4 import BeautifulSoup as bs

import requests
import pprint

def get_relevant_aupairs():
    ret = []
    with requests.Session() as s:
        s.post(login_page, data=creds)

        for i in range(1,50):
            print "Getting page",i
            #r = s.get(easy_find_n+str(i))
            r = s.get(easy_find_ll_n+str(i))
            soup = bs(r.text)
            aupairs=soup.find_all("a",class_="th")
            for a in aupairs:
                link = a.attrs["href"]
                id = int(link[link.index("a=")+2:link.index("#")])
                ret.append(id)

    return ret



def get_rating(aupair_id,classifier,vectorizer):
    a  = AuPair.populate_from_db_or_web(dbsession,aupair_id)

  #   a  = AuPair.populate_from_db(dbsession,2514118) #
#    print a

    #sample_text= """Hello, My name is Rael Nyandoro, am aged 26 and i currently live in Nairobi, Kenya. I could like to stay with my host family for a period of 6 to 12months. I have a mature approach to life and am able to carry out day to day housework comfortably. I could like to get involved in the family activities fully as part of the family member. Thank you for taking your time to go through my profile and i look forward to hear from you soon.I am a very friendly and smiley person, i respect and understand people's needs especially children. Am very good when it comes to taking care of children. My hobbies are cooking, reading, making friends and nature walk. I would like to work as an au pair because i want to improve my language skills and learn a new culture. I also have plans to pursue my studies abroad, so this will be a stepping stone to achieving my future goals. """

    sample_text = a.features

    t_form = vectorizer.transform([sample_text])

  #  print classifier.classes_
 #   print classifier.predict_proba(t_form)

    probs = classifier.predict_proba(t_form)
    ret_probs = {}
    for i,p in enumerate(probs[0]):
        print "# ", classifier.classes_[i] , "%.2f %%" % (p*100)
        ret_probs[classifier.classes_[i]] = p*100

    print a.name, "-->" , classifier.predict(t_form[0])[0] # , [(classifier.classes_[i], [0][i]) for i in range(len(classifier.classes_))]

    return (a,ret_probs)


def get_classifier_vectorizer():
    aupairs = dbsession.query(AuPair).filter(or_(AuPair.category=="active",AuPair.category=="reject",AuPair.category=="crazy",AuPair.category=="not_english"))
    #bad_aupairs =  dbsession.query(AuPair).filter(AuPair.category == "reject")

    all_text = [(a.features, a.category) for a in aupairs]

  #  pprint.pprint( all_text )

    #good_text = [a.all_text for a in good_aupairs]
    #bad_text = [a.all_text for a in bad_aupairs]

   # vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5, stop_words='english',ngram_range=(1,3))
    #vectorizer = CountVectorizer(stop_words='english',ngram_range=(1,3))
    vectorizer = TfidfVectorizer(min_df=2,ngram_range=(1,4), stop_words='english')

    X_train = vectorizer.fit_transform([x[0] for x in all_text])
    y_train = ([x[1] for x in all_text])

    #print X_train,y_train

    #classifier = MultinomialNB()
    classifier = LogisticRegression()
    classifier.fit(X_train,y_train)

    print("Training score: {0:.1f}%".format(classifier.score(X_train, y_train) * 100))

    return (classifier,vectorizer)


def trim(s):
    """Trim string to fit on terminal (assuming 80-column display)"""
    return s if len(s) <= 200 else s[:177] + "..."

if __name__ == "__main__":



    (classifier,vectorizer)= get_classifier_vectorizer()

    categories = classifier.classes_

    feature_names = np.asarray(vectorizer.get_feature_names())

    n = 20

    print("top %s keywords per class:" %( n ))

    for i, category in enumerate(categories):
        top10 = np.argsort(classifier.coef_[i])[-n:]
        print(trim("%s: %s"
              % (category, ", ".join(feature_names[top10]))))


    aupair_ids = get_relevant_aupairs()

    #print aupair_ids

    all_aupairs = []

    for a in aupair_ids:
        ratings = get_rating(a,classifier,vectorizer)
        all_aupairs.append(ratings)

    for category in categories:

        ordered = sorted(all_aupairs,key=lambda s:-s[1][category])

        print " **", category

        for i in range(0,100):
            ap = ordered[i][0]
            if not ap.category:
                print "*",
                print ap.name,  ap.category, ap.link,  ordered[i][1][category]

   # print vectorizer.get_feature_names()

  #  print classifier.predict([])

    #print vectorizer
    #print X_train