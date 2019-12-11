"""Unittests for urlcheck app"""

from urlcheck import ValidateUrl, UrlParseError, UnresolvedUrl
import unittest

to_test = ValidateUrl()
class TestParseToValidate(unittest.TestCase):
    """This test class tests the parse_to_validate method"""
    def test_qualified_url(self):
        """Verifies the method returns True val for qualified url"""
        #qualified url: the url which has all valid scheme, domain and path
        url = "https://www.cisco.com/c/en/us/products"
        result = to_test.parse_to_validate(url)
        #print(result)
        self.assertTrue(result[0])
        self.assertTrue(result[1])
        self.assertTrue(result[2])
    def test_exceptions(self):
        """Verifies the function raises exceptions"""
        #Expect exception on an empty string url
        with self.assertRaises(UrlParseError): to_test.parse_to_validate("")
        #Expect exception when url length exceeds
        myurl = "https://" + "test" * 2036 + ".com"
        with self.assertRaises(UrlParseError): to_test.parse_to_validate(myurl)
        #Expect exception when url scheme is invalid
        myurl = "htt://google.com"
        with self.assertRaises(UrlParseError): to_test.parse_to_validate(myurl)
        #Expect exception when url domain is not specified
        myurl = "http://"
        with self.assertRaises(UrlParseError): to_test.parse_to_validate(myurl)

class TestDnslookup(unittest.TestCase):
    """This test class tests the dnslookup method"""
    def test_valid_domain(self):
        """Verifies the method returns True for valid domain"""
        domain = "www.cisco.com"
        self.assertTrue(to_test.dnslookup(domain))
    def test_invalid_domain(self):
        """Verifies the method returns False for invalid domain"""
        domain = "woksfornoneallnonsense.com"
        self.assertFalse(to_test.dnslookup(domain))

class TestFetchStatusUrl(unittest.TestCase):
    """This test class tests the fetch_status_url method"""
    def test_valid_url(self):
        result = to_test.fetch_status_url("https://google.com/flights")
        self.assertTrue(result)
    def test_unknown_url(self):
        result = to_test.fetch_status_url("https://woksfornoneallnonsense.com")
        self.assertFalse(result)

if __name__=='__main__':
    unittest.main() 
