
def main():
    creds = authenticate()
    if not creds:
        print("Authentifizierung fehlgeschlagen.")
        return

    try:
        service = build("calendar", "v3", credentials=creds)

        #create_event(a,b,c,d..)
        #modify_event(a,b,c,d..)
        #delete_event(a,b,c)
        #list_events(a,b,c,d)
        create_event(
            service=service,
            summary="Team Meeting",
            start_time="2025-04-07T10:00:00",
            end_time="2025-04-07T11:00:00",
            description="Besprechung der Projektfortschritte",
            location="Konferenzraum A",
            timezone="Europe/Berlin",
            #attendees=["john.doe@example.com", "jane.doe@example.com"],
            #reminders=[
            #    {'method': 'email', 'minutes': 30},
            #    {'method': 'popup', 'minutes': 10}
            #],
            #recurrence=['RRULE:FREQ=WEEKLY;COUNT=5']
        )



    except Exception as e:
        print(f"Fehler bei der API-Nutzung: {e}")


if __name__ == "__main__":
    main()
