#!/bin/bash

USER=vscode

# Reconfigure User id if set by user
if [ ! -z "${USER_UID}" ] && [ "${USER_UID}" != "`id -u ${USER}`" ] ; then
  echo -n "Update uid for user ${USER} with ${USER_UID}"
  usermod -u ${USER_UID} ${USER}
  echo "... updated"
else
  echo "skipping UID configuration"
fi

if [ -n "${USER_GID}" ] && [ "${USER_GID}" != "`id -g ${USER}`" ] ; then
  echo -n "Update gid for group ${USER} with ${USER_GID}"
  usermod -u ${USER_UID} ${USER}
  echo "... updated"
else
  echo "skipping GID configuration"
fi

#if [ -z "$SSH_AUTH_SOCK" ]; then
#   # Check for a currently running instance of the agent
#   RUNNING_AGENT="`ps -ax | grep 'ssh-agent -s' | grep -v grep | wc -l | tr -d '[:space:]'`"
#   if [ "$RUNNING_AGENT" = "0" ]; then
#        # Launch a new instance of the agent
#        ssh-agent -s &> $HOME/.ssh/ssh-agent
#   fi
#   eval `cat $HOME/.ssh/ssh-agent`
#fi

/bin/sh -c "while sleep 1000; do :; done"
