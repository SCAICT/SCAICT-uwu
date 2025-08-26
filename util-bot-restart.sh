#!/bin/bash

# XXX: Either add a trailing slash wherever this variable is used 
# (to increase flexibility), or
# ensure that this variable always has a trailing slash.
LOG_DIR="/var/log/Bot_uwu"

# For developers
# LOG_DIR="./log/bot"

TIMESTAMP="$(date +%Y-%m-%dT%H-%M-%S)"

START_COMMAND="python3 ./main.py"

# Simulate Ctrl-C (SIGINT) instead of SIGKILL to exit as safely as possible
screen -S bot -X stuff "\003"

mkdir -p "${LOG_DIR}" || exit 1
test -w "${LOG_DIR}" || { \
    echo "Please make sure you have permission to write log file to ${LOG_DIR}"; \
    exit 1
}

echo "Log file will be written to ${LOG_DIR}/Log_${TIMESTAMP}.log"
echo "HINT: If you see [screen is terminating], the process have exited"
echo "HINT: 如果你看見 [screen is terminating], 那麼很遺憾的這個處理程序並未正常啟動"

# Start a process with screen
# To avoid someone who didn't know how to detach the screen
screen -S bot -L -Logfile "${LOG_DIR}/Log_${TIMESTAMP}.log" \
    bash -c "echo TIPS: You can detach with Ctrl-A D;
        echo which won\'t kill the process;
        echo and you can reattach to observer the output and interact with util-bot-reattach.sh; \
        echo TIPS: 您可以透過 Ctrl-A D 脫離這個界面，並且不會殺死這個處理程序;
        echo 之後也可以透過 util-bot-reattach.sh 重新回來觀察輸出與互動;
        ${START_COMMAND}"
