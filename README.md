# cisco-dev
#This is a Python3 based web service development project.
#The intent of the web service is to render the safe/validity
#of the URL which has been requested
#
#Usage
#To start the web-service follow these steps:
# cd <relative>/cisco-dev/safeurl
# pip3 install -r requirements.txt
# python3 urlcheck.py (You may choose to run in foreground or background)
# 
#With the above service being running, now you can make send GET requests
#for the URL of your interest.
#For example:
#GET "http://127.0.0.1:5000/https://www.cisco.com/c/en/us/products"
#where > "http://127.0.0.1:5000/" is the web-service endpoint
#"https://www.cisco.com/c/en/us/products" is the requested URL to be validated
#
