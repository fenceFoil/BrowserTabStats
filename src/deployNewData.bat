rem Called by runBrowserTabArchiver.bat to deploy the generated static site data to S3.
python updateStaticPageData.py
aws s3 cp staticPageOut/open-tabs-data.js s3://www.williamkarnavas.com/opentabs/open-tabs-data.js