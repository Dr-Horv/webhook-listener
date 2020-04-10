#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import json
import hmac
import hashlib
import base64
import os
import subprocess

def verify_signature(request):
    request_sig = request.headers.get('X-Hub-Signature')
    if request_sig == None:
        return False
    sig = 'sha1=' + hmac.new(os.environ['GITHUB_SECRET'].encode(), msg=request.body, digestmod=hashlib.sha1).hexdigest()
    print(request_sig)
    print(sig)
    return sig == request_sig

def deploy(project):
    cmd = ''
    if "retro-frontend" in project:
        cmd = './retro-frontend.sh'
    elif "retro-backend" in project:
        cmd = './retro-backend.sh'
    else:
        print("Unsupported project")
        return
    
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    # print(output)
    if error:
        print(error)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("pong")
    
    def post(self):
        valid = verify_signature(self.request)
        if not valid:
            self.send_error(401)
            return
        data = json.loads(self.request.body)
        print(data)
        if data.get('data', {}).get('built'):
            deploy(data['data']['built'])


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    github_secret = os.environ.get('GITHUB_SECRET')
    port = os.environ.get('PORT', 8888)
    if not github_secret:
        print("Please provide GITHUB_SECRET as environment variable")
        exit(1)

    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()