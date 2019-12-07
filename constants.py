DATA_DIR = './data/'

USE_PBTXT = False

# If true, does not store messages in the inbox file, and redacts names in the web app
STRIP_PII = False

# Data import/export

FB_IMPORT_PATH = DATA_DIR + '/facebook-daylenyang-json/messages'

IMESSAGE_IMPORT_PATH = '/Users/daylenyang/Library/Messages/chat.db'
CONTACTS_PATH = DATA_DIR + 'contacts.csv'
SELF_NAME = 'Daylen Yang'

EXPORT_PATH = DATA_DIR + '/inbox'
EXPORT_PATH_FB = DATA_DIR + '/inbox_fb'
EXPORT_PATH_IMESSAGE = DATA_DIR + '/inbox_imessage'

# Web app

HOME_MAX_CONVERSATIONS = 50
APP_PATH = 'converscope-react/build'