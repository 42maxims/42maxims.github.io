#!/bin/bash

# Download and extreact Hugo
wget https://github.com/gohugoio/hugo/releases/download/v0.47/hugo_0.47_Linux-64bit.tar.gz
tar xzvf hugo_0.47_Linux-64bit.tar.gz hugo
rm hugo_0.47_Linux-64bit.tar.gz

# Initial site setup
# ./hugo new site 42maxims
# cp 42maxims/* . && rmdir 42maxims
# git clone --depth 1 https://github.com/MunifTanjim/minimo themes/minimo
# minmo theme ref: https://minimo.netlify.com/docs/installation/
# cp theme/minimo/exampleSite/config.toml .
