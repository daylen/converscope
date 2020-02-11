DATA_DIR = './data/'

USE_PBTXT = False

# If true, redacts names in the web app
STRIP_PII = False
HASH_SALT = ''

# Data import/export

FB_IMPORT_PATH = DATA_DIR + '/fb-dump-2020-01-26/messages'

IMESSAGE_IMPORT_PATH = DATA_DIR + '/chat.db'
CONTACTS_PATH = DATA_DIR + 'contacts.csv'
SELF_NAME = 'Daylen Yang'

EXPORT_PATH = DATA_DIR + '/inbox'
EXPORT_PATH_FB = DATA_DIR + '/inbox_fb'
EXPORT_PATH_IMESSAGE = DATA_DIR + '/inbox_imessage'

# Web app
TIME_ZONE = 'America/Los_Angeles'
HOME_MAX_CONVERSATIONS = 20
APP_PATH = 'converscope-react/build'

# Time ranges. You can fill these in by using WolframAlpha

HIGH_SCHOOL_GRAD_TS = 1370070000
COLLEGE_GRAD_TS = 1496300400