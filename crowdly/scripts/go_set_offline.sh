#!/usr/bin/env bash
pushd /var/www/iot/
#pushd /home/molteanu/work/cloudmatix-demo/
source env/bin/activate
exec python src/framework/manage.py runscript set_offline