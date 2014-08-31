__author__ = 'richard'

from bs4 import BeautifulSoup as bs
import requests

import pickle

import sqlalchemy

creds = {"userid":"richardagreen@gmail.com","password":"piersermisse","login":"Login"}

login_page = "https://www.aupair-world.net/login"

base_page = "https://www.aupair-world.net/aupair_detail?a="
import pprint
#message_page = "https://www.aupair-world.net/my_aupair_world/messages"
message_page = "https://www.aupair-world.net/my_aupair_world/messages?&voption[count_option]=100&page=1&box=1"
message_detail = "https://www.aupair-world.net/my_aupair_world/messages/msg?id="

negative_messages = "https://www.aupair-world.net/my_aupair_world/messages?&voption[count_option]=100&page=1&box=3"
negative_messages = "https://www.aupair-world.net/my_aupair_world/messages?&voption[count_option]=5&page=1&box=3"




from sklearn.feature_extraction.text import HashingVectorizer

class AuPair(object):
    @classmethod
    def populate_from_id(cls,session,id):
        pass

    @classmethod
    def populate_from_html(cls,html_text):

        soup = bs(html_text)

        metadata = {"Name":"name","Nationality":"nationality","Previous au pair experience":"previous_experience"}
        class_search = {"aupair_age":"age","gender":"sex"}

        profile_tab = soup.find(id="profileTab")
        letters_tab = soup.find(id="lettersTab")

        a = AuPair()

        for m in metadata:
            th = profile_tab.find('th',text=m)
            if th:
                td =  th.findNext('td')
                print "%s -> %s" %(m,td.text)
            else:
                print "%s -> :-(" %(m)


        for cs in class_search:
            val = profile_tab.find(class_ = cs).text
            print "%s -> %s" %(class_search[cs],val )



        all_text = ""

        comments = ["Dear Family","About me","Why do you want to be an au pair? "]

        for c in comments:
            th = letters_tab.find('h3',text=c)
            if th:
                td =  th.findNext('p')
                print "%s -> %s" %(c,td.text)
                all_text = all_text + td.text
            else:
                print "%s -> :-(" %(c)


        return a


    def __init__(self):
        pass


class Message(object):
    def __init__(self,**kwargs):
        self.sender_id = None
        self.text = None
        for k in kwargs:
            setattr(self,k,kwargs[k])

    def __repr__(self):
        print "<Message %s - %s>" % (self.sender_id, str(self.text.replace("\r","\n")))



def read_negative_messages(s):
    r = s.get(negative_messages)
    soup = bs(r.text)

    message_table = soup.find(id="messageList")

    ret = []
    messages = message_table.find_all(class_="text")
    for me in messages:
        ret.append(int(me.a.attrs["name"]))

    pprint.pprint(get_messages_from_id(s,ret))



def get_messages_from_id(s,id_list):
    ret = []
    for m in id_list:
        r = s.get(message_detail+str(m))
        #print r.text
        soup = bs(r.text)
        message = soup.find(id="msSingle")

        thread = message.find(id="thread")
        sender = thread.a.text
        sender_id = thread.a.attrs["href"].split("=")[1]
        email = thread.find(class_="msCustom panel radius typewriter").text


        print m,"-->", sender_id, "(" , sender, ")"
    #    print "-----------------------------------------------------------"
    #    print email.replace("\r","\n")
    #    print "-----------------------------------------------------------"

        mes = Message(sender_id=sender_id,text=email)

        ret.append(mes)


    return ret


def read_messages(s):
    r = s.get(message_page)
    soup = bs(r.text)

    message_table = soup.find(id="messageList")

    ret = []
    messages = message_table.find_all(class_="text")
    for me in messages:
        ret.append(int(me.a.attrs["name"]))

    get_messages_from_id(s,ret)




def read_html(s,id):


    from_web = False

    if from_web:
        pf = open("exampleaupair.pf","wb")
        r = s.get(base_page+str(id))
        pickle.dump(r,pf)
        pf.close()
    else:
        pf = open("exampleaupair.pf","rb")
        r = pickle.load(pf)
        pf.close()


    a = AuPair.populate_from_html(r.text)

    print a

  #  v = HashingVectorizer([all_text])

 #   print v



    pass


#def login(s):

def get_categories():
    return ["yes","no"]





if __name__ == "__main__":


    with requests.Session() as s:
        s.post(login_page, data=creds)
        # print the html returned or something more intelligent to see if it's a successful login page.
  #      print s

        # An authorised request.
        r = s.get('https://www.aupair-world.net/my_aupair_world/messages')
#        print r.text
#        print "------"
            # etc...

        #
        #print read_messages(s)
        print read_negative_messages(s)
        #print read_html(s,2525313)