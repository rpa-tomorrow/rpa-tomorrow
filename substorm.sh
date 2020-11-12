#!/bin/bash
MULTILINE1=$(conda env list | grep -F substorm-nlp)

if [ "$MULTILINE1" = "" ]
then
    echo "no conda env found, creating env..."
    conda env create -f substorm-nlp.yml
fi

echo "activate conda substorm-nlp env..."
source ~/anaconda3/etc/profile.d/conda.sh 
conda activate substorm-nlp

spacy download xx_ent_wiki_sm

MULTILINE2=$(pip list | grep -F en-rpa-simple)

echo "installed rpa-models..."
echo "${MULTILINE2}"

if [ "$MULTILINE2" = "" ]
then
    echo "missing rpa-models, installing required packages..."
    pip install -r requirements.txt
    pwd
fi

