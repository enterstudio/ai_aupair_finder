__author__ = 'richard'

from schema import AuPair


from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import or_
from schema import AuPair, Message, engine, dbsession

engine = create_engine('sqlite:///aupairs.db',echo=False)
Session = sessionmaker()
Session.configure(bind=engine)
dbsession = Session()


if __name__ == "__main__":
    d = r"data_out/"

    aupairs = dbsession.query(AuPair).filter(or_(AuPair.category=="active",AuPair.category=="reject",AuPair.category=="crazy",AuPair.category=="not_english"))

    for a in aupairs:
        with open(d+a.category+"/"+str(a.id)+".txt","w") as f:
            f.write((a.features).encode('utf-8').strip())

        print a
