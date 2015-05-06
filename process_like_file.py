__author__ = 'richard'

from schema import AuPair

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import requests
from aupair_world import login_page
from creds import creds


if __name__ == "__main__":

    engine = create_engine('sqlite:///aupairs.db')
    Session = sessionmaker()
    Session.configure(bind=engine)
    dbsession = Session()

    with requests.Session() as s:
        s.post(login_page, data=creds)

        lf = "likefile.txt"

        with open(lf) as f:
            print f
            for l in f:
                l = l.rstrip()
            #    print l
                a = l.split("/")
             #   print a

                like_dislike = a[1]
                aupair_id = int(a[2])


                if len(like_dislike) and aupair_id != 0:

                    if aupair_id == 2427155:
                        pass

                    a = AuPair.populate_from_db_or_web(dbsession,aupair_id)

                    if not a.category:

                        print a.name , like_dislike

                        if like_dislike == "like":
                            a.category = "active"

                        if like_dislike == "dislike":
                            a.category = "reject"

                        dbsession.add(a)
                        dbsession.commit()