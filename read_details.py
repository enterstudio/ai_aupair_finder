__author__ = 'richard'

from bs4 import BeautifulSoup as bs
import requests
import sqlite3

import pickle

import sqlalchemy

from creds import creds

from aupair_world import login_page, message_page, negative_messages, aupair_detail_page

import pprint


from sklearn.feature_extraction.text import HashingVectorizer

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from schema import AuPair, Message, engine, dbsession


def read_negative_messages(s):
    return read_messages_from_url(s,negative_messages)

def read_messages_from_url(s,url):
    r = s.get(url)
    soup = bs(r.text)

    message_table = soup.find(id="messageList")

    ret = []
    messages = message_table.find_all(class_="text")
    for me in messages:
        id = int(me.a.attrs["name"])
        print "message id", id
        if dbsession.query(Message).filter(Message.id==id).count() == 0:
            try:
                m = Message.populate_message_from_id(s,id)
                ret.append(m)
                dbsession.add(m)
                dbsession.commit()
            except AttributeError:
                pass
        else:
            m = dbsession.query(Message).filter(Message.id==id).first()
            ret.append(m)
            print "already in database"

    return ret


def read_messages(s):
    return read_messages_from_url(s,message_page)



def read_html(s,id):

    from_web = False

    if from_web:
        pf = open("exampleaupair.pf","wb")
        r = s.get(aupair_detail_page+str(id))
        pickle.dump(r,pf)
        pf.close()
    else:
        pf = open("exampleaupair.pf","rb")
        r = pickle.load(pf)
        pf.close()


    a = AuPair.populate_from_html(r.text)

  #  print a
   # print a.features()

    return a

#    with requests.Session() as s:
#        s.post(login_page, data=creds)
#        a2 = AuPair.populate_from_id(s,2511347)
#        print a2

  #  v = HashingVectorizer([all_text])

 #   print v



    pass


#def login(s):

def get_categories():
    return ["yes","no"]


def read_mail():
    with requests.Session() as s:
        s.post(login_page, data=creds)
        r = s.get('https://www.aupair-world.net/my_aupair_world/messages')
        print read_negative_messages(s)

if __name__ == "__main__":

    engine = create_engine('sqlite:///aupairs.db',echo=True)
    Session = sessionmaker()
    Session.configure(bind=engine)
    dbsession = Session()

    Base.metadata.create_all(engine)

    with requests.Session() as s:
        s.post(login_page, data=creds)


        a = AuPair.populate_from_id(s,2470232)
        print a

        pos_messages = read_messages(s)
        neg_messages = read_negative_messages(s)


        good_texts = []
        bad_texts = []

        for p in pos_messages:
            if not dbsession.query(AuPair).filter(AuPair.id == p.sender_id).count():
                a = AuPair.populate_from_id(s,p.sender_id)
                a.category="active"
                print "**** Adding"
                try:
                    print a
                except UnicodeEncodeError:
                    pass
                dbsession.add(a)
                dbsession.commit()

            good_texts.append(a.features())

        for p in neg_messages:
            if not dbsession.query(AuPair).filter(AuPair.id == p.sender_id).count():
                a = AuPair.populate_from_id(s,p.sender_id)
                if a.category == None:
                    a.category = "reject"
                if "inactive" in a.category:
                    a.name = p.sender
                else:
                    a.category = "reject"
                try:
                    print "**** Adding"
                    print a
                except UnicodeEncodeError:
                    print "decode error"
                dbsession.add(a)
                dbsession.commit()
                bad_texts.append(a.features())




        print bad_texts




