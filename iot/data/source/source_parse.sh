#!/usr/bin/env bash
file_date=$1
if [ "${file_date}" ]; then
    flag="."
else
    flag=""
fi

# shellcheck disable=SC2006
root_path=`pwd`
servers=(10.200.22.217 10.200.26.2)
for i in ${servers[*]}; do
    if [ "$i" == "${servers[0]}" ]; then #判断字符串是否相等，注意前后要有空格，否则变为赋值语句
        # shellcheck disable=SC2092
        `grep "'message\': \'IC auth consumed time" "${root_path}"/"$i"/app.log${flag}${file_date} > ../"$i"${flag}${file_date}_in_data`
    fi
    if [ "$i" == "${servers[1]}" ]; then
        #echo  "${root_path}"/"$i"/app.log${flag}"${file_date}"
        `grep "'message\': \'IC auth consumed time" "${root_path}"/"$i"/app.log${flag}${file_date} > ../"$i"${flag}${file_date}_in_data`
    fi
done

