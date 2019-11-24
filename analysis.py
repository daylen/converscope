from constants import *
import chat_pb2
from metric_pb2 import *
from collections import Counter
import random

def count_messages(c_view, f):
	"""
	Input: ConversationView, MetricFilter
	Return: [IntegerMetric]
	One IntegerMetric per sender_name
	"""
	metrics = []
	sender_names = c_view.get_participants()
	if len(f.sender_name) > 0:
		sender_names = [f.sender_name]
	for sender_name in sender_names:
		filter_with_name = MetricFilter()
		filter_with_name.CopyFrom(f)
		filter_with_name.sender_name = sender_name

		metric = IntegerMetric()
		metric.value = len(c_view.get_messages(filter_with_name))
		metric.filter.CopyFrom(filter_with_name)
		metrics.append(metric)
	return metrics

class ConversationView:
	def __init__(self, conversation):
		self.conversation = conversation

	def get_participants(self):
		return self.conversation.participant

	def get_messages(self, f):
		"""
		Input: MetricFilter
		Return: [Message]
		"""
		# TODO handle timestamps
		if f.max_participants > 0 and len(self.get_participants()) > f.max_participants:
			return []
		messages = self.conversation.message
		if len(f.sender_name) > 0:
			messages = filter(lambda m: f.sender_name == m.sender_name, messages)
		return list(messages)


class InboxAnalyzer:
	metric_handler_map = {
		MN_MESSAGE_COUNT: count_messages
	}

	def __init__(self, inbox):
		self.inbox = inbox
		self.id_conversation_map = {}
		for c in inbox.conversation:
			self.id_conversation_map[c.id] = c
		print('InboxAnalyzer initialized,', len(self.id_conversation_map), 'conversations')

	def get_conversations(self):
		"""
		Return all conversation metadata stripped of messages, and the metric
		response for the count metric.

		Returns: [Conversation], [IntegerMetric]
		"""
		c_metadatas = []
		for c in self.id_conversation_map.values():
			c_metadata = chat_pb2.Conversation()
			c_metadata.id = c.id
			c_metadata.participant.extend(c.participant)
			c_metadata.group_name = c.group_name
			c_metadatas.append(c_metadata)
		req = MetricRequest()
		req.metric = MN_MESSAGE_COUNT
		resp = self.handle_metric_request(req)
		# Eliminate sender_name to get total message count in thread
		m_resp = sort_metrics(combine_metrics(resp.int_metric, 'sender_name'))
		return c_metadatas, m_resp

	def get_conversation(self, c_id):
		return self.id_conversation_map[c_id]

	def handle_metric_request(self, req):
		"""
		Input: MetricRequest
		Return: MetricResponse
		"""
		# Was a conversation ID specified?
		filters = []
		if req.HasField('filter'):
			if req.filter.conversation_id > 0:
				filters.append(req.filter)
			else:
				for c_id in self.id_conversation_map.keys():
					mf = MetricFilter()
					mf.CopyFrom(req.filter)
					mf.conversation_id = c_id
					filters.append(mf)
		else:
			for c_id in self.id_conversation_map.keys():
				mf = MetricFilter()
				mf.conversation_id = c_id
				filters.append(mf)

		metrics = []
		for f in filters:
			c_view = ConversationView(self.id_conversation_map[f.conversation_id])
			metrics.extend(self.metric_handler_map[req.metric](c_view, f))

		m_resp = MetricResponse()
		m_resp.request.CopyFrom(req)
		m_resp.int_metric.extend(metrics)
		return m_resp

def combine_metrics(metrics, field_to_eliminate):
	"""
	Try to eliminate field_to_eliminate from the filter.
	"""
	d = Counter()
	for metric in metrics:
		new_filter = MetricFilter()
		new_filter.CopyFrom(metric.filter)
		new_filter.ClearField(field_to_eliminate)
		d[new_filter.SerializeToString()] += metric.value
	new_metrics = []
	for f, v in d.items():
		m = IntegerMetric()
		m.value = v
		m.filter.ParseFromString(f)
		new_metrics.append(m)
	return new_metrics

def sort_metrics(metrics):
	return sorted(metrics, key=lambda x: x.value)

def filter_zeros(metrics):
	return filter(lambda x: x.value > 0, metrics)

def main():
	f = open(EXPORT_PATH, 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()

	ia = InboxAnalyzer(inbox)
	req = MetricRequest()
	req.metric = MN_MESSAGE_COUNT
	# req.filter.max_participants = 2

	print('MetricRequest:', req)
	resp = ia.handle_metric_request(req)
	# print(list(filter_zeros(resp.int_metric)))
	# print('===')
	result = sort_metrics(combine_metrics(resp.int_metric, 'sender_name'))
	print(result)
	for im in result:
		c = ia.get_conversation(im.filter.conversation_id)
		print('[', im, c.group_name, c.participant, ']')
	# print(sort_metrics(resp.int_metric))

def word_find(word):
	f = open(EXPORT_PATH, 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()

	ia = InboxAnalyzer(inbox)
	req = MetricRequest()
	req.metric = MN_MESSAGE_COUNT
	req.filter.sender_name = 'Daylen Yang'
	# req.filter.max_participants = 2

	print('MetricRequest:', req)
	resp = ia.handle_metric_request(req)
	# print(list(filter_zeros(resp.int_metric)))
	# print('===')
	result = sort_metrics(combine_metrics(resp.int_metric, 'sender_name'))
	print(result)
	for im in result:
		c = ia.get_conversation(im.filter.conversation_id)
		for msg in c.message:
			if msg.content_type == chat_pb2.Message.CT_TEXT and word in msg.content.lower() and msg.sender_name == 'Daylen Yang':
				print('[', im, c.group_name, c.participant, ']')
				print(msg)
	# print(sort_metrics(resp.int_metric))

def conv_to_string(conv):
	ordered = sorted(conv.message, key=lambda x: x.timestamp)
	text_only = filter(lambda x: x.content_type == chat_pb2.Message.CT_TEXT, ordered)
	transcript = ''
	for message in text_only:
		transcript += str.upper(message.sender_name) + ': ' + message.content + '\n\n'
	return transcript

def conv_count(conv):
	ordered = sorted(conv.message, key=lambda x: x.timestamp)
	text_only = filter(lambda x: x.content_type == chat_pb2.Message.CT_TEXT, ordered)
	return len(list(text_only))

def dump_for_gpt2():
	"""
	Dump everything to a text file for finetuning GPT-2.
	"""
	f = open(EXPORT_PATH, 'rb')
	inbox = chat_pb2.Inbox()
	inbox.ParseFromString(f.read())
	f.close()

	random.seed(42)
	TRAIN_PERCENT = 0.85

	ia = InboxAnalyzer(inbox)
	train_txt = ''
	test_txt = ''
	train_count, test_count = 0, 0
	for c_metadata in ia.get_conversations()[0]:
		conv = ia.get_conversation(c_metadata.id)
		count = conv_count(conv)
		transcript = conv_to_string(conv)
		if random.random() < TRAIN_PERCENT:
			train_txt += '<|startoftext|>\n'
			train_txt += transcript + '\n'
			train_txt += '<|endoftext|>\n'
			train_count += count
		else:
			test_txt += '<|startoftext|>\n'
			test_txt += transcript + '\n'
			test_txt += '<|endoftext|>\n'
			test_count += count
	with open('./gpt2_train_daylenyang.txt', 'w') as f:
		f.write(train_txt)
	with open('./gpt2_test_daylenyang.txt', 'w') as f:
		f.write(test_txt)
	print(train_count, test_count, 'messages')


if __name__ == '__main__':
	dump_for_gpt2()