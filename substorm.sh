#!/bin/bash

if [ ! -d ~/.conda/envs/substorm-nlp ]; then
   echo "no conda env found, creating env..."
   conda env create -f substorm-nlp.yml
fi

echo "activate conda substorm-nlp env..."
source ~/anaconda3/etc/profile.d/conda.sh 
conda activate substorm-nlp

python -m spacy download en_core_web_sm

MULTILINE=$(pip list \
	   | grep -F en-rpa-simple)

echo "installed rpa-models..."
echo "${MULTILINE}"

if [ MULTILINE = "" ]
then
	echo "missing rpa-models, installing required packages..."
	pip install -r requirements.txt
	pwd
fi

