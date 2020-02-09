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
        if len(inbox.conversation) == 0:
            raise Exception("No conversations to merge")
        for conv in inbox.conversation:
            key = '+'.join(sorted(conv.participant))
            if key in parts_to_convs:
                # Merge messages
                parts_to_convs[key].message.extend(conv.message)
            else:
                parts_to_convs[key] = conv
    for conv in parts_to_convs.values():
        combined.conversation.add().CopyFrom(conv)
    print(parts_to_convs.keys())
    assign_conversation_ids(combined)
    return combined


def validate(inbox):
    for conv in inbox.conversation:
        actual_participants = set(map(lambda x: x.sender_name, conv.message))
        for part in actual_participants:
            if part not in conv.participant:
                raise Exception('Participants field is messed up', conv)


def main():
    inbox_fb = read_facebook(FB_IMPORT_PATH)
    validate(inbox_fb)
    inbox_imessage = read_imessage(IMESSAGE_IMPORT_PATH)
    validate(inbox_imessage)
    inbox = combine_inboxes([inbox_fb, inbox_imessage])
    validate(inbox)
    if STRIP_PII:
        for c in inbox.conversation:
            for m in c.message:
                m.content = ""
                del m.media_uri[:]

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
