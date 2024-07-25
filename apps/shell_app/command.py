# This is a placeholder python file for os commands. We directly call os commands from the docker so no need to use this python file. 
# We will put some templates here for os commands.


# DEMO = (
#    'You can run a shell command by calling `command` with 1 argument.\n'
#    '1. The shell command to run: command: str\n'
#    "You can call it by: {'app': 'shell', 'action': 'command', 'command': ...}" 
# )

DEMO = (
   "run a shell command: "
   "{'app': 'shell', 'action': 'command', 'command': [THE_COMMAND_YOU_WISH_TO_RUN]}"
)

def construct_action(work_dir, args: dict):
    return args["command"]


