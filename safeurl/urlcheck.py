"""This module validates URL"""
from socket import gethostbyname, gaierror
import sys
import urllib
import requests
from flask import Flask, jsonify

app = Flask(__name__)
#One of the intent to initialize the instance of the Flask app
#ahead of python custom classes, just so that we logging module of
#flask could be leveraged

class Error(Exception):
    """Base class for custom exceptions"""
class UrlParseError(Error):
    """Raised on encountering invalidity during URL parsing"""
class UnresolvedUrl(Error):
    """Raised when DNS resolution of the domain fails"""

class ValidateUrl:
    """Primary class for safe URL validation"""
    def __init__(self):
        self.timeout = 30
        self.valid_schemes = ['http', 'https', 'ftp', 'news', 'telnet'] #commonly used URL schemes
        self.dns_success = {} #keeps track of ONLY successfully resolved domains
        self.url_statuses = {} #Book-keeper of the URL status, renders the status of the URL

    def parse_to_validate(self, url):
        """Parses the URL to extract scheme, domain, path
        and checks their validity wrt their formations
        Returns the parsed URL
        """
        url = url.strip()
        if not url:
            raise UrlParseError("URL is not specified")
        if len(url) > 2048:
            raise UrlParseError("URL exceeds it recommended max length of 2048 chars")
        parse_result = urllib.parse.urlparse(url)
        if not parse_result.scheme:
            raise UrlParseError("URL scheme is not specified")
        if parse_result.scheme not in self.valid_schemes:
            raise UrlParseError(f"{parse_result.scheme} > Not a common URL scheme")
        if not parse_result.hostname:
            raise UrlParseError("URL domain is not specified")
        if len(parse_result.hostname) > 255:
            raise UrlParseError("Domain name exceeds 255 chars as per RFC 3986")
        return parse_result.geturl(), parse_result.hostname, parse_result.path

    def dnslookup(self, domain):
        """DNS resolution of domain/hostname in the URL
        Returns boolean
        """
        try:
            app.logger.info("The domain == %s", domain)
            gethostbyname(domain)
            self.dns_success[domain] = True
        except gaierror as _err:
            app.logger.error(f"DNS Resolution of URL Failed due to {_err}")
            return False
        return True

    def fetch_status_url(self, url):
        """Primary function to be exposed to flask app"""
        try:
            #1st step: below needed variable assignment ensures url parsing validation
            url, domain, path = self.parse_to_validate(url)
            #2nd step: validates dns resolution and updates the dns-map
            app.logger.info("Current state of DNS cache = %s", self.dns_success)
            if domain not in self.dns_success:
                self.url_statuses[domain] = {}
                dns_result = self.dnslookup(domain)
                self.url_statuses[domain]['status'] = dns_result
                if not dns_result: #Before raising Exception ensure to set domain's status to False as above
                    raise UnresolvedUrl(f"{domain} is network unreachable")
            #3rd step: only on success of above two steps, makes it relevant now to make
            #http-request for the url. Could have used method <get>(/w stream=True) inorder to
            #avoid downloading the content. Instead used method <head>
            req = requests.head(url, timeout=self.timeout)
            app.logger.info("Status code = %s", req.status_code)
            if req.status_code == 301: #Incase of domain or path permanently redirected
                self.url_statuses[domain][path] = True
                return True
            elif req.status_code == 200: #Incase of both domain and path exists
                self.url_statuses[domain][path] = True
                return True
            else:
                self.url_statuses[domain][path] = False #Incase of domain exists but unsure of path
                return False
        except UrlParseError as _err:
            app.logger.error(_err)
            return False
        except UnresolvedUrl as _err:
            app.logger.error(_err)
            return False
        except (requests.ConnectionError, requests.ConnectTimeout):
            self.url_statuses[domain] = False
            return False

validator = ValidateUrl()
@app.route('/<path:url>', methods=["GET"])
def get_url_status(url):
    """Handles incoming GET request for URL check"""
    app.logger.info('The URL to be tested == %s', url)
    app.logger.debug("Current state of hashmap = %s", validator.url_statuses)
    if validator.fetch_status_url(url):
        return jsonify('Safe', 200)
    return ('Invalid', 500)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
