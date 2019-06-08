import glob
import chat_pb2

FB_PATH = './data/facebook-daylenyang-json/messages'
IMESSAGE_PATH = './imessage_chat.db'

def read_fb_conversation(path):
	"""
	Read a single Facebook message_1.json file. Returns a Conversation proto.
	"""
	return chat_pb2.Conversation()

def read_fb_dir(fb_path):
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
		conversation_paths = glob.glob(full_path + '/*/message_1.json')
		for path in conversation_paths:
			conversation = read_fb_conversation(path)
			inbox.conversation.extend([conversation])
	return inbox

def read_imessage(imessage_path):
	pass

def main():
	fb_inbox = read_fb_dir(FB_PATH)
	print('Conversations in FB:', len(fb_inbox.conversation))
	imessage_inbox = read_imessage(IMESSAGE_PATH)

if __name__ == '__main__':
	main()