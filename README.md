# unsub-me
Unsubscribe in bulk

Grabs the last 

Prints a list of unsubscribe URLs, which you can paste into a browser.

# Usage

    unsub-me.py [-h] -s SERVER -p PORT -u USER [-f FOLDER] [-c CACHE_DIR]
                   [-d DEBUG] [-n NDAYS]

SERVER = IMAP Server
PORT = IMAP Port
USER = IMAP User
FOLDER = IMAP Folder, Default:inbox
CACHE_DIR = Directory to cache emails, Default:".unsub-me"
DEBUG = Not implemented
NDAYS = Grab last n emails from server.

## Example
    python unsub-me.py -s imap.gmail.com -p 993 -u "my.email@gmail.com" -n 31

# Notes

I had to disable some security measures on gmail to get raw IMAP working. I enabled them again after use. 


