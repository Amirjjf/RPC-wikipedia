#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import requests
import argparse

DB_FILE = "notes.xml"

def init_db(db_file):

    if not os.path.exists(db_file):
        root = ET.Element("data")
        tree = ET.ElementTree(root)
        tree.write(db_file)

def add_note(topic, text, timestamp, search_term="", db_file=DB_FILE):

    wikipedia_link = ""
    wikipedia_extract = ""
    if search_term:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": search_term,
            "limit": "1",
            "namespace": "0",
            "format": "json"
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            if data and len(data) >= 4 and data[3]:
                wikipedia_link = data[3][0]
                # Retrieve page title from suggestions to use for extracting content.
                if data[1] and data[1][0]:
                    page_title = data[1][0]
                    params_extract = {
                        "action": "query",
                        "prop": "extracts",
                        "exintro": True,
                        "explaintext": True,
                        "titles": page_title,
                        "format": "json"
                    }
                    extract_response = requests.get(url, params=params_extract, timeout=5)
                    extract_data = extract_response.json()
                    pages = extract_data.get("query", {}).get("pages", {})
                    if pages:
                        page = next(iter(pages.values()))
                        wikipedia_extract = page.get("extract", "")
        except Exception as e:
            print("Wikipedia API request failed:", e)
    
    # Load the XML database
    tree = ET.parse(db_file)
    root = tree.getroot()
    
    # Find or create the topic element
    topic_elem = None
    for t in root.findall('topic'):
        if t.get('name') == topic:
            topic_elem = t
            break
    if topic_elem is None:
        topic_elem = ET.SubElement(root, "topic", name=topic)
    
    # Create a new note element with a 'name' attribute to mimic the example structure.
    note_name = f"{topic} note {timestamp}"
    note_elem = ET.SubElement(topic_elem, "note", name=note_name)
    
    text_elem = ET.SubElement(note_elem, "text")
    text_elem.text = text
    timestamp_elem = ET.SubElement(note_elem, "timestamp")
    timestamp_elem.text = timestamp
    
    if wikipedia_link:
        wiki_elem = ET.SubElement(note_elem, "wikipedia_link")
        wiki_elem.text = wikipedia_link
        if wikipedia_extract:
            extract_elem = ET.SubElement(note_elem, "wikipedia_extract")
            extract_elem.text = wikipedia_extract
    
    tree.write(db_file)
    message = f"Note added under topic '{topic}'"
    if wikipedia_link:
        message += f" with Wikipedia link: {wikipedia_link}"
    return message

def get_notes(topic, db_file=DB_FILE):

    if not os.path.exists(db_file):
        return "No database file found."
    
    tree = ET.parse(db_file)
    root = tree.getroot()
    
    notes_list = []
    for t in root.findall('topic'):
        if t.get('name') == topic:
            for note in t.findall('note'):
                note_data = {}
                text_elem = note.find('text')
                ts_elem = note.find('timestamp')
                wiki_elem = note.find('wikipedia_link')
                extract_elem = note.find('wikipedia_extract')
                note_data["text"] = text_elem.text if text_elem is not None else ""
                note_data["timestamp"] = ts_elem.text if ts_elem is not None else ""
                note_data["wikipedia_link"] = wiki_elem.text if wiki_elem is not None else ""
                note_data["wikipedia_extract"] = extract_elem.text if extract_elem is not None else ""
                notes_list.append(note_data)
            break
    return notes_list

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

def main():
    global DB_FILE  # Declare global variable at the very start of the function
    parser = argparse.ArgumentParser(description="XML-RPC Notebook Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--db", type=str, default=DB_FILE, help="XML database file")
    args = parser.parse_args()
    
    DB_FILE = args.db
    
    init_db(DB_FILE)
    server = ThreadedXMLRPCServer(("localhost", args.port), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()
    # Use lambda wrappers to pass the current DB_FILE value.
    server.register_function(lambda topic, text, timestamp, search_term="": add_note(topic, text, timestamp, search_term, DB_FILE), "add_note")
    server.register_function(lambda topic: get_notes(topic, DB_FILE), "get_notes")
    
    print(f"Server is running on port {args.port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server is shutting down.")

if __name__ == "__main__":
    main()
