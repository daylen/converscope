import glob
import chat_pb2
import json
from constants import *
import google.protobuf.text_format as text_format

def get_content_type(message_obj):
	# Message is of Generic type but has special fields.
	if 'sticker' in message_obj:
		return chat_pb2.Message.CT_STICKER
	if 'photos' in message_obj:
		return chat_pb2.Message.CT_PHOTO
	if 'gifs' in message_obj:
		return chat_pb2.Message.CT_GIF
	if 'files' in message_obj:
		return chat_pb2.Message.CT_FILE
	if 'videos' in message_obj:
		return chat_pb2.Message.CT_VIDEO
	if 'audio_files' in message_obj:
		return chat_pb2.Message.CT_AUDIO
	# Message should be ignored. Currently we ignore phone/video calls,
	# events where someone is added/removed to a group, payments, and calendar plans.
	if message_obj['type'] in set(['Call', 'Subscribe', 'Unsubscribe', 'Payment', 'Plan']):
		return chat_pb2.Message.CT_IGNORE
	# For now, process Share types as just text.
	if message_obj['type'] == 'Generic' or message_obj['type'] == 'Share':
		return chat_pb2.Message.CT_TEXT
	print('Unknown type:', message_obj['type'])
	return chat_pb2.Message.CT_UNKNOWN

def read_fb_conversation(path):
	"""
	Read a single Facebook message_1.json file. Returns a Conversation proto.
	"""
	conversation = chat_pb2.Conversation()
	with open(path) as f:
		data = json.load(f)
		# data = data
		# print(data)
		conversation.group_name = data['title'].encode('latin1').decode('utf8')
		for participant_obj in data['participants']:
			conversation.participant.extend([participant_obj['name']])
		KNOWN_FIELDS = set(['sender_name', 'timestamp_ms', 'content', 'type'])
		for message_obj in data['messages']:
			message_proto = conversation.message.add()
			message_proto.sender_name = message_obj['sender_name']
			message_proto.timestamp = message_obj['timestamp_ms'] // 1000
			message_proto.content_type = get_content_type(message_obj)
			if message_proto.content_type == chat_pb2.Message.CT_TEXT:
				if 'content' not in message_obj:
					# Sometimes for some odd reason, Facebook will have blank messages
					pass
				else:
					message_proto.content = message_obj['content'].encode('latin1').decode('utf8')
			elif message_proto.content_type == chat_pb2.Message.CT_STICKER:
				message_proto.media_uri.extend([message_obj['sticker']['uri']])
			elif message_proto.content_type == chat_pb2.Message.CT_PHOTO:
				message_proto.media_uri.extend([obj['uri'] for obj in message_obj['photos']])
			elif message_proto.content_type == chat_pb2.Message.CT_GIF:
				message_proto.media_uri.extend([obj['uri'] for obj in message_obj['gifs']])
			elif message_proto.content_type == chat_pb2.Message.CT_FILE:
				message_proto.media_uri.extend([obj['uri'] for obj in message_obj['files']])
			elif message_proto.content_type == chat_pb2.Message.CT_VIDEO:
				message_proto.media_uri.extend([obj['uri'] for obj in message_obj['videos']])
			elif message_proto.content_type == chat_pb2.Message.CT_AUDIO:
				message_proto.media_uri.extend([obj['uri'] for obj in message_obj['audio_files']])
			elif message_proto.content_type == chat_pb2.Message.CT_IGNORE:
				pass
			else:
				print('Unprocessed:', chat_pb2.Message.ContentType.Name(message_proto.content_type), message_obj)
	return conversation

def assign_conversation_ids(inbox):
	i = 1
	for c in inbox.conversation:
		c.id = i
		i += 1

def read_facebook(fb_path):
	"""
	Read a Facebook /messages/ folder. That folder should contain an
	archived_threads folder and an inbox folder. Returns an Inbox proto.
	"""
	print('Reading Facebook directory: ' + fb_path)
	folders = ['archived_threads', 'inbox']
	inbox = chat_pb2.Inbox()
	for folder in folders:
		full_path = fb_path + '/' + folder
		print('Reading ' + full_path)
		conversation_paths = glob.glob(full_path + '/*/message*.json')
		for path in conversation_paths:
			conversation = read_fb_conversation(path)
			inbox.conversation.extend([conversation])
	assign_conversation_ids(inbox)
	return inbox

def main():
	inbox = read_facebook(FB_IMPORT_PATH)

	print(inbox)
	if USE_PBTXT:
		f = open(EXPORT_PATH_FB + '.pbtxt', 'w')
		f.write(str(text_format.MessageToString(inbox)))
	else:
		f = open(EXPORT_PATH_FB + '.pb', 'wb')
		f.write(inbox.SerializeToString())
	f.close()
	print('Wrote', len(inbox.conversation), 'conversations to', EXPORT_PATH_FB)

if __name__ == '__main__':
	main()