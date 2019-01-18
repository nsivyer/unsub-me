#!/usr/bin/env python
import os,sys
import glob,re
import imaplib,email,getpass,argparse
import datetime,dateutil.parser,time
import email.header

script_name = os.path.splitext(__file__)[0]

parser = argparse.ArgumentParser(description='unsub-me.py')
parser.add_argument('-s', '--server', help='IMAP Server eg. imap.gmail.com' ,required=True)
parser.add_argument('-p', '--port', help='IMAP Server port eg. 993' ,required=True)
parser.add_argument('-u', '--user', help='Usename' ,required=True)
parser.add_argument('-f', '--folder', help='Folder to search.',default="inbox")
parser.add_argument('-c', '--cache-dir', help='Local directory to cache emails',default="." + script_name)
parser.add_argument('-d', '--debug', help='Switch on debugging')
parser.add_argument('-n', '--ndays', help='Number of days to grab from mailbox',default=31)
args = parser.parse_args()

imap_cachedir = args.cache_dir
user = args.user
check_days = args.ndays
server = args.server
port = args.port
folder = args.folder
emails = []
unsub_urls = []
unsub_doms = []

password = getpass.getpass("Please enter the password for " +  server + ":\n")

suspected_words=['unsubscribe']


if not os.path.exists(imap_cachedir):
    os.mkdir(imap_cachedir)

# decode headers
def decode_header(t):
    dh = email.header.decode_header(t)
    default_charset = 'ISO-8859-1'
    r = ''.join([ unicode(t[0], t[1] or default_charset) for t in dh ])
    return r.encode('utf-8')

# extract meaningful parts of e-mails
def email_to_string(msg):
    parts = []
    for part in msg.walk():
        if not part.get_content_maintype() == 'text':
            continue
        parts.append(part.get_payload(decode=True))
    return "\n".join(parts)

try:
    print "Looking for unsubscribe links from the past %s days." % check_days
    mail = imaplib.IMAP4_SSL(server,port)
    mail.login(user.strip(), password.strip())
    mail.list()
    mail.select(folder,readonly=True )
    date = (datetime.date.today() - datetime.timedelta(int(check_days))).strftime("%d-%b-%Y")
    typ, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=date))
    email_uids = data[0].split()
    print "Found %s emails. Fetching:" % len(email_uids)
    for emailid in email_uids:
        email_cachefile = imap_cachedir+"/o_"+emailid
        email_text = "Unfetched"
        if os.path.isfile(email_cachefile) and os.stat(email_cachefile).st_size > 0:
            with open(email_cachefile, 'r') as cachefile:
                email_text = cachefile.read()
            sys.stdout.write("+")
        else:
            typ, data = mail.uid('fetch', emailid, '(RFC822)')
            sys.stdout.write(".")
            email_text = data[0][1]
            with open(email_cachefile + '.tmp', 'w') as cachefile:
                cachefile.write(email_text)
            os.rename(email_cachefile + '.tmp', email_cachefile)
        sys.stdout.flush()
        emails.append(email.message_from_string(email_text))
    mail.close()
    mail.logout()
    print " All fetched."
    emails.reverse()
except EOFError:
    print "Error while fetching emails"
    sys.exit(1)


for message in emails:
    message_decoded_from    = decode_header(message['From'])
    message_decoded_subject = decode_header(message['Subject'])
    message_body_lower      = email_to_string(message).lower()
    message_subject_lower   = message_decoded_subject.lower()

    urls = re.findall(r'href=[\'"]?([^\'" >]+)', message_body_lower)

    for url in urls:
        if any([word in url for word in suspected_words]):
            unsub_urls.append(url)
            unsub_doms.append(url.split("//")[-1].split("/")[0])

#print("\n".join( x for x in set(unsub_doms) ) )
print("\n".join( x for x in set(unsub_urls) ) )
#print([[x,unsub_doms.count(x)] for x in set(unsub_doms)])


    
