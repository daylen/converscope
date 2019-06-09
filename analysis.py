from constants import *
import chat_pb2
from metric_pb2 import *
from collections import Counter

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
	req.filter.max_participants = 2

	print('MetricRequest:', req)
	resp = ia.handle_metric_request(req)
	# print(list(filter_zeros(resp.int_metric)))
	# print('===')
	print(sort_metrics(combine_metrics(resp.int_metric, 'conversation_id')))

if __name__ == '__main__':
	main()