from data_reader_facebook import read_facebook
from data_reader_imessage import read_imessage
from constants import *
import chat_pb2
import google.protobuf.text_format as text_format
import hashlib


def combine_inboxes(inbox_arr):
    assert len(inbox_arr) >= 1
    print('Combining inboxes')
    combined = chat_pb2.Inbox()
    parts_to_convs = {}
    for inbox in inbox_arr:
        if len(inbox.conversation) == 0:
            raise Exception(
                "No conversations to merge. Check if paths in constants.py are correct."
            )
        for conv in inbox.conversation:
            # Use participants to merge between iMessage and Facebook
            key = '+'.join(sorted(conv.participant))
            if key in parts_to_convs:
                # Merge messages
                parts_to_convs[key].message.extend(conv.message)
            else:
                parts_to_convs[key] = conv
    for conv in parts_to_convs.values():
        combined.conversation.add().CopyFrom(conv)
    # print(parts_to_convs.keys())
    # Assign IDs
    for conv in combined.conversation:
        key = '+'.join(sorted(conv.participant))
        conv.id = hashlib.sha1((key + HASH_SALT).encode()).hexdigest()
    return combined


def validate(inbox):
    for conv in inbox.conversation:
        actual_participants = set(map(lambda x: x.sender_name, conv.message))
        for part in actual_participants:
            if part not in conv.participant:
                raise Exception('Participants field is messed up', conv)


def main():
    inboxes = []
    if USE_FACEBOOK:
        print('Reading Facebook data')
        inboxes.append(read_facebook(FB_IMPORT_PATH))
    if USE_IMESSAGE:
        print('Reading iMessage data')
        inboxes.append(read_imessage(IMESSAGE_IMPORT_PATH))
    inbox = combine_inboxes(inboxes)
    validate(inbox)

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
