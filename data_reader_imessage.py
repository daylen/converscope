import glob
import chat_pb2
import json
import sqlite3
from constants import *
import pandas as pd
import phonenumbers
import google.protobuf.text_format as text_format
import datetime

def get_id_name_map(df):
    id_df = df[list(filter(lambda x: 'Phone' in x or 'Email' in x, df.columns))]
    id_name_map = {}
    for idx, row in id_df.iterrows():
        for cell in row:
            if pd.isnull(cell):
                continue
            identifier = cell
            try:
                phone = phonenumbers.parse(cell, 'US')
                identifier = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
            except:
                pass
            id_name_map[identifier] = str(df.loc[idx]['First Name']) + ' ' + str(df.loc[idx]['Last Name'])
    return id_name_map

def read_imessage(path):
	# Load contacts
	id_name_map = get_id_name_map(pd.read_csv(CONTACTS_PATH))

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
		conversation.group_name = 'iMessage Chat ID ' + str(chat_id[0])
		conversation.id = chat_id[0]
		messages = c2.execute("SELECT text, handleT.id, messageT.date/1000000000 + strftime(\"%s\", \"2001-01-01\") as date_unix, is_from_me FROM message messageT INNER JOIN chat_message_join chatMessageT ON (chatMessageT.chat_id=" + str(chat_id[0]) + ") AND messageT.ROWID=chatMessageT.message_id LEFT JOIN handle handleT ON handleT.ROWID = messageT.handle_id ORDER BY messageT.date")
		participants = set()
		for msg in messages:
			if msg[0] is None:
				print('skipping empty message', msg)
				continue
			message_proto = conversation.message.add()
			sender_name = msg[1]
			if msg[1] in id_name_map:
				sender_name = id_name_map[msg[1]]
			if msg[3]:
				sender_name = SELF_NAME
			# It look like lack of handle ID means self
			if msg[1] is None:
				sender_name = SELF_NAME
			message_proto.sender_name = sender_name
			message_proto.timestamp = msg[2]
			message_proto.content_type = chat_pb2.Message.CT_TEXT
			message_proto.content = msg[0]
			participants.add(sender_name)
		conversation.participant.extend(list(participants))
		# Overwrite group name with other party if this is a DM
		if len(conversation.participant) == 2:
			conversation.group_name = (conversation.participant[0] if conversation.participant[0] != SELF_NAME else conversation.participant[1])
			assert conversation.group_name != SELF_NAME, conversation.participant
		inbox.conversation.extend([conversation])
	conn.close()
	return inbox

def main():
	inbox = read_imessage(IMESSAGE_IMPORT_PATH)

	print(inbox)
	if USE_PBTXT:
		f = open(EXPORT_PATH_IMESSAGE + '.pbtxt', 'w')
		f.write(str(text_format.MessageToString(inbox)))
	else:
		f = open(EXPORT_PATH_IMESSAGE + '.pb', 'wb')
		f.write(inbox.SerializeToString())
	f.close()
	print('Wrote', len(inbox.conversation), 'conversations to', EXPORT_PATH_IMESSAGE)

if __name__ == '__main__':
	main()