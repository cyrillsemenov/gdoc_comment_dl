https = r"(?:https?)\:\/\/"
www = r"(?:www.|[a-zA-Z.]+)?"
host = r"[a-zA-Z0-9\-\.]+"
tld = r"\.(?:\w)?"
port = r"(?:\:[0-9][0-9]{0,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?"
path = r"(?:[a-zA-Z0-9\-\.\/_]+)?"
query = r"(?:\?$|[a-zA-Z0-9\.\,\;\?\'\+&%\$\=~_\-\*]+)?"
# BASED ON https://regex101.com/library/rQjzDU
URL = https + www + host + tld + port + path + query
YT_LINK = https + www + r"(?:youtu\.be\/|youtube\.com\/watch\?v=)[a-zA-Z0-9_-]{11}"
TC = r"\b(?:\d?\d ?[:—–−-] ?\d\d)(?:(?: ?[:—–−-] ?)(?:\d?\d ?[:—–−-] ?\d\d))?(?:(?: ?\+ ?)(?:\d?\d ?[:—–−-] ?\d\d)(?:(?: ?[:—–−-] ?)(?:\d?\d ?[:—–−-] ?\d\d))?)?"
GOOGLE_ID = r"[a-zA-Z0-9-_]{44}"
GOOGLE_DOC = https + r"docs\.google\.com\/document\/d\/" + GOOGLE_ID + "\/?"
