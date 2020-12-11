#!/bin/bash
MULTILINE1=$(conda env list | grep -F rpa-tomorrow)

if [ "$MULTILINE1" = "" ]
then
    echo "no conda env found, creating env..."
    conda env create -f rpa-tomorrow.yml
fi

echo "activate conda RPA Tomorrow env..."
source ~/anaconda3/etc/profile.d/conda.sh 
conda activate rpa-tomorrow 

MULTILINE2=$(pip list | grep -F en-rpa-simple)

echo "installed rpa-models..."
echo "${MULTILINE2}"

if [ "$MULTILINE2" = "" ]
then
    echo "missing rpa-models, installing required packages..."
    pip install -r requirements.txt
    pwd
fi

