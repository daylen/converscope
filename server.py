import analysis
from constants import *
import chat_pb2
import flask
from flask_cors import CORS
from flask import Flask
from google.protobuf.json_format import MessageToDict

ia = None
app = Flask(__name__)
CORS(app)

def zip_metrics_for_conversations(conversations, id_count_map):
	"""
	Add the metric to the conversations json.
	"""
	zipped = []
	for c in conversations:
		cdict = MessageToDict(c)
		cdict['count'] = id_count_map[c.id] if c.id in id_count_map else -1
		zipped.append(cdict)
	return list(reversed(sorted(zipped, key=lambda x: x['count'])))

@app.route('/')
def main():
	return 'Main page'

@app.route('/api/conversations')
def conversations():
	c_metadatas = ia.get_conversations()
	id_count_map = ia.get_message_counts()
	return flask.jsonify({
		'conversations': zip_metrics_for_conversations(c_metadatas, id_count_map)
		})

def init():
	global ia
	f = open(EXPORT_PATH + ('.pbtxt' if USE_PBTXT else '.pb'), 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = analysis.InboxAnalyzer(inbox)

init()