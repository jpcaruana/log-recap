#!/bin/bash
EXPECTED_ARGS=5

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: `basename $0` <start-time> <end-time> <file-to-parse> <one-word-email-title> <email-to>"
  echo "       with start-time and end-time in hh:mm[:ss] format"
  echo
  echo "       example: `basename $0` 11:00 11:59:59 /var/log/front.log front john@acme.com"
  exit 1
fi

START_TIME=$1
END_TIME=$2
FILE_NAME=$3
TITLE=$4
DEST=$5

all_file=/tmp/${TITLE}.log
python timegrep.py ${START_TIME} ${END_TIME} ${FILE_NAME} > ${all_file}
for level in "ERROR" "WARN"
do
	level_file=/tmp/${TITLE}-${level}.log
	cat << EOF > ${level_file}
Subject: [RECAP] [${level}] ${TITLE}
To: ${DEST}

EOF
	grep $level ${all_file} >> ${level_file}
	nb_lines=`wc -l ${level_file} | cut -d" " -f1`
	if [  "3" != $nb_lines ]
	then
		cat ${level_file} | ssmtp ${DEST}
	fi
	rm ${level_file}
done

rm ${all_file}
