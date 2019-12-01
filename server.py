import analysis
from constants import *
import chat_pb2
import flask
from flask_cors import CORS
from flask import Flask
from google.protobuf.json_format import MessageToDict
import datetime

ia = None
app = Flask(__name__)
CORS(app)

def zip_metrics_for_conversations(conversations, id_count_map, ia):
	"""
	Add the metric to the conversations json.
	"""
	num_days = 0
	zipped = []
	for c in conversations:
		cdict = MessageToDict(c)
		cdict['count'] = id_count_map[c.id] if c.id in id_count_map else -1
		zipped.append(cdict)
	zipped = list(reversed(sorted(zipped, key=lambda x: x['count'])))
	# Truncate
	zipped = zipped[:min(HOME_MAX_CONVERSATIONS, len(zipped))]
	for c in zipped:
		c['count_by_day'] = ia.get_count_timeline(int(c['id']))
		num_days = len(c['count_by_day'])
	return zipped, num_days

@app.route('/')
def main():
	return 'Main page'

@app.route('/api/conversations')
def conversations():
	c_metadatas = ia.get_conversations()
	id_count_map = ia.get_message_counts()
	zipped, num_days = zip_metrics_for_conversations(c_metadatas, id_count_map, ia)
	return flask.jsonify({
		'conversations': zipped,
		'dates': list(reversed([(datetime.datetime.today() - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(num_days)]))
		})

def init():
	global ia
	f = open(EXPORT_PATH + ('.pbtxt' if USE_PBTXT else '.pb'), 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = analysis.InboxAnalyzer(inbox)

init()