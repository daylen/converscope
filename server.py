import analysis
from constants import *
import chat_pb2
import flask
from flask_cors import CORS
from flask import Flask, request, send_from_directory
from google.protobuf.json_format import MessageToDict
import datetime
import json
import sys
import os
import time
from enum import Enum
from collections import defaultdict, Counter

ia = analysis.InboxAnalyzer()
app = Flask(__name__, static_folder=APP_PATH)
CORS(app)


def zip_metrics_for_conversations(conversations, id_count_map, ia,
                                  filter_to_groups):
    """
	Add the metric to the conversations json.
	"""
    num_days = 0
    zipped = []
    for c in conversations:
        if not filter_to_groups and len(c.participant) > 2:
            continue
        if filter_to_groups and len(c.participant) <= 2:
            continue
        cdict = MessageToDict(c)
        cdict['count'] = id_count_map[c.id] if c.id in id_count_map else -1
        if STRIP_PII:
            cdict['participant'] = []
            if filter_to_groups:
                # Keep names for group chats
                pass
            else:
                cdict['groupName'] = ''
        zipped.append(cdict)
    zipped = list(reversed(sorted(zipped, key=lambda x: x['count'])))
    # Truncate
    zipped = zipped[:min(HOME_MAX_CONVERSATIONS, len(zipped))]
    i = 1
    for c in zipped:
        if STRIP_PII and not filter_to_groups:
            c['groupName'] = 'person #' + str(i)
            i += 1
        c['count_by_day'] = ia.get_count_timeline(int(c['id']))
        num_days = len(c['count_by_day'])
    return zipped, num_days


# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


TIME_RANGES = {
    'all_time': (0, sys.maxsize),
    'high_school': (0, HIGH_SCHOOL_GRAD_TS),
    'college': (HIGH_SCHOOL_GRAD_TS, COLLEGE_GRAD_TS),
    'post_college': (COLLEGE_GRAD_TS, sys.maxsize)
}


def get_time_range(time_period):
    if time_period in TIME_RANGES:
        return TIME_RANGES[time_period]
    elif time_period == 'last_year':
        return (time.time() - 60 * 60 * 24 * 365, sys.maxsize)
    else:
        return time_period[TimePeriod.ALL_TIME]


@app.route('/api/conversations')
def conversations():
    c_metadatas = ia.get_conversations()
    id_count_map = ia.get_message_counts(
        *get_time_range(request.args.get('time_period')))
    filter_to_groups = request.args.get('groups') == '1'
    zipped, num_days = zip_metrics_for_conversations(c_metadatas, id_count_map,
                                                     ia, filter_to_groups)
    return flask.jsonify({
        'conversations':
            zipped,
        'dates':
            list(
                reversed([(datetime.datetime.today() -
                           datetime.timedelta(days=x)).strftime('%Y-%m-%d')
                          for x in range(num_days)])),
        'first_ts':
            ia.get_oldest_ts(),
    })


@app.route('/api/conversation')
def conversation_details():
    c_id = request.args.get('id')
    if not ia.exists(int(c_id)):
        return flask.jsonify(
            {'error': 'Conversation ID ' + c_id + ' not found'})
    c_id = int(c_id)
    c = ia.get_conversation(c_id)

    # message count metric
    counts_by_name = {}
    for name in c.participant:
        counts_by_name[name] = len(
            list(filter(lambda x: x.sender_name == name, c.message)))
    # char count
    char_counts_by_name = {}
    for name in c.participant:
        char_counts_by_name[name] = sum(
            map(lambda x: len(x.content),
                filter(lambda x: x.sender_name == name, c.message)))
    # most used emoji
    emoji_list_by_name = analysis.emoji_counts(c)
    pop_emoji_by_name = {}
    for (name, emojis) in emoji_list_by_name.items():
        the_emoji, num_times = Counter(emojis).most_common(1)[0]
        pop_emoji_by_name[name + ' used ' + str(num_times) + ' time' +
                          ('' if num_times == 1 else 's')] = the_emoji

    cdict = MessageToDict(c)
    del cdict['message']
    cdict['metrics'] = {
        'messages_sent': counts_by_name,
        'characters_sent': char_counts_by_name,
        'most_used_emoji': pop_emoji_by_name,
        'longest_streak': {
            'days': ia.longest_streak_days(c_id)
        }
    }
    return flask.jsonify(cdict)
