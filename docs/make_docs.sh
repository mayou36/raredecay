#!/bin/bash

# get current directory name
pushd `dirname $0` > /dev/null
MAKE_DOCS_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
popd > /dev/null

# generate the ReST files
sphinx-apidoc -o $MAKE_DOCS_PATH/api $MAKE_DOCS_PATH/../raredecay  -fMeT && \
python $MAKE_DOCS_PATH/api/tools/change_headline.py $MAKE_DOCS_PATH/api/raredecay.* && \
make -C $MAKE_DOCS_PATH/api clean && make -C $MAKE_DOCS_PATH/api html -j4 && \
echo "Documentation succesfully build!" || echo "FAILED to build Documentation"
