#!/bin/sh

d=`dirname $0`

if [ -z "$RAIL_HOME" ] ; then
	echo "Set RAIL_HOME first"
	exit 1
fi

PROJ=cuffdiff2_small

s3cmd del --recursive s3://langmead/tornado_${PROJ}/manifest
s3cmd del --recursive s3://langmead/tornado_${PROJ}/output

s3cmd put ${d}/cuffdiff2_small.manifest s3://langmead/tornado_${PROJ}/manifest/

python $RAIL_HOME/src/driver/tornado.py \
	--emr \
	--manifest s3://langmead/tornado_${PROJ}/manifest/cuffdiff2_small.manifest \
	--output s3://langmead/tornado_${PROJ}/output \
	--reference s3://tornado-emr/refs/hg19_UCSC.tar.gz \
	--instance-type c1.xlarge \
	--instance-counts 1,1,8 \
	--bid-price 0.071 \
	--no-differential \
	$*

echo "s3cmd del --recursive s3://langmead/tornado_${PROJ}"