

from flask import Flask ,render_template,request,jsonify
import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import pkg_resources
from symspellpy import SymSpell, Verbosity
from multiprocessing import Value
import urllib.request
import re
from pytube import YouTube
import wikipedia
from transformers import *

import nltk as nltk
from flask_restful import reqparse, abort, Api, Resource



model = PegasusForConditionalGeneration.from_pretrained("tuner007/pegasus_paraphrase")
tokenizer = PegasusTokenizerFast.from_pretrained("tuner007/pegasus_paraphrase")



def get_index_positions(list_of_elems, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    index_pos_list = []
    index_pos = 0
    while True:
        try:
         
            index_pos = list_of_elems.index(element, index_pos)
           
            index_pos_list.append(index_pos)
            index_pos += 1
        except ValueError as e:
            break
    return index_pos_list

def get_paraphrased_sentences(model, tokenizer, sentence, num_return_sequences=5, num_beams=5):

  inputs = tokenizer([sentence], truncation=True, padding="longest", return_tensors="pt")
  outputs = model.generate(
    **inputs,
    num_beams=num_beams,
    num_return_sequences=num_return_sequences,
  )

  return tokenizer.batch_decode(outputs, skip_special_tokens=True)

def sentence(sentence):
    return get_paraphrased_sentences(model, tokenizer, sentence, num_beams=10, num_return_sequences=10)

mgss=[]

class DataStore():
    words=None
    a = None
    b= None
    c = None
    d = None
    e = None
    f = None
    g = None
    h = None 
    i = None
    title = None
    link=None
    duration=None
    description=None
    text=None
    goals=None
    vid= None
    mgs=None
    my_str=None
    my_strr=None
    sens=None
    TODOS=None
data = DataStore()



application = Flask(__name__)
api = Api(application)

def search(search_keyword):
    s=search_keyword.replace(" ", "+")
    urls="https://www.youtube.com/results?search_query=" + s
    ur=str(urls)
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + ur)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    link="https://www.youtube.com/watch?v=" + video_ids[0]
    data.link=link
    yt = YouTube(link)
    title=yt.title
    data.title=title
    Views=yt.views
    Duration=yt.length
    data.duration=Duration
    Description=yt.description
    data.description=Description
    Ratings=yt.rating

def article(text):
    
    wiki = wikipedia.page(text)

  
    text = wiki.content

  
    text = text.replace('==', '')

    text = text.replace('\n', '')[:-12]
    data.text=text

@application.route("/",methods =["GET", "POST"])
def home():
  return render_template("getzing/home.html")

@application.route("/form",methods=["GET", "POST"])
def form():
  mgs=[]
  if request.method=="POST":
    goals= request.form.get("goal")
    data.goals=goals
    data.words="none"
    data.qq="none"
    i_w=sentence(goals)
    forms = {"am" : "are", "are" : "am", 'i' : 'you', 'my' : 'yours', 'me' : 'you', 'mine' : 'yours', 'you' : 'I', 'your' : 'my', 'yours' : 'mine'}
    def translate(word):
      if word.lower() in forms: return forms[word.lower()]
      return word
    ok=i_w[0]
    sent = ok
    result = ' '.join([translate(word) for word in nltk.wordpunct_tokenize(sent)])
    words=result
    data.words=words
    return render_template('getzing/formA.html',words=words)

@application.route("/formA",methods=["GET", "POST"])
def Aform():
  mgs=[]
  if request.method=="POST":
    g= request.form.get("y")
    data.g=g
    if data.g=="no":
      return render_template('getzing/quesion.html')
    if data.g=="yes":
      return render_template('getzing/formC.html')

@application.route("/quesion",methods=["GET", "POST"])
def que():
  if request.method=="POST":
    qq= request.form.get("ques")
    data.qq=qq
    return render_template('getzing/formC.html')

@application.route("/formB",methods=["GET", "POST"])
def Bform():
  mgs=[]
  if request.method=="POST":
    vid= request.form.get("q")
    if vid=="video":
      search(data.my_strr)
      video_Title=data.title
      video_Duration=data.duration
      video_Link=data.link
      return render_template('getzing/formC.html',video_Title=video_Title,video_Duration=video_Duration,video_Link=video_Link)
    if vid=="text":
      try:
        article(data.my_strr)
      except:
        data.text="I can't find an article for this goal"
      wrd=data.text
      return render_template('getzing/formC.html',wrd=wrd)
    if vid=="all":
      search(data.my_strr)
      video_Title=data.title
      video_Duration=data.duration
      video_Link=data.link
      try:
        article(data.my_strr)
      except:
        data.text="I can't find an article for this goal"
      wrd=data.text
      return render_template('getzing/formC.html',video_Title=video_Title,video_Duration=video_Duration,video_Link=video_Link,wrd=wrd)



def abort_if_todo_doesnt_exist(todo_id):
    TODOS = {
        
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
    data.TODOS=TODOS
    if todo_id not in data.TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')



class Todo(Resource):
    def get(self, todo_id):
        TODOS = {
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
        data.TODOS=TODOS
        abort_if_todo_doesnt_exist(todo_id)
        return data.TODOS[todo_id]

    def delete(self, todo_id):
        TODOS = {
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
        data.TODOS=TODOS
        abort_if_todo_doesnt_exist(todo_id)
        del data.TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        TODOS = {
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
        data.TODOS=TODOS
        args = parser.parse_args()
        task = {'task': args['task']}
        data.TODOS[todo_id] = task
        return task, 201

class TodoList(Resource):
    def get(self):
        TODOS = {
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
        data.TODOS=TODOS
        return data.TODOS

    def post(self):
        TODOS = {
            'todo1': {'user_input': data.goals},
            'todo2': {'suggestion': data.words},
            'todo3': {'more_info':  data.qq},
        }
        data.TODOS=TODOS
        args = parser.parse_args()
        todo_id = int(max(data.TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        data.TODOS[todo_id] = {'task': args['task']}
        return data.TODOS[todo_id], 201


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')

if __name__ == '__main__': 
  application.run()

