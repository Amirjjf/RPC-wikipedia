#!/usr/bin/env python3
import xmlrpc.client
import datetime

def main():
    server_url = input("Enter server URL (default http://localhost:8000): ").strip() or "http://localhost:8000"

    try:
        # Try to connect to the server
        proxy = xmlrpc.client.ServerProxy(server_url, allow_none=True)
        # Test if the server is reachable
        proxy.system.listMethods()  
    except (ConnectionRefusedError, xmlrpc.client.ProtocolError):
        print("\nERROR: Could not connect to the server. Please make sure the server is running.")
        return  

    while True:
        print("\n--- Notebook Client ---")
        print("1. Add a note")
        print("2. Get notes by topic")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()
        
        if choice == "1":
            topic = input("Enter topic: ").strip()
            text = input("Enter note text: ").strip()
            timestamp = datetime.datetime.now().isoformat()
            search_term = input("Enter search term for Wikipedia (or leave blank): ").strip()
            
            try:
                result = proxy.add_note(topic, text, timestamp, search_term)
                print("Server response:", result)
            except (ConnectionRefusedError, xmlrpc.client.Fault, xmlrpc.client.ProtocolError):
                print("\nERROR: Could not connect to the server. Please make sure the server is running.")
                return
        elif choice == "2":
            topic = input("Enter topic to retrieve notes: ").strip()
            try:
                notes = proxy.get_notes(topic)
                if isinstance(notes, str):
                    print("Server response:", notes)
                else:
                    if not notes:
                        print("No notes found for this topic.")
                    else:
                        print(f"Notes for topic '{topic}':")
                        for note in notes:
                            print("----")
                            print("Text:", note.get("text"))
                            print("Timestamp:", note.get("timestamp"))
                            if note.get("wikipedia_link"):
                                print("Wikipedia link:", note.get("wikipedia_link"))
                            if note.get("wikipedia_extract"):
                                print("Wikipedia extract:", note.get("wikipedia_extract"))
            except (ConnectionRefusedError, xmlrpc.client.Fault, xmlrpc.client.ProtocolError):
                print("\nERROR: Could not connect to the server. Please make sure the server is running.")
                return
        elif choice == "3":
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
