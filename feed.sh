#!/bin/bash
wget --header "Authorization: Token $1" https://api.koodous.com/feed/apks -O "apks.zip"
unzip -o "apks.zip"
for i in $(cat samples); do URL=`echo $i | awk -F";" '{print $2 " -O apks/" $1}'`; wget $URL; done
rm "apks.zip"
