# Converscope
Analyze your conversations. Very much a WIP.

## Instructions
1. Download your Facebook info at https://www.facebook.com/dyi/. Select the JSON format and deselect everything except Messages.
2. Run `data_reader.py` to convert the Facebook archive into the Inbox/Conversation/Message protos defined in `chat.proto`
3. Run `analysis.py` to get metrics.

## TODO
- Web interface
- More metrics
- iMessage support
