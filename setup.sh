#!/usr/bin/env bash -e

PYTHON=`which python3`
VENV=venv

if [ -f "$PYTHON" ]
then

    if [ ! -d $VENV ]
    then
        # Create a virtual environment if it doesn't exist.
        $PYTHON -m venv $VENV
    else
        if [ -e $VENV/bin/python2 ]
        then
            # If a Python2 environment exists, delete it first
            # before creating a new Python 3 virtual environment.
            rm -r $VENV
            $PYTHON -m venv $VENV
        fi
    fi

    # Activate the virtual environment and install requirements.
    . $VENV/bin/activate
    pip3 install -q -r requirements.txt

else
    >&2 echo "Cannot find Python 3. Please install it."
fi

if [ -d /usr/share/games/fortunes/de ] ; then
    cp -r /usr/share/games/fortunes/de .
else
    >&2 echo "Please install the package 'fortunes-de'."
fi


if [ -f /usr/share/snips/assistant/snippets/domi.Witze_\&_Glueckskekse/config.ini ]
then
    cp /usr/share/snips/assistant/snippets/domi.Witze_\&_Glueckskekse/config.ini config.ini
else
    cp config.ini.default config.ini
fi
