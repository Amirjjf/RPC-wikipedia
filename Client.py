#!/usr/bin/env python3
import xmlrpc.client
import datetime

def main():
    # Prompt for the server URL to allow connecting to different servers.
    server_url = input("Enter server URL (default http://localhost:8000): ").strip() or "http://localhost:8000"
    proxy = xmlrpc.client.ServerProxy(server_url, allow_none=True)
    
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
            result = proxy.add_note(topic, text, timestamp, search_term)
            print("Server response:", result)
        elif choice == "2":
            topic = input("Enter topic to retrieve notes: ").strip()
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
        elif choice == "3":
            print("Exiting client.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
