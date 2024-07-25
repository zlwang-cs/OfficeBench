import os
import fire
import sys
from icalendar import Calendar, Event
from datetime import datetime


DEMO = (
    "delete an event from a user's calendar given the event summary:"
    "{'app': 'calendar', 'action': 'delete_event', 'user': [USER_NAME], 'summary': [EVENT_SUMMARY]}"
)


def construct_action(word_dir, args: dict, py_file_path='/apps/calendar_app/calendar_delete_event.py'):
    return f'python3 {py_file_path} --user {args["user"]} --summary "{args["summary"]}"'


def delete_event(user, summary):
    try:
        calendar_file = '/testbed/calendar/{}.ics'.format(user)
        calendar = Calendar.from_ical(calendar_file)

        for component in calendar.walk():
            if component.name == "VEVENT":
                if component.get('summary') == summary:
                    calendar.subcomponent.remove(component)
                    break
        with open(calendar_file, 'wb') as f:
            f.write(calendar.to_ical())
        return True
    except:
        return False


def main(user, summary):
    success = delete_event(user, summary)
    if success:
        observation = f"OBSERVATION: Successfully delete an event named {summary} from {user}'s calendar."
    else:
        observation = f"OBSERVATION: Failed to delete an event named {summary} from {user}'s calendar."
    return observation


if __name__ == '__main__':
    fire.Fire(main)