#!/bin/bash

set -e

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
   build-essential git gettext \
   python-virtualenv curl yui-compressor python-dev \
   libpq-dev libxml2-dev libxslt-dev libffi-dev \
   libjpeg-dev screen \
   libyaml-dev >/dev/null


grep -qG 'cd $HOME' "$HOME/.bashrc" ||
   cat <<'EOF' >> "$HOME/.bashrc"

source ~/venv/bin/activate
cd ~/
EOF
source "$HOME/.bashrc"

cd ~/
yournextrepresentative/bin/pre-deploy
