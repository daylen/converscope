#######################
# Things to configure #
#######################

DATA_DIR = './data/'

# Facebook configuration
# Set to true if you have Facebook data
USE_FACEBOOK = True
# Inside this folder should be folders like `inbox`, `archived_threads`,
# `filtered_threads`, `message_requests` etc.
FB_IMPORT_PATH = DATA_DIR + '/fb_messages'

# iMessage configuration
# Set to true if you have iMessage data
USE_IMESSAGE = True
IMESSAGE_IMPORT_PATH = DATA_DIR + '/chat.db'
CONTACTS_PATH = DATA_DIR + 'contacts.csv'
SELF_NAME = 'Daylen Yang'

# Unix times. You can fill these in by using WolframAlpha, e.g. "june 27, 2005 unix time"
HIGH_SCHOOL_GRAD_TS = 1370070000 # ~2013
COLLEGE_GRAD_TS = 1496300400 # ~2017

#####################
# Optional settings #
#####################

# Disable if page loads are too slow (i.e. you have a lot of messages)
USE_TFIDF = True

# Redacts names in the web app and hides the "blast from the past" feature
STRIP_PII = False

# If you want to deploy this app publicly, use a salt for the SHA-1 hashes to prevent dictionary attacks
HASH_SALT = ''

# For streaks to be calculated correctly
TIME_ZONE = 'America/Los_Angeles'

# Number of conversations to display on homepage of web app
HOME_MAX_CONVERSATIONS = 20

#################
# Do not change #
#################

APP_PATH = 'converscope-react/build'
USE_PBTXT = False
EXPORT_PATH = DATA_DIR + '/inbox'
EXPORT_PATH_FB = DATA_DIR + '/inbox_fb'
EXPORT_PATH_IMESSAGE = DATA_DIR + '/inbox_imessage'