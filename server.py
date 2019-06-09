import analysis
from constants import *
import chat_pb2
import flask
from flask import Flask
from google.protobuf.json_format import MessageToDict

ia = None
app = Flask(__name__)

@app.route('/')
def main():
	return 'Main page'

@app.route('/api/conversations')
def conversations():
	c_metadatas, m_resp = ia.get_conversations()
	return flask.jsonify({
		'conversations': [MessageToDict(c) for c in c_metadatas],
		'counts': [MessageToDict(m) for m in m_resp]
		})

def init():
	global ia
	f = open(EXPORT_PATH, 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = analysis.InboxAnalyzer(inbox)

init()