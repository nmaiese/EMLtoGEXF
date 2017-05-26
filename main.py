import email
import glob
import os
from tqdm import tqdm
from optparse import OptionParser
import os.path
import re
import sys,pprint
import datetime
import json

sys.path.append('../gexf')

from gexf import Gexf, GexfImport

ROOTDIR = r'C:\Users\aniello.maiese\Desktop\email-bck\eml'


regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))

regex_simple = r'[\w\.-]+@[\w\.-]+'

def file_to_str(filename):
    """Returns the contents of filename as a string."""
    with open(filename) as f:
        return f.read().lower() # Case is lowered to prevent regex mismatches.

def get_emails(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))




def caption (origin):
    """Extracts: To, From, Sgraph.addubject and Date from email.Message() or mailbox.Message()
    origin -- Message() object
    Returns tuple(From, To, Subject, Date)
    If message doesn't contain one/more of them, the empty strings will be returned.
    """
    metadata = {}

    if origin.has_key("date"):
        metadata = {"date" : origin["date"].strip()}

    if origin.has_key("from"):
        metadata["from"] = origin["from"].strip()

    if origin.has_key("to"):
        metadata["to"] = origin["to"].strip()

    if origin.has_key("cc"):
        metadata["cc"] = origin["cc"].strip()

    if origin.has_key("subject"):
        metadata["subject"] = origin["subject"].strip()

    return metadata

def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output


email_pattern = os.path.join(ROOTDIR, '*.eml')
emails = glob.glob(email_pattern)

emails_list = []
for elem in tqdm(emails):
    f = open(elem,"rb")
    text = email.message_from_file(f)
    metadata  = caption(text)
    emails_list.append(metadata)


object_graph = []
date_check = []

for f in tqdm(emails_list):

    if f.has_key("date"):
        meta_date = datetime.datetime.strptime(f["date"][:-6], "%a, %d %b %Y %H:%M:%S")
        #meta_date = str(meta_date.year) + "/" + str(meta_date.month) + "/" + str(meta_date.day)
        meta_date = "{:4d}-{:02d}-{:02d}".format(meta_date.year,meta_date.month,meta_date.day)
        if meta_date not in date_check:
            print meta_date
            date_check.append(meta_date)

    else:
        meta_date = "EMPTY0"

    if f.has_key("from"):
        if type(f["from"]) == str:
            meta_from = re.findall(regex_simple, f["from"])
            if meta_from != []:
                meta_from = meta_from[0]
            else:
                meta_from = "EMPTY0"

        else:
            meta_from = re.findall(regex_simple, f["from"])[0]
    else:
        meta_from = "EMPTY0"

    if f.has_key("to"):
        meta_to = re.findall(regex_simple, f["to"])
    else:
       meta_to = ["EMPTY0"]
    meta_to = uniq(meta_to)
    for address in meta_to:
        object_graph.append({"from": meta_from, "to": address, "date":meta_date})
    if f.has_key("cc"):
        meta_cc = re.findall(regex_simple, f["cc"])
        for address in meta_cc:
            object_graph.append({"from": meta_from, "to": address, "date": meta_date})


gexf = Gexf("Aniello Maiese","Email Works")
graph=gexf.addGraph("directed","dynamic","sample")



id = 1

nodes = []

for elem in object_graph:
    if elem["from"] not in nodes:
        graph.addNode(elem["from"],elem["from"],elem["date"])
        nodes.append(elem["from"])
    if elem["to"] not in nodes:
        graph.addNode(elem["to"], elem["to"],elem["date"])
        nodes.append(elem["to"])
    graph.addEdge(id, elem["from"],elem["to"],1,elem["date"])
    id += 1

output_file = open("myemail_dynamics_connections.gexf", "w")
gexf.write(output_file)

