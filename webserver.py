__author__ = 'richard'

import SimpleHTTPServer
import SocketServer

PORT = 8000

from schema import AuPair

like_file = "likefile.txt"
lf = open(like_file,"a")

classifier,vectorizer = AuPair.get_classifier_vectorizer()

print classifier
print vectorizer

def classify(server,aupair_id):
    print aupair_id
    (a,r) = AuPair.get_rating(aupair_id,classifier,vectorizer)
    server.send_response(200)
    server.send_header('Content-type','text/html')
    server.end_headers()
    ret = ""
    for cat in r:
        ret += " %s -> %.2f %% <br>" % ( cat, r[cat] )
    server.wfile.write(ret)


class MyServerRH(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        print "IN GET!"
        print self.path
        path = self.path.split("/")

        if path[1] == "classify":
            return classify(self,path[2])
        lf.write(self.path+"\n")
        lf.flush()
        #print self.
        self.send_response(200)

httpd = SocketServer.TCPServer(("", PORT), MyServerRH)

print "serving at port", PORT
httpd.serve_forever()