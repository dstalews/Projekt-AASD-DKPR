#!/bin/sh
prosodyctl register "datacollectorID$1" localhost $2
prosodyctl register "healthanalyzerID$1" localhost $2
prosodyctl register "decisionmakerID$1" localhost $2
prosodyctl register "actionexecutorID$1" localhost $2

sudo chmod 777 -R /var/lib/prosody
exit 0