#!/bin/sh
if ! pgrep -f "python3 /home/user/[l]ogin_screen.py" > /dev/null; then
    python3 /home/user/login_screen.py &
fi
