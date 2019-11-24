import glob
import chat_pb2
import json
import sqlite3
from constants import *

def read_imessage(path):
	# useful resource: https://github.com/dsouzarc/iMessageAnalyzer/blob/master/Random%20SQLite%20Commands.txt
	conn = sqlite3.connect(path)
	c = conn.cursor()
	c2 = conn.cursor()
	# get all the chat IDs
	chat_ids = c.execute("SELECT ROWID FROM chat")
	inbox = chat_pb2.Inbox()
	for chat_id in chat_ids:
		# print('CHAT ID', chat_id)
		conversation = chat_pb2.Conversation()
		# TODO fill in name, participants
		conversation.group_name = str(chat_id[0])
		messages = c2.execute("SELECT text, handleT.id, date, is_from_me FROM message messageT INNER JOIN chat_message_join chatMessageT ON (chatMessageT.chat_id=" + str(chat_id[0]) + ") AND messageT.ROWID=chatMessageT.message_id INNER JOIN handle handleT ON handleT.ROWID = messageT.handle_id ORDER BY messageT.date")
		for msg in messages:
			if msg[0] is None:
				print('skipping empty message', msg)
				continue
			message_proto = conversation.message.add()
			message_proto.sender_name = msg[1]
			message_proto.timestamp = msg[2]
			message_proto.content_type = chat_pb2.Message.CT_TEXT
			message_proto.content = msg[0]
		inbox.conversation.extend([conversation])
	conn.close()
	return inbox

def main():
	inbox = read_imessage(IMESSAGE_IMPORT_PATH)
	# assign_conversation_ids(inbox)

	print(inbox)
	# f = open(EXPORT_PATH2, 'wb')
	# f.write(inbox.SerializeToString())
	# f.close()
	# print('Wrote', len(inbox.conversation), 'conversations to', EXPORT_PATH2)

if __name__ == '__main__':
	main()