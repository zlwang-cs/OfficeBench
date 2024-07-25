import os
import fire
import sys
from icalendar import Calendar, Event
from datetime import datetime


DEMO = (
    "create a new event to a user's calendar where the time format is '%Y-%m-%d %H:%M:%S':"
    "{'app': 'calendar', 'action': 'create_event', 'user': [USER_NAME], 'summary': [EVENT_SUMMARY], 'time_start': [EVENT_START_TIME], 'time_end': [EVENT_END_TIME]}"
)


def construct_action(word_dir, args: dict, py_file_path='/apps/calendar_app/calendar_create_event.py'):
    # return f'python3 {py_file_path} --user {args["user"]} --summary "{args["summary"]}" --time_start "{args["time_start"]}" --time_end "{args["time_end"]}"'
    if isinstance(args["user"], list):
        args["user"] = 'Multiple users'
    return "python3 {} --user '''{}''' --summary '{}' --time_start '{}' --time_end '{}'".format(
        py_file_path, args["user"], args["summary"], args["time_start"], args["time_end"]
    )


def create_event(user, summary, time_start, time_end):
    os.makedirs('/testbed/calendar', exist_ok=True)
    try:
        calendar_file = '/testbed/calendar/{}.ics'.format(user)
        if not os.path.exists(calendar_file):
            calendar = Calendar()
            calendar.add('prodid', '-//My Calendar Product//mxm.dk//')
            calendar.add('version', '2.0')
        else:
            calendar = Calendar.from_ical(open(calendar_file, 'rb').read())

        event = Event()
        event.add('summary', summary)
        event.add('dtstart', datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S'))
        event.add('dtend', datetime.strptime(time_end, '%Y-%m-%d %H:%M:%S'))
        event.add('dtstamp', datetime.now())
        event.add('description', 'This is a test event')
        event.add('location', 'Online')

        calendar.add_component(event)

        with open(calendar_file, 'wb') as f:
            f.write(calendar.to_ical())
        return True
    except Exception as e:
        print('!!!', e)
        return False


def main(user, summary, time_start, time_end):
    if user == 'Multiple users':
        observation = f"OBSERVATION: Failed to create a new event to {user}. Only support one user."
        return observation
    success = create_event(user, summary, time_start, time_end)
    if success:
        observation = f"OBSERVATION: Successfully create a new event to {user}'s calendar."
    else:
        observation = f"OBSERVATION: Failed to create a new event to {user}'s calendar."
    return observation


if __name__ == '__main__':
    fire.Fire(main)