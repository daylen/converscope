from constants import *
import chat_pb2
from collections import Counter, defaultdict
import sys
import numpy as np
import datetime
import time
from enum import Enum
from emoji import UNICODE_EMOJI
from sklearn.feature_extraction.text import TfidfVectorizer

TFIDF_BLACKLIST = [
    'kimtranscriptpluginbreadcrumbtextreceiveridentifier', 'http'
]


class InboxAnalyzer:

    # conversation id -> sorted list of top n tokens
    tfidf_tokens_by_cid = {}
    tfidf_scores_by_cid = {}

    def __init__(self):
        f = open(EXPORT_PATH + ('.pbtxt' if USE_PBTXT else '.pb'),
                 'r' if USE_PBTXT else 'rb')
        inbox = chat_pb2.Inbox()
        inbox.ParseFromString(f.read())
        f.close()

        self.inbox = inbox
        self.id_conversation_map = {c.id: c for c in inbox.conversation}
        assert len(self.id_conversation_map) == len(inbox.conversation)
        self.oldest_ts = sys.maxsize
        self.newest_ts = -1
        for c_id in self.id_conversation_map.keys():
            old, new = self.__get_extreme_ts(c_id)
            self.oldest_ts = min(self.oldest_ts, old)
            self.newest_ts = max(self.newest_ts, new)
        print('InboxAnalyzer initialized,', len(self.id_conversation_map),
              'conversations')
        self.tfidf = TfidfVectorizer(max_df=0.2, max_features=50000, stop_words=TFIDF_BLACKLIST)
        if USE_TFIDF:
            self.__fit_tfidf()

    def __fit_tfidf(self):

        def doc_generator():
            for c in self.id_conversation_map.values():
                chat = ''
                for m in c.message:
                    chat += m.content + '\n'
                yield chat

        print('running fit')
        self.tfidf.fit(doc_generator())
        print('done')

    def get_conversations(self):
        """
		Return all conversation metadata stripped of messages.
		Returns: [Conversation]
		"""
        c_metadatas = []
        for c in self.id_conversation_map.values():
            c_metadata = chat_pb2.Conversation()
            c_metadata.id = c.id
            c_metadata.participant.extend(c.participant)
            c_metadata.group_name = c.group_name
            c_metadatas.append(c_metadata)
        return c_metadatas

    def get_message_counts(self, start_ts=0, end_ts=sys.maxsize):
        return {
            c.id: len(
                list(
                    filter(
                        lambda m: m.timestamp > start_ts and m.timestamp <
                        end_ts, c.message))) for c in self.inbox.conversation
        }

    def exists(self, c_id):
        return c_id in self.id_conversation_map

    def get_conversation(self, c_id):
        return self.id_conversation_map[c_id]

    def search_conversations_by_name(self, name):
        matches = []
        for c in self.inbox.conversation:
            if name.lower() in c.group_name.lower():
                matches.append(c.id)
        return matches

    def get_oldest_ts(self):
        return self.oldest_ts

    def get_newest_ts(self):
        return self.newest_ts

    def __get_extreme_ts(self, c_id):
        c = self.id_conversation_map[c_id]
        if len(c.message) == 0:
            return sys.maxsize, -1
        # TODO hack: there appear to be some corrupted timestamps from ~2003. Filter to be >2007.
        return min(
            filter(lambda x: x > 1167638400,
                   map(lambda x: x.timestamp,
                       c.message))), max(map(lambda x: x.timestamp, c.message))

    def get_approx_histogram_week_bins(self, c_id):
        """
        Histogram of message counts, binned by week and using an approximate algorithm.
        """
        c = self.id_conversation_map[c_id]
        messages = sorted(map(lambda x: x.timestamp, c.message))
        num_days = (datetime.date.fromtimestamp(self.newest_ts) -
                    datetime.date.fromtimestamp(self.oldest_ts)).days
        date_range = (self.oldest_ts, self.newest_ts)
        hist, bin_edges = np.histogram(messages,
                                       bins=num_days // 7,
                                       range=date_range)
        return hist.tolist(), self.__get_date_range(self.oldest_ts,
                                                    self.newest_ts,
                                                    week_mode=True,
                                                    size=num_days // 7)

    def get_accurate_histogram_day_bins(self, c_id):
        """
        Histogram of message counts, binned by day and using an accurate algorithm
        that takes into account time zone and midnight boundaries.
		"""
        c = self.id_conversation_map[c_id]
        hist = defaultdict(int)
        messages = sorted(c.message, key=lambda x: x.timestamp)
        for m in messages:
            date_str = datetime.date.fromtimestamp(m.timestamp).isoformat()
            hist[date_str] += 1
        extremes = self.__get_extreme_ts(c_id)
        date_range = self.__get_date_range(start_ts=extremes[0],
                                           end_ts=extremes[1])
        counts = [hist[x] if x in hist else 0 for x in date_range]
        return counts, date_range

    def __get_date_range(self,
                         start_ts,
                         end_ts,
                         week_mode=False,
                         size=sys.maxsize):
        date_range = (datetime.date.fromtimestamp(start_ts),
                      datetime.date.fromtimestamp(end_ts))
        dates = [date_range[0]]
        while (not week_mode and
               dates[-1] != date_range[1]) or (week_mode and len(dates) < size):
            increment = 7 if week_mode else 1
            dates.append(dates[-1] + datetime.timedelta(days=increment))
        dates = list(map(lambda x: x.isoformat(), dates))
        return dates

    def longest_streak_days(self, c_id):
        hist = zip(*self.get_accurate_histogram_day_bins(c_id))
        best = 0
        best_end_date = ''
        curr = 0
        for count, date in hist:
            if count == 0:
                curr = 0
            else:
                curr += 1
            if curr > best:
                best = curr
                best_end_date = date
        return best, best_end_date

    def all_names(self):
        names = set()
        for c in self.inbox.conversation:
            names.update(c.participant)
        return names

    def get_top_tfidf_tokens(self, c_id, n=20):
        # Check if we have already computed all the tokens we need
        if c_id in self.tfidf_tokens_by_cid and len(self.tfidf_tokens_by_cid[c_id]) >= n:
            return self.tfidf_tokens_by_cid[c_id][:n], self.tfidf_scores_by_cid[c_id][:n]

        conv = self.get_conversation(c_id)
        # Make the document
        chat = ''
        for m in conv.message:
            chat += m.content + '\n'
        response = self.tfidf.transform([chat])

        feature_array = np.array(self.tfidf.get_feature_names())
        tfidf_sorting = np.argsort(response.toarray()).flatten()[::-1]
        top_tokens = feature_array[tfidf_sorting]
        scores = response.toarray().flatten()[tfidf_sorting]

        # Memoize
        self.tfidf_tokens_by_cid[c_id] = top_tokens[:n].tolist()
        self.tfidf_scores_by_cid[c_id] = scores[:n].tolist()

        return self.tfidf_tokens_by_cid[c_id], self.tfidf_scores_by_cid[c_id]


def print_messages(conv, start_ts=0, end_ts=sys.maxsize):
    i = 0
    for message in sorted(conv.message, key=lambda m: m.timestamp):
        if message.timestamp > start_ts and message.timestamp < end_ts:
            print(
                i,
                datetime.datetime.fromtimestamp(message.timestamp).isoformat(),
                message.sender_name, ':', message.content)
            i += 1


class CountGranularity(Enum):
    MESSAGE = 1
    CHARACTER = 2


def get_counts_by_sender(conv, count_granularity):
    if count_granularity == CountGranularity.MESSAGE:
        return Counter(map(lambda x: x.sender_name, conv.message))
    elif count_granularity == CountGranularity.CHARACTER:
        c = defaultdict(int)
        for m in conv.message:
            c[m.sender_name] += len(m.content)
        return c


def main():
    ia = InboxAnalyzer()
    print('total messages',
          sum([len(x.message) for x in ia.inbox.conversation]))
    # print(ia.get_top_tfidf_tokens(''))
    conv = ia.get_conversation('e56a810ed31da5ad9056e8d64c3a1711b505d7b6')
    print_messages(conv)
    # print(list(map(lambda x: (ia.get_conversation(x).group_name, ia.get_conversation(x).id), ia.search_conversations_by_name('Roader trip'))))


def emoji_counts(conv):
    emoji_list_by_name = defaultdict(list)
    for msg in conv.message:
        for char in msg.content:
            if char in UNICODE_EMOJI:
                emoji_list_by_name[msg.sender_name].append(char)
    return emoji_list_by_name


if __name__ == '__main__':
    main()
