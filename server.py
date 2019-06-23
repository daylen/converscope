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

def zip_metrics_for_conversations(conversations, metrics):
	"""
	Add the metric to the conversations json. Assumes that the filter is just
	conversation_id.
	"""
	cid_count_dict = {}
	for int_metric in metrics:
		cid_count_dict[int_metric.filter.conversation_id] = int_metric.value
	zipped = []
	for c in conversations:
		cdict = MessageToDict(c)
		cdict['count'] = cid_count_dict[c.id]
		zipped.append(cdict)
	return list(reversed(sorted(zipped, key=lambda x: x['count'])))

@app.route('/')
def main():
	return 'Main page'

@app.route('/api/conversations')
def conversations():
	c_metadatas, m_resp = ia.get_conversations()
	return flask.jsonify({
		'conversations': zip_metrics_for_conversations(c_metadatas, m_resp)
		})

def init():
	global ia
	f = open(EXPORT_PATH, 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = analysis.InboxAnalyzer(inbox)

init()