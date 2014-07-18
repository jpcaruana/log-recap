#!/bin/bash

START_TIME=$1
END_TIME=$2
FILE_NAME=$3
TITLE=$4
DEST=$5

# TODO control input

all_file=/tmp/${TITLE}.log
python log.py ${START_TIME} ${END_TIME} ${FILE_NAME} > ${all_file}
for level in "ERROR" "WARN"
do
	level_file=/tmp/${TITLE}-${level}.log
	cat << EOF > ${level_file}
Subject: [RECAP] [${level}] ${TITLE}
To: ${DEST}

EOF
	grep $level ${all_file} >> ${level_file}
	cat ${level_file} | ssmtp ${DEST}
	rm ${level_file}
done

rm ${all_file}
