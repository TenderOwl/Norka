#!/bin/bash

APP_NAME="norka"
APP_DOMAIN="com.github.tenderowl.norka"

if [ -z $1 ]; then
    echo "Usage: $0 lang"
    exit
fi
lang="$1"

rm *.pot

version=$(fgrep "version: " ../meson.build | head -1 | grep -o "'.*'" | sed "s/'//g")

find ../$APP_NAME -iname "*.py" | xargs pygettext -d $APP_DOMAIN -o $APP_NAME-python.pot
find ../data/ui -iname "*.ui" -or -iname "*.glade" | xargs pygettext -d $APP_DOMAIN -o $APP_NAME-glade.pot
find ../data/ -iname "*.desktop.in" | xargs pygettext -d $APP_DOMAIN -o $APP_NAME-desktop.pot
find ../data/ -iname "*.appdata.xml.in" | xargs pygettext -d $APP_DOMAIN -o $APP_NAME-appdata.pot

msgcat --use-first $APP_NAME-python.pot $APP_NAME-glade.pot $APP_NAME-desktop.pot $APP_NAME-appdata.pot > $APP_DOMAIN.pot

sed 's/#: //g;s/:[0-9]*//g;s/\.\.\///g' <(fgrep "#: " $APP_DOMAIN.pot) | sort | uniq | grep -v " " > POTFILES.in

[ -f "${lang}.po" ] && mv "${lang}.po" "${lang}.po.old"
msginit --locale=$lang --input $APP_DOMAIN.pot
if [ -f "${lang}.po.old" ]; then
    mv "${lang}.po" "${lang}.po.new"
    msgmerge -N "${lang}.po.old" "${lang}.po.new" > ${lang}.po
    rm "${lang}.po.old" "${lang}.po.new"
fi
sed -i 's/ASCII/UTF-8/' "${lang}.po"
rm *.pot
