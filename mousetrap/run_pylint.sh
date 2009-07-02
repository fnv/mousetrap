#!/bin/bash
#
# SCRIPT TAKEN FROM ORCA PROJECT
#
# Script to run pylint on the MouseTrap sources you've modified or added.
# See http://live.gnome.org/MouseTrap/Pylint for more info.
#
exec_prefix=/usr/local
INSTALL_DIR=/usr/lib/python2.6/dist-packages
if [ "x$*" == "x" ]
then
    if [ -d .git ]
    then
        FILES=`git status | egrep 'modified:|new file:' | grep '[.]py$' | awk '{ print $NF }'`
    else if [ -d .svn ]
        FILES=`svn stat src/mouseTrap | egrep "^M|^A" | grep "[.]py$" | awk '{ print $2 }'`
    fi
else
    FILES="$*"
fi
FILES=`echo $FILES | sed 's^src/mousetrap/^^g'`
echo Thank you for your attention to quality
for foo in $FILES
do
    echo
    OUTPUT_FILE=`dirname $foo`/`basename $foo .py`.pylint
    OUTPUT_FILE=`echo $OUTPUT_FILE | sed 's~^./~~' | sed 's^/^.^g'`
    echo Checking $foo, sending output to $OUTPUT_FILE
    PYTHONPATH=$INSTALL_DIR:$PYTHONPATH pylint --init-hook="import pyatspi" $INSTALL_DIR/mousetrap/$foo > $OUTPUT_FILE 2>&1
    grep "code has been rated" $OUTPUT_FILE | cut -f1 -d\( \
    | sed "s/.pylint:Your code has been rated at / /" \
    | sed "s^/10^^" | sort -n -k 2,2
done
