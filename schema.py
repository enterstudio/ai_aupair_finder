__author__ = 'richard'


from aupair_world import message_detail,aupair_detail_page,login_page

import unicodedata

comment_paragraphs = ["Dear Family","About me","Why do you want to be an au pair? "]

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, ForeignKey

Base = declarative_base()
from bs4 import BeautifulSoup as bs

from creds import creds
import requests

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import or_

from aupair_world import aupair_detail_page

engine = None
dbsession = None

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
#from sklearn.naive_bayes import BernoulliNB, MultinomialNB
from sklearn.linear_model import LogisticRegression


engine = create_engine('sqlite:///aupairs.db',echo=True)
Session = sessionmaker()
Session.configure(bind=engine)
dbsession = Session()

class AuPair(Base):
    __tablename__ = "aupair"

    id = Column(Integer,primary_key=True)
    name = Column(String)
    nationality = Column(String)
    sex = Column(String)
    all_text = Column(String)
    previous_experience = Column(String)
    age = Column(Integer)
    category = Column(String)
    messages = relationship("Message",backref="aupair")

    @property
    def link(self):
        return aupair_detail_page + str(self.id)

    @classmethod
    def populate_from_db_or_web(cls,dbsession,id):
        a = AuPair.populate_from_db(dbsession,id)
        if a:
            return a
        else:
            with requests.Session() as s:
                s.post(login_page, data=creds)
                a = AuPair.populate_from_id(s,id)
                dbsession.add(a)
                dbsession.commit()
                return a

    @classmethod
    def populate_from_db(cls,dbsession,id):
        return dbsession.query(AuPair).filter(AuPair.id == id).first()

    @classmethod
    def populate_from_id(cls,session,id):
        r = session.get(aupair_detail_page+str(id))
        return AuPair.populate_from_html(r.text)

    def __repr__(self):
        return unicodedata.normalize("NFKD",u"<AuPair " + ", ".join("%s: %s".encode('ascii','ignore') % item for item in vars(self).items() if item[0] != "all_text") +">").encode('ascii', 'ignore')

    @property
    def features(self):
        #ret = " " .join("%s=%s" % item for item in vars(self).items() if item[0] != "all_text")
        return self.all_text + " previous_experience_%s" %( self.previous_experience ) + " nationality_%s" % ( self.nationality)

    @classmethod
    def populate_from_html(cls,html_text):
        a = AuPair()

        soup = bs(html_text)

        if soup.find("h3") and "Profile not active at the moment" in soup.find("h3").text:
            a.category = "inactive"
            return a

        metadata = {"Name":"name","Nationality":"nationality","Previous au pair experience":"previous_experience","Profile number":"id"}
        class_search = {"aupair_age":"age","gender":"sex"}

        profile_tab = soup.find(id="profileTab")
        letters_tab = soup.find(id="lettersTab")


        if profile_tab:
            for m in metadata:
                th = profile_tab.find('th',text=m)
                if th:
                    td =  th.findNext('td')
                    #print "%s -> %s" %(m,td.text)
                    setattr(a,metadata[m],td.text)
                else:
                    pass
                 #   print "%s -> :-(" %(m)


            for cs in class_search:
                val = profile_tab.find(class_ = cs).text
               # print "%s -> %s" %(class_search[cs],val )
                setattr(a,class_search[cs],val)

        all_text = ""

        comments = comment_paragraphs

        if letters_tab:

            for c in comments:
                th = letters_tab.find('h3',text=c)
                if th:
                    td =  th.findNext('p')
                  #  print "%s -> %s" %(c,td.text)
                    all_text = all_text + td.text
                else:
                    pass
                #    print "%s -> :-(" %(c)

        a.all_text = all_text

        return a

    def __init__(self):
        pass


    @classmethod
    def get_classifier_vectorizer(cls):
        aupairs = dbsession.query(AuPair).filter(or_(AuPair.category=="active",AuPair.category=="reject",AuPair.category=="crazy",AuPair.category=="not_english"))
        all_text = [(a.features, a.category) for a in aupairs]
        vectorizer = CountVectorizer(stop_words='english',ngram_range=(1,4))
        #vectorizer = TfidfVectorizer(min_df=2)
        X_train = vectorizer.fit_transform([x[0] for x in all_text])
        y_train = ([x[1] for x in all_text])
        classifier = LogisticRegression()
        classifier.fit(X_train,y_train)
        print("Training score: {0:.1f}%".format(classifier.score(X_train, y_train) * 100))
        return classifier,vectorizer



    @classmethod
    def get_rating(cls,aupair_id,classifier,vectorizer):
        a  = AuPair.populate_from_db_or_web(dbsession,aupair_id)
        t_form = vectorizer.transform([a.features])
        probs = classifier.predict_proba(t_form)
        ret_probs = {}
        for i,p in enumerate(probs[0]):
            print "# ", classifier.classes_[i] , "%.2f %%" % (p*100)
            ret_probs[classifier.classes_[i]] = p*100

        print a.name, "-->" , classifier.predict(t_form[0])[0] # , [(classifier.classes_[i], [0][i]) for i in range(len(classifier.classes_))]

        return (a,ret_probs)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer,primary_key=True)
    text = Column(String)
    sender = Column(String)
    sender_id = Column(Integer,ForeignKey('aupair.id'))


    def __init__(self,**kwargs):
        self.sender_id = None
        self.text = None
        self.sender = None
        for k in kwargs:
            setattr(self,k,kwargs[k])

    @classmethod
    def populate_message_from_id(cls,session,id):
        r = session.get(message_detail+str(id))
        #print r.text
        soup = bs(r.text)
        message = soup.find(id="msSingle")

        thread = message.find(id="thread")
        sender = thread.a.text
        sender_id = int(thread.a.attrs["href"].split("=")[1])
        email = thread.find(class_="msCustom panel radius typewriter").text


        print id,"-->", sender_id, "(" , sender, ")"
    #    print "-----------------------------------------------------------"
    #    print email.replace("\r","\n")
    #    print "-----------------------------------------------------------"

        email = email.replace("\r","\n").encode('ascii', 'ignore')

        mes = Message(sender_id=sender_id,text=email,sender=sender, id = id)

        return mes

    def __repr__(self):
        print str("<Message %s - %s>" % (self.sender_id, str(self.text.replace("\r","\n"))))


if __name__ == "__main__":
    Base.metadata.create_all(engine)