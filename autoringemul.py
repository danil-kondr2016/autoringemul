#!/usr/bin/env python3

from datetime import datetime
from wsgiref.util import request_uri
from wsgiref.simple_server import make_server

from cgi import FieldStorage
from urllib.parse import parse_qs

# Constants

MAX_LESSONS = 15
MAX_POST = 2048

# Variables

time_d = 0
n_lessons = 10
schedule = [
  [510, 555, 0],
  [565, 610, 0],
  [630, 675, 0],
  [695, 740, 0],
  [755, 800, 0],
  [810, 855, 0],
  [865, 910, 0],
  [930, 975, 0],
  [985, 1030, 0],
  [1040, 1085, 0],
  [1440, 1485, 0],
  [1440, 1485, 0],
  [1440, 1485, 0],
  [1440, 1485, 0],
  [1440, 1485, 0]
]

pwdhash = ''
pwdsalt = ''

def get_time():
  global time_d
  t = datetime.now()
  return (t.hour * 3600 + t.minute * 60 + t.second + time_d) % 86400

def set_time(h, m, s):
  global time_d
  t_old = get_time()
  t_new = (h * 3600 + m * 60 + s) % 86400
  time_d += (t_new - t_old)
  time_d %= 86400

def schedule_str():
  global schedule
  result = []
  for i in range(n_lessons):
    result.append('{0}-{1}.{2}.{3}'.format(i+1, *schedule[i]))
  return '_'.join(result) + '_'

def parse_schedule(s):
  global schedule, n_lessons
  a = [xa for xa in s.split('_') if xa != '']
  print(a)
  for xa in a:
    bs = xa.split('-')
    ln = int(bs[0]) - 1
    if (ln > MAX_LESSONS):
      break
    print(bs, ln)
    ls = list(map(int, bs[1].split('.')))
    schedule[ln] = ls
  n_lessons = len(a)
  if n_lessons > MAX_LESSONS:
    n_lessons = MAX_LESSONS

def app(environ, start_response):
  global schedule, n_lessons, pwdhash, pwdsalt

  answer = []
  answer_headers = [('Content-Type', 'text/plain')]

  uri = request_uri(environ)
  print(uri)

  q_str = None
  if environ['REQUEST_METHOD'] == 'GET':
    q_str = environ['QUERY_STRING']
  elif environ['REQUEST_METHOD'] == 'POST':
    content_len = int(environ.get('CONTENT_LENGTH', str(MAX_POST)))
    if content_len >= MAX_POST:
      content_len = MAX_POST
    q_str = environ['wsgi.input'].read(content_len)

  if (isinstance(q_str, bytes)):
    q_str = q_str.decode('utf-8')

  form = parse_qs(q_str)
  print(form)

  method = ''.join(form['method']).strip()
  if method == 'set':
    for x in form:
      if x == 'method':
        continue
      if x == 'schedule':
        parse_schedule(form[x][0])
      elif x == 'lessnum':
        n_lessons = int(form[x][0])
      elif x == 'time':
        h,m,s = map(int, form[x][0].split(':'))
        set_time(h, m, s)
      elif x == 'passwd':
        pwdhash = form[x]
      elif x == 'pwdsalt':
        pwdsalt = form[x]
  elif method == 'schedule':
    answer.append('lessnum=' + str(n_lessons))
    answer.append('schedule=' + schedule_str())
  elif method == 'doring':
    print('ring')
  elif method == 'password':
    answer.append('pwdhash=' + pwdhash)
    answer.append('pwdsalt=' + pwdsalt)

  answer.append('state=0')
  start_response("200 OK", answer_headers)
  return ['&'.join(answer).encode('utf-8')]


with make_server('', 8000, app) as httpd:
  httpd.serve_forever()

