import oauth2 as oauth
import urlparse
import shelve
import os.path
from xml.dom.minidom import parseString
from BeautifulSoup import BeautifulSoup



# TODO Add your own consumer key and secret
consumer_key    =   'm0fxs2y7qnn5'
consumer_secret =   'XgOkKtylhl6k5Wjs'
 
# the URLs we will use
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url =  'https://api.linkedin.com/uas/oauth/accessToken'
authorize_url =     'https://api.linkedin.com/uas/oauth/authorize'
 
 
# make_request is a simple wrapper around the oauth request call
# It is essentially the code below (but is detailed in full later + in the code download)
def make_request(client,url,request_headers={},error_string="Failed Request",method="GET",body=''):
    resp,content = client.request(url, method, headers=request_headers, body=body)
    return (resp, content)

def get_access(client):
    if os.path.exists("access.db"):
        return load_access()


    response, content = make_request(client,request_token_url,{},"Failed to fetch request token","POST")

    # parse out the tokens from the response
    request_token = dict(urlparse.parse_qsl(content))
    print "Go to the following link in your browser:"
    print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
 
    # ask for the verifier pin code
    oauth_verifier = raw_input('What is the PIN? ')
 
    # swap in the new token + verifier pin
    token = oauth.Token(request_token['oauth_token'],request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)
 
    # fetch the access token
    response, content = make_request(client,access_token_url,{},"Failed to fetch access token","POST")

    # parse out the access token
    access_token = dict(urlparse.parse_qsl(content))
    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print

    database = shelve.open("access.db")
    database['access'] = access_token
    database.close()

    return access_token 

def load_access():
    #print "load_access subroutine"
    database = shelve.open("access.db")
    access_token = database['access']
    
    return access_token

def main():
    # Create our OAuth consumer instance
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    access_token = get_access(client)
    # swap in the new auth token to the client
    token = oauth.Token(access_token['oauth_token'],access_token['oauth_token_secret'])
    client = oauth.Client(consumer, token)

 
    # Simple profile call
    print "\n********A basic user profile call********"
    #response, content = make_request(client,"http://api.linkedin.com/v1/people/~/connections")
    person_url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,industry)"
    response, content = make_request(client,person_url,{},"Failed", "GET")

    person_content = BeautifulSoup(content)    

    industry = person_content.findAll('industry')[-1].contents[-1]
    print industry

    first = person_content.findAll('first-name')[-1].contents[-1]
    print first


if __name__ == '__main__':
    main()
    print 'Done.'



