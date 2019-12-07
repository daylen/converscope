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
		self.id_conversation_map = {c.id: c for c in inbox.conversation}
		assert len(self.id_conversation_map) == len(inbox.conversation)
		self.oldest_ts = sys.maxsize
		for c_id in self.id_conversation_map.keys():
			self.oldest_ts = min(self.oldest_ts, self.__get_oldest_ts(c_id))
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
		return {c.id: len(c.message) for c in self.inbox.conversation}

	def get_conversation(self, c_id):
		return self.id_conversation_map[c_id]

	def get_conversation_by_group_name(self, group_name):
		for c in self.inbox.conversation:
			if c.group_name == group_name:
				return c
		return None

	def get_oldest_ts(self):
		return self.oldest_ts

	def __get_oldest_ts(self, c_id):
		c = self.id_conversation_map[c_id]
		if len(c.message) == 0:
			return sys.maxsize
		# TODO hack: there appear to be some corrupted timestamps from ~2003. Filter to be >2007.
		return min(filter(lambda x: x > 1167638400, map(lambda x: x.timestamp, c.message)))

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
		

def print_messages(group_name, start_ts, end_ts):
	f = open(EXPORT_PATH + ('.pbtxt' if USE_PBTXT else '.pb'), 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()
	ia = InboxAnalyzer(inbox)
	i = 0
	conv = ia.get_conversation_by_group_name(group_name)
	for message in conv.message:
		if message.timestamp > start_ts and message.timestamp < end_ts:
			print(i, message.timestamp, message.sender_name, ':', message.content)
			i += 1

# if __name__ == '__main__':
# 	main()