from data_reader_facebook import read_facebook
from data_reader_facebook import assign_conversation_ids
from data_reader_imessage import read_imessage
from constants import *
import chat_pb2
import google.protobuf.text_format as text_format

def combine_inboxes(inbox_arr):
	combined = chat_pb2.Inbox()
	parts_to_convs = {}
	for inbox in inbox_arr:
		for conv in inbox.conversation:
			key = '+'.join(sorted(conv.participant))
			if key in parts_to_convs:
				# Merge messages
				parts_to_convs[key].message.extend(conv.message)
			else:
				parts_to_convs[key] = conv
	for conv in parts_to_convs.values():
		combined.conversation.add().CopyFrom(conv)
		# assert conv.group_name != SELF_NAME, conv.participant
	print(parts_to_convs.keys())
	assign_conversation_ids(combined)
	return combined

def main():
	inbox_fb = read_facebook(FB_IMPORT_PATH)
	inbox_imessage = read_imessage(IMESSAGE_IMPORT_PATH)
	inbox = combine_inboxes([inbox_fb, inbox_imessage])

	# print(inbox)
	if USE_PBTXT:
		f = open(EXPORT_PATH + '.pbtxt', 'w')
		f.write(str(text_format.MessageToString(inbox)))
	else:
		f = open(EXPORT_PATH + '.pb', 'wb')
		f.write(inbox.SerializeToString())
	f.close()
	print('Wrote', len(inbox.conversation), 'conversations to', EXPORT_PATH)

if __name__ == '__main__':
	main()