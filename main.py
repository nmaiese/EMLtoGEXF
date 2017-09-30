import networkx as nx
import os, glob, email, re
import datetime

email_regex = r'[\w\.-]+@[\w\.-]+'


def caption(origin):
    """Extracts: To, From, Sgraph.addubject and Date from email.Message() or mailbox.Message()
    origin -- Message() object
    Returns tuple(From, To, Subject, Date)
    If message doesn't contain one/more of them, the empty strings will be returned.
    """
    metadata = {}

    if "date" in origin:
        metadata = {"date": origin["date"].strip()}

    if "from" in origin:
        metadata["from"] = origin["from"].strip()

    if "to" in origin:
        metadata["to"] = origin["to"].strip()

    if "cc" in origin:
        metadata["cc"] = origin["cc"].strip()

    if "subject" in origin:
        metadata["subject"] = origin["subject"].strip()

    return metadata


def uniqe(input):
    output = []
    [output.append(x) for x in input if x not in output]
    return output


def extract_meta_fields_from_email(file):
    """Extract meta fields from email. Take an eml file as input and extract
    the "to","from","subject" and "date", field from emails"""

    with open(file, 'r', encoding='ISO-8859-1') as f:
        text = email.message_from_file(f)
        return caption(text)


def generate_graph_object(fields):
    object_graph = []
    date_check = []

    for f in fields:
        if "date" in f:
            meta_date = datetime.datetime.strptime(f["date"][:-6], "%a, %d %b %Y %H:%M:%S")
            meta_date = "{:4d}-{:02d}-{:02d}".format(meta_date.year, meta_date.month, meta_date.day)
            if meta_date not in date_check:
                date_check.append(meta_date)

        else:
            meta_date = ""

        if "from" in f:
            if type(f["from"]) == str:
                meta_from = re.findall(email_regex, f["from"].lower())
                if meta_from != []:
                    meta_from = meta_from[0]
                else:
                    meta_from = ""

            else:
                meta_from = re.findall(email_regex, f["from"].lower())[0]
        else:
            meta_from = ""

        if "to" in f:
            meta_to = re.findall(email_regex, f["to"].lower())
        else:
            meta_to = [""]

        meta_to = uniqe(meta_to)

        for address in meta_to:
            object_graph.append({"from": meta_from, "to": address, "date": meta_date})

        if "cc" in f:
            meta_cc = re.findall(email_regex, f["cc"].lower())
            for address in meta_cc:
                object_graph.append({"from": meta_from, "to": address, "date": meta_date})

    return object_graph


# path of EML files folder
dir_path = "/Users/aniello.maiese/Desktop/MEC/Old Desktop/email-bck/eml"

# collect all emails in a list
email_pattern = os.path.join(dir_path, '*.eml')
emails = glob.glob(email_pattern)

# extract fields
meta_fields = [extract_meta_fields_from_email(x) for x in emails]

# generate graph object
graph = generate_graph_object(meta_fields)

G = nx.MultiDiGraph()

# add edges
for i, c in enumerate(graph):
    G.add_edge(u=c['from'], v=c['to'], weight=1, key=i, date=c['date'])

# write output
nx.write_gexf(G, 'my_emails.gexf')

