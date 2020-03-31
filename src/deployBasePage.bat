rem Most useful during page development. Deploy entire static site out to S3 AND fresh data.
call deployNewData.bat
aws s3 cp staticPageOut/ s3://www.williamkarnavas.com/opentabs/ --recursive