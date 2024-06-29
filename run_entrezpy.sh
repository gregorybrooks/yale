#!/usr/bin/bash
chmod a+x .venv/bin/activate
.venv/bin/activate
echo 'after activate'
cd yale
python pubmed.py $1 $2
echo 'after python'