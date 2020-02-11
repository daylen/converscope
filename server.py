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


def strip_group_name(group_name):
    names = ia.all_names()
    names.remove(SELF_NAME)
    for name in names:
        if name in group_name:
            return 'XXX'
    return group_name


def maybe_strip_pii(c):
    if STRIP_PII:
        c['groupName'] = strip_group_name(c['groupName'])
        c['participant'] = [
            'XXX' if name != SELF_NAME else SELF_NAME
            for name in c['participant']
        ]
    # Always delete messages even if STRIP_PII is false
    if 'message' in c:
        del c['message']


def maybe_strip_names(arr_of_arr):
    if not STRIP_PII:
        return arr_of_arr
    names = ia.all_names()
    names.remove(SELF_NAME)
    # print(names)
    # stripped = []
    for i in range(len(arr_of_arr)):
        # x2 = []
        for j in range(len(arr_of_arr[i])):
            if not isinstance(arr_of_arr[i][j], str):
                continue
            for name in names:
                if name in arr_of_arr[i][j]:
                    arr_of_arr[i][j] = arr_of_arr[i][j].replace(name, 'XXX')
    return arr_of_arr


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
        zipped.append(cdict)
    zipped = list(reversed(sorted(zipped, key=lambda x: x['count'])))
    # Truncate
    zipped = zipped[:min(HOME_MAX_CONVERSATIONS, len(zipped))]
    for c in zipped:
        maybe_strip_pii(c)
        c['count_by_day'] = ia.get_count_timeline(c['id'])
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
        'conversations': zipped,
        'dates': ia.get_date_range(),
    })


@app.route('/api/conversation')
def conversation_details():
    c_id = request.args.get('id')
    if not ia.exists(c_id):
        return flask.jsonify(
            {'error': 'Conversation ID ' + c_id + ' not found'})
    c = ia.get_conversation(c_id)

    # message count metric
    counts_by_name = []
    for name in c.participant:
        counts_by_name.append([
            name,
            len(list(filter(lambda x: x.sender_name == name, c.message)))
        ])
    # char count
    char_counts_by_name = []
    for name in c.participant:
        char_counts_by_name.append([
            name,
            sum(
                map(lambda x: len(x.content),
                    filter(lambda x: x.sender_name == name, c.message)))
        ])
    # most used emoji
    emoji_list_by_name = analysis.emoji_counts(c)
    pop_emoji_by_name = []
    for (name, emojis) in emoji_list_by_name.items():
        the_emoji, num_times = Counter(emojis).most_common(1)[0]
        pop_emoji_by_name.append([
            name + ' used ' + str(num_times) + ' time' +
            ('' if num_times == 1 else 's'), the_emoji
        ])
    # longest streak
    streak_length, end_date = ia.longest_streak_days(c_id)
    longest_streak = [['days, ending on ' + end_date, streak_length]]

    cdict = MessageToDict(c)
    maybe_strip_pii(cdict)
    cdict['metrics'] = {
        'messages_sent': maybe_strip_names(counts_by_name),
        'characters_sent': maybe_strip_names(char_counts_by_name),
        'most_used_emoji': maybe_strip_names(pop_emoji_by_name),
        'longest_streak': longest_streak
    }
    return flask.jsonify(cdict)
