#!/usr/bin/env bash -e

VENV=venv

if [ -d /usr/share/games/fortunes/de ] ; then
    cp -r /usr/share/games/fortunes/de .
fi

if [ ! -d "$VENV" ]
then

    PYTHON=`which python2`

    if [ ! -f $PYTHON ]
    then
        echo "could not find python"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip install -r requirements.txt
