import icalendar
import os
import fire

DEMO = (
    "list all events from a user's calendar: "
    "{'app': 'calendar', 'action': 'list_events', 'username': [USER_NAME]}"
)

def construct_action(word_dir, args: dict, py_file_path='/apps/calendar_app/calendar_list_events.py'):
    if isinstance(args["username"], list):
        args["username"] = 'Multiple users'
    return "python3 {} --username '''{}'''".format(py_file_path, args["username"])

def format_time(obj):
    if obj:
        return obj.dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return obj

def list_events(username):
    """
    List all events from a user's calendar.
    """
    calendar_file = f'/testbed/calendar/{username}.ics'
    if not os.path.exists(calendar_file):
        calendar = icalendar.Calendar()
        calendar.add('prodid', '-//My Calendar Product//mxm.dk//')
        calendar.add('version', '2.0')
        with open(calendar_file, 'wb') as f:
            f.write(calendar.to_ical())
    try:
        calendar = icalendar.Calendar.from_ical(open(calendar_file, 'rb').read())
        message = ''
        for component in calendar.walk():
            if component.name == "VEVENT":
                message += f'Summary: {component.get("summary")}\n'
                message += f'Start Time: {format_time(component.get("dtstart"))}\n'
                message += f'End Time: {format_time(component.get("dtend"))}\n'
                message += f'Description: {component.get("description")}\n'
                message += f'Location: {component.get("location")}\n'
                message += '-' * 50 + '\n'
        message = message.strip()
        return message
    except Exception as e:
        return 'Error: Failed to list events.'

def main(username):
    if username == 'Multiple users':
        observation = f"OBSERVATION: Failed to list events for {username}. Only support one user."
        return observation
    message = list_events(username)
    if message == 'Error: Failed to list events.':
        observation = f"OBSERVATION: Failed to list events for {username}."
    elif message == '':
        observation = f"OBSERVATION: No events found for {username}."
    else:
        observation = f"OBSERVATION: Successfully list events for {username}:\n{message}"
    return observation

if __name__ == '__main__':
    fire.Fire(main)


