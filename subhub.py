import sublime, sublime_plugin;
import time, os.path, json, threading, sys
import subprocess
from os.path import expanduser
from threading import Thread
import json
import re
import signal

try:
  import BaseHTTPServer
except ImportError:
  import http.server as BaseHTTPServer
  
CACHE_DIR = expanduser("~") + '/.subhub'
PORT      = 48666
def open(directory):
  if sublime.platform() == 'windows':
    subprocess.Popen([sublime.executable_path(), '.'], cwd=directory, shell=True)
  else:
    subprocess.call([os.path.join(os.path.dirname(sublime.executable_path()), '../SharedSupport/bin/subl'), directory])

def clone(url):
  print('Cloning ' + url)
  m = re.search('.*github.com[\/|:]([^\/]+)\/([^\/|\.]+)', url)
  user = m.group(1)
  repo = m.group(2)
  
  local_repo = CACHE_DIR + '/' + user + '/' + repo

  if not os.path.isdir(local_repo):
    subprocess.call(['mkdir', '-p', CACHE_DIR + '/' + user])
    
    if sublime.platform() == 'windows':
      subprocess.call(['git', 'clone', "https://github.com/"+ user +"/" + repo + ".git", local_repo, '--depth', '1'])
    else:
      subprocess.call(['git', 'clone', url, local_repo, '--depth', '1'])
  
  else: 
    settings = sublime.load_settings("subhub.sublime-settings")
    if settings.get('if_exists') == 'pull':
      process = subprocess.Popen(['git', 'pull'], cwd=local_repo, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      stdout = [x.decode('unicode_escape').rstrip() for x in process.stdout.readlines()]
      print(stdout)
    print('Repository is already checked out')

  return local_repo

class ConnectionHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def do_GET(self):
    print('Received: heartbeat1')
    self.send_response(200)
    self.send_header('Content-type',  'application/json')
    self.send_header('Access-Control-Allow-Origin',  '*')    
    self.end_headers()
    

    return

  def do_POST(self):
    self.data_string = self.rfile.read(int(self.headers['Content-Length']))
    self.send_response(201)    
    self.send_header('Content-type',  'application/json')    
    self.send_header('Access-Control-Allow-Origin',  '*')    
    self.end_headers()
    data = json.loads(self.data_string.decode("utf-8"))
    open(clone(data['url']))

    return

print("Staring subhub server on port " + str(PORT))

server = BaseHTTPServer.HTTPServer(('', PORT), ConnectionHandler)
Thread(target=server.serve_forever).start()

def plugin_unloaded():
  print("Closing subhub server")
  server.shutdown()
  server.server_close()
  
#curl -X POST -H "Content-Type: application/json" -d '{"url":"https://github.com/nodejitsu/nssocket"}' http://localhost:48666
