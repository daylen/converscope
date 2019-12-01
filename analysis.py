from constants import *
import chat_pb2
from metric_pb2 import *
from collections import Counter

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
