# log-recap

Parse your logs and send them via email.

This is a pretty simple/crude script, but it does the job for me. Thanks to Dennis Williamson who wrote the timegrep.py script in response to http://serverfault.com/questions/101744/fast-extraction-of-a-time-range-from-syslog-logfile

I use it to parse my production logs every hour.

## Prerequisites
* python >= 2.6
* a configured ssmtp (https://wiki.debian.org/sSMTP)
* enought disk space on your loghost

## Install
Just copy these files under whatever forder you like. I personnaly use /opt/log-recap

## How to use it
````
Usage: recap.sh <start-time> <end-time> <file-to-parse> <one-word-email-title> <email-to>
       with start-time and end-time in hh:mm[:ss] format

       example: recap.sh 11:00 11:59:59 /var/log/front.log front john@acme.com
````

## Cron
For every hour, parsing logs on several files for the last hour

My crontab looks like this:

````
# m h  dom mon dow   command
10 * * * * cd /opt/log-recap && ./last_hour.sh
````

And my last_hour.sh file looks like this:

````
#!/bin/bash
hour=`date +\%H -d "-1 hour"`
begin=${hour}:00:00
end=${hour}:59:59

./recap.sh ${begin} ${end} /var/log/front.log front john@acme.com
./recap.sh ${begin} ${end} /var/log/back.log back john@acme.com
````
