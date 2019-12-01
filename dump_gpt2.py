from analysis import InboxAnalyzer
from constants import *
import random

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
