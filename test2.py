import win32evtlog

server = "localhost"
log_type = "Security"

hand = win32evtlog.OpenEventLog(server, log_type)

flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

events = True

while events:
    events = win32evtlog.ReadEventLog(hand, flags, 0)
    if events:
        for event in events:
            if event.EventID in [4660, 4663]:
                print("Time:", event.TimeGenerated)
                print("Event ID:", event.EventID)
                print("Source:", event.SourceName)
                print("-" * 50)