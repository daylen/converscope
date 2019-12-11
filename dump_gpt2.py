from analysis import InboxAnalyzer
from constants import *
import chat_pb2
import random
import sys


def conv_to_string(conv, ts_range):
    in_range = filter(
        lambda x: x.timestamp >= ts_range[0] and x.timestamp < ts_range[1] and x
        .content_type == chat_pb2.Message.CT_TEXT, conv.message)
    ordered = sorted(in_range, key=lambda x: x.timestamp)
    transcript = ''
    for message in ordered:
        if 'Say hi to your new Facebook friend' in message.content:
            continue
        transcript += str.upper(
            message.sender_name) + ': ' + message.content + '\n\n'
    return transcript, len(ordered)


def dump_for_gpt2(ia, ts_range=(0, sys.maxsize), fname_prefix=''):
    TRAIN_PERCENT = 0.82

    train_txt = ''
    test_txt = ''
    train_count, test_count = 0, 0
    for c_metadata in ia.get_conversations():
        conv = ia.get_conversation(c_metadata.id)
        transcript, count = conv_to_string(conv, ts_range)
        # Do not include really short conversations
        if count < 5:
            continue
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
    with open('./' + fname_prefix + 'train.txt', 'w') as f:
        f.write(train_txt)
    with open('./' + fname_prefix + 'test.txt', 'w') as f:
        f.write(test_txt)
    print(train_count + test_count, 'messages',
          (train_count) / float(train_count + test_count), ts_range,
          fname_prefix)


def main():
    """
	Dump everything to a text file for finetuning GPT-2.
	"""
    random.seed(42)
    TS_SPLIT = 1433131200 + (1.5 * 60 * 60 * 24 * 365)

    ia = InboxAnalyzer()
    dump_for_gpt2(ia, ts_range=(0, sys.maxsize), fname_prefix='all_data_')
    # dump_for_gpt2(ia, ts_range=(0, TS_SPLIT), fname_prefix='dec2010_nov2016')
    # dump_for_gpt2(ia,
    #               ts_range=(TS_SPLIT, sys.maxsize),
    #               fname_prefix='nov2016_dec2019')


if __name__ == '__main__':
    main()
