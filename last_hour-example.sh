#!/bin/bash
hour=`date +\%H -d "-1 hour"`
begin=${hour}:00:00
end=${hour}:59:59

./recap.sh ${begin} ${end} /var/log/front.log front john@acme.com
./recap.sh ${begin} ${end} /var/log/back.log back john@acme.com
