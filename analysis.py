from constants import *
import chat_pb2
from metric_pb2 import *
from collections import Counter
import sys
import numpy as np
import datetime
import time

class InboxAnalyzer:

	def __init__(self, inbox):
		self.inbox = inbox
		self.id_conversation_map = {}
		# Precompute message counts so that we have an ordering
		self.id_count_map = {}
		for c in inbox.conversation:
			if c.id in self.id_conversation_map:
				raise Exception("Duplicate ID found")
			self.id_conversation_map[c.id] = c
			self.id_count_map[c.id] = len(c.message)
		self.oldest_ts = sys.maxsize
		for c_id in self.id_conversation_map.keys():
			self.oldest_ts = min(self.oldest_ts, self.get_oldest_ts(c_id))
		print('InboxAnalyzer initialized,', len(self.id_conversation_map), 'conversations')

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

	def get_message_counts(self):
		return self.id_count_map

	def get_conversation(self, c_id):
		return self.id_conversation_map[c_id]

	def get_oldest_ts(self, c_id):
		c = self.id_conversation_map[c_id]
		if len(c.message) == 0:
			return sys.maxsize
		return min(map(lambda x: x.timestamp, c.message))

	def get_count_timeline(self, c_id, start_ts=-1):
		"""
		If start_ts is -1, uses the oldest ts in the inbox as the start_ts.
		Bin granularity is by day.
		End ts is today.
		"""
		c = self.id_conversation_map[c_id]
		messages = sorted(map(lambda x: x.timestamp, c.message))
		if start_ts == -1:
			start_ts = self.oldest_ts
		num_days = (datetime.date.today() - datetime.date.fromtimestamp(start_ts)).days
		date_range = (start_ts, time.time())
		hist, bin_edges = np.histogram(messages, bins=num_days, range=date_range)
		return hist.tolist()
		

def main():
	f = open(EXPORT_PATH + ('.pbtxt' if USE_PBTXT else '.pb'), 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = InboxAnalyzer(inbox)
	hist = ia.get_count_timeline(955)
	np.set_printoptions(threshold=sys.maxsize)
	print(hist)

if __name__ == '__main__':
	main()