import hashlib#for computing hash
from rauth.service import OAuth1Service #see https://github.com/litl/rauth for more info
import shelve #for persistent caching of tokens, hashes,etc.

#get your consumer key and secret after registering as a developer here: https://oauth.withings.com/en/partner/add

#FIXME add method to set default units and make it an optional argument to the constructor
class Withings:
    def __init__(self,email_address,consumer_key,consumer_secret,cache_name='tokens.dat'):
        if email_address == None:
            raise Exception("You must specify the email address associated with your Withings account")
        #cache stores tokens and hashes on disk so we avoid
        #requesting them every time.
        self.cache=shelve.open(cache_name,writeback=False)
        self.email_address = email_address
        self.password_hash = self.cache.get('withings_password_hash')
        if self.password_hash is None: 
            password = raw_input('Enter your Withings account password: ')
            self.password_hash = hashlib.md5(password).hexdigest() 
            self.cache['withings_password_hash'] = self.password_hash
        
        #FIXME figure out a way to determine if tokens have expired
        self.oauth=OAuth1Service(
                name='withings',
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                request_token_url='https://oauth.withings.com/account/request_token',
                access_token_url='https://oauth.withings.com/account/access_token',
                authorize_url='https://oauth.withings.com/account/authorize',
                header_auth=True)

        self.access_token = self.cache.get('withings_access_token',None)
        self.access_token_secret = self.cache.get('withings_access_token_secret',None)
        self.request_token =  self.cache.get('withings_request_token',None)
        self.request_token_secret =  self.cache.get('withings_request_token_secret',None)
        self.pin= self.cache.get('withings_pin',None)
        
        #If this is our first time running- get new tokens 
        if (self.need_request_token()):
            self.get_request_token()

        #If tokens have expired, get new ones
        #for some reason, periodically withings just decides not to return an access token but you
        #can keep accessing the data regardless?! Not sure how to know if lack of response
        #here is actually a problem or how to know if token has expired
        #if( not self.get_access_token()):
        if( self.request_token is None):
            self.get_request_token()
            got_access_token=self.get_access_token()
            if( not got_access_token):
                print "Error: Unable to get access token"
        #Maybe you always need to recompute the hash/get a new once to avoid expiration?
        #self.reqhash = self.cache.get('withings_reqhash',None)
        #self.public_key = self.cache.get('withings_public_key',None)
        self.reqhash=None
        self.public_key = None
        if self.public_key is None:
            #this will set public_key,user_id, and is_public
            self.get_public_key_and_user_id()

        self.user_id =  self.cache.get('withings_user_id',None)
        #the call to get_public_key_and_user_id above should set is_public:w
        #7= everything public, if we don't have that, then make it public
        self.is_public = self.cache.get('withings_is_public',None)
        #if self.is_public != 7:
        #    self.make_data_public()

        #Maybe you need to split up getting the PIN and getting the request token
        #not clear if you maybe need to retrieve the request token everytime?


    def get_request_token(self):
        self.request_token,self.request_token_secret = self.oauth.get_request_token(http_method='GET')
        authorize_url=self.oauth.get_authorize_url(self.request_token)
        #the pin you want here is the string that appears after oauth_verifier on the page served
        #by the authorize_url
        print 'Visit this URL in your browser then login: ' + authorize_url
        self.pin = raw_input('Enter PIN from browser: ')
        self.cache['withings_request_token']=self.request_token
        self.cache['withings_request_token_secret']=self.request_token_secret
        self.cache['withings_pin']=self.pin
        print "withings_pin is ",self.cache.get('withings_pin')

    def need_request_token(self):
        #created this method because i'm not clear when request tokens need to be obtained, or how often
        if (self.request_token==None) or (self.request_token_secret==None) or (self.pin==None):
            return True
        else:
            return False

    def get_access_token(self):
        print "in get_access_token"
        response=self.oauth.get_access_token(self.request_token,
            self.request_token_secret,
            http_method='GET',
            oauth_verifier=self.pin)
        data=response.content
        print response.content
        self.access_token=data.get('oauth_token')
        self.access_token_secret=data.get('oauth_token_secret')
        self.cache['withings_access_token']=self.access_token
        self.cache['withings_access_token_secret']=self.access_token_secret
        if not(self.access_token) or not(self.access_token_secret):
            print "access token expired "
            return False
        else:
            return True

    def get_public_key_and_user_id(self):
        if self.reqhash==None:
            self.compute_hash()
        print "using hash ",self.reqhash
        params={'action': 'getuserslist','email':self.email_address,'hash':self.reqhash} #how to determine public key and userid
        response=self.oauth.request(
                'GET',
                'http://wbsapi.withings.net/account',
                self.access_token,
                self.access_token_secret,
                header_auth=True,
                params=params)
        data=response.content
        print data
        body=data['body']
        #FIXME- allow handling multiple users
        self.public_key=body['users'][0]['publickey']
        self.user_id=body['users'][0]['id']
        self.cache['withings_user_id']=self.user_id
        self.cache['withings_public_key']=self.public_key
        self.is_public = int(body['users'][0]['ispublic'])
        self.cache['withings_is_public'] = self.is_public
        print "get_public_key response is ",response
        print "get_public_key data is ",data
        print "get_public_key body is ",body
        #FIXME refactor this to return values which you then store where needed
        #return public_key,user_id,is_public
        
    #certain requests require sending a signature hash
    def compute_hash(self):
        params={'action': 'get'} #this fetches the once needed to compute the hash
        response=self.oauth.request(
            'GET',
            'http://wbsapi.withings.net/once',
            self.access_token,
            self.access_token_secret,
            header_auth=True,
            params=params)
        #response.content is a dictionary with status and body as keys
        data=response.content
        body=data['body']
        once=body['once']
        print "once is ",once
        reqhash = ":".join([self.email_address,self.password_hash,once])
        self.reqhash=hashlib.md5(reqhash).hexdigest()
        #save the hash for subsequent uses. this should only need to be done once,
        #unless you change your password?
        self.cache['withings_reqhash']=self.reqhash

    #only need to do this once
    def make_data_public(self):
        return
        params={'action': 'update','userid': self.user_id,'publickey': self.public_key,'ispublic': '7'} #set all data to be public
        response=self.oauth.request(
                'GET',
                'http://wbsapi.withings.net/user',
                self.access_token,
                self.access_token_secret,
                header_auth=True,
                params=params)

    def get_weights(self):
        if (self.public_key==None):
            self.get_public_key_and_user_id()
        print "user_id in get_weights ",self.user_id
        params={'action': 'getmeas','userid': self.user_id,'publickey': self.public_key,'startdate': '0'} #how to determine first and last name
        response=self.oauth.request(
                'GET',
                'http://wbsapi.withings.net/measure',
                self.access_token,
                self.access_token_secret,
                header_auth=True,
                params=params)
        data=response.content
        body=data['body']
        measuregroups=body['measuregrps']
        print len(measuregroups)
        weight_data=[]
        dates=[]
        for mgrp in measuregroups:
            measures=mgrp['measures']
            #print len(measures)
            for measure in measures:
                if measure['type']==1:
                   #use encoded exponent for unit and convert to pounds
                   one_weight=(measure['value']*(10**measure['unit']))*2.20462262
                   weight_data.append(one_weight)
                   dates.append(mgrp['date'])
        return (dates,weight_data)

