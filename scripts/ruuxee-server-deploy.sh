#!/bin/bash
# encoding = utf-8 without BOM
#
# Jan 15, 1025, created by fuzhou.chen@ruuxee.com
# This is a script to install ruuxee module
#
# Command line format:
#     ruuxee-deploy.sh <full-path>
#
#

# Define error codes.
STATUS_OK=0
STATUS_ERROR_VIRTUALENV_NOT_FOUND=1
STATUS_ERROR_DEPLOYMENT_ROOT_UNDEFINED=2
STATUS_ERROR_DEPLOYMENT_ROOT_ALREADY_EXISTS=3
STATUS_ERROR_DEPENDENCY_FILE_NOT_SPECIFIED=4
STATUS_ERROR_COMPILER_NOT_INSTALLED=5
STATUS_ERROR_SYSTEM_NOT_SUPPORTED=6

function fullpath {
    # Support UNIX/Linux/Mac only
    GIVENPATH=$1
    CHECK=`echo ${GIVENPATH} | grep "^\\/"`
    if [ -z "$CHECK" ]; then
        echo `pwd`/${GIVENPATH}
    else
        echo ${GIVENPATH}
    fi
}

SCRIPT_DIR=`dirname ${BASH_SOURCE[0]}`
SCRIPT_DIR_FULL=`fullpath ${SCRIPT_DIR}`

VIRTUALENV=`which virtualenv`
if [ ! "$?" = "0" ]; then
    echo "ERROR: virtualenv is not found from search path. Exit."
    exit ${STATUS_ERROR_VIRTUALENV_NOT_FOUND}
fi
if [ -z "$1" ]; then
    echo "ERROR: deployment folder path not found."
    echo "USAGE:"
    echo "        $0 <deployment root> [pip-dependency-list]"
    exit ${STATUS_ERROR_DEPLOYMENT_ROOT_UNDEFINED}
fi
DEPLOY_ROOT=$1
if [ -d "${DEPLOY_ROOT}" ]; then
    echo "WARNING: Deployment root already exists."
fi
if [ -z "$2" ]; then
    echo "Dependency file list not specified. Fallback to default one."
    DEPENDENCY_FILE=${SCRIPT_DIR_FULL}/ruuxee-server-env-deps.txt
    if [ ! -f "${DEPENDENCY_FILE}" ]; then
        echo "ERROR: Default dependency not found: ${DEPENDENCY_FILE}"
        exit ${STATUS_ERROR_DEPENDENCY_FILE_NOT_SPECIFIED}
    fi
else
    DEPENDENCY_FILE=$2
fi

UNAME=`uname | grep Linux -i`
if [ ! -z "$UNAME" ]; then
    echo "Linux detected. Install python-dev in advance."
    ISDEBIAN=`which apt-get`
    if [ ! -z "${ISDEBIAN}" ]; then
        # Yes it's Debian or Ubuntu system.
        apt-get install -y python-dev
    else
        echo "ERROR: Non debian system is not supported: ${UNAME}"
        exit ${STATUS_ERROR_SYSTEM_NOT_SUPPORTED}
    fi
else
    UNAME=`uname | grep Darwin -i`
    if [ ! -z "$UNAME" ]; then
        echo "Mac detected. Check if you have compiler installed."
        HASCOMPILER=`which clang`
        if [ -z "${HASCOMPILER}" ]; then
            echo "ERROR: Compiler not installed. Please install Xcode."
            exit ${STATUS_ERROR_COMPILER_NOT_INSTALLED}
        fi
    else
        echo "ERROR: Not supported operating system: ${UNAME}"
        exit ${STATUS_ERROR_SYSTEM_NOT_SUPPORTED}
    fi
fi

PYTHON_MAJOR_VER=`python -c "import sys;print(sys.version_info.major)"`
PYTHON_MINOR_VER=`python -c "import sys;print(sys.version_info.minor)"`
PYTHON_VER=${PYTHON_MAJOR_VER}.${PYTHON_MINOR_VER}
echo "Detect Python version ${PYTHON_VER}."

echo -n "Creating new virtual environment... "
# Now we can really create virtual root, and install all dependencies.
ROOT_FULLPATH=`fullpath ${DEPLOY_ROOT}`
DEPENDENCY_FILE_FULLPATH=`fullpath ${DEPENDENCY_FILE}`
${VIRTUALENV} ${ROOT_FULLPATH} > /dev/null
cd ${ROOT_FULLPATH} > /dev/null
echo "Done."

echo -n "Install dependencies... "
. bin/activate # Now we can install all stuff
pip install --requirement ${DEPENDENCY_FILE_FULLPATH} > /dev/null
if [ "$?" != "${STATUS_OK}" ]; then
    echo "ERROR: Fail to install packages."
    exit $?
fi
echo "Done."

# After installing, we put the 
echo -n "Deploy ruuxee module to environment... "
RUUXEE_MODULE=${SCRIPT_DIR_FULL}/../src/server/ruuxee
cp -r ${RUUXEE_MODULE} ./lib/python${PYTHON_VER}/site-packages
echo "Done."

# TODO: Deploy executable scripts to bin folder.

echo "All complete."
exit $STATUS_OK
