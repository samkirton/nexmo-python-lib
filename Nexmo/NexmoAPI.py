import os
import urllib2
import json
from StringIO import StringIO

class NexmoREST(object):
	'''
	@author	memtrip
	'''
	def __init__(self, apiKey=os.environ.get('NEXMO_API_KEY'), apiSecret=os.environ.get('NEXMO_API_SECRET')):
		'''
		Define base level constants which are common for all resources
		'''
		self.BASE_URI = "https://rest.nexmo.com/"
		self.TRANSPORT_TYPE = "json"
		self.API_KEY = apiKey
		self.API_SECRET = apiSecret
	
	def populateApiKeyAndSecret(self, jsonRequest):
		'''
		Populate the provided dictionary with the api key and secret
		'''
		jsonRequest['api_key'] = self.API_KEY
		jsonRequest['api_secret'] = self.API_SECRET
		return jsonRequest

	def populateOptionalParameters(self, jsonRequest, **kwargs):
		'''
		Populate the provided dictionary with the optional values defined in **kwargs
		'''
		for key, value in kwargs.iteritems():
			jsonRequest[key] = value
			
		return jsonRequest
	
	def httpRequest(self, jsonRequest, resource):
		'''
		POST the JSON request to the web service end point
		'''
		request = urllib2.Request(self._constructUri(resource), jsonRequest, {'Content-Type': 'application/json'})
		stream = urllib2.urlopen(request)
		response = stream.read()
		stream.close()
		
		return NexmoResponse(StringIO(response))
			
	def _constructUri(self, resource):
		'''
		Create the REST end point URI based on BASE_URI, the provided resource
		and the desired transport type
		'''
		return self.BASE_URI + resource + self.TRANSPORT_TYPE
		
class NexmoSMS(object):
	'''
	/sms/ resource
	@author	memtrip
	'''
	def __init__(self, nexmoREST):
		self.nexmoREST = nexmoREST
		self.REST_RESOURCE = "sms/"
		
	def sendPlainTextSMS(self, sentFrom, to, body, **kwargs):
		'''
		Send a plain text SMS
		@param	sentFrom	Sender address may alphanumeric (Ex: from=MyCompany20).
							Restrictions may apply depending on the destination. See our (nexmo) FAQs.
		@param	to			Mobile number in international format, and one recipient per request. 
							Ex: to=447525856424 or to=00447525856424 when sending to UK.
		@param	body		Body of the text message (with a maximum length of 3200 characters), 
							UTF-8 and URL encoded value.				
		@param	**kwargs	Extra optional parameters: vcard, vcal, ttl, message-class
		'''
		jsonRequest = {"from":sentFrom,"to":to,"text":body}
		return self._sendSMS(jsonRequest, **kwargs)
		
	def sendBinarySMS(self, sentFrom, to, udh, body, **kwargs):
		'''
		Send a binary SMS
		@param	sentFrom	Sender address may alphanumeric (Ex: from=MyCompany20).
							Restrictions may apply depending on the destination. See our (nexmo) FAQs.
		@param	to			Mobile number in international format, and one recipient per request. 
							Ex: to=447525856424 or to=00447525856424 when sending to UK.
		@param	udh			Hex encoded udh. Ex: udh=06050415811581
		@param	body		Hex encoded binary data. Ex: body=0011223344556677
		@param	**kwargs	Extra optional parameters: vcard, vcal, ttl, message-class
		'''
		jsonRequest = {"from":sentFrom,"to":to,"udh":udh,"body":body}
		return self._sendSMS(jsonRequest, **kwargs)
		
	def _sendSMS(self,jsonRequest,**kwargs):
		'''
		Send an SMS
		'''
		jsonRequest = self.nexmoREST.populateApiKeyAndSecret(jsonRequest)
		jsonRequest = self.nexmoREST.populateOptionalParameters(jsonRequest,**kwargs)
		jsonRequest = json.dumps(jsonRequest)
		return self.nexmoREST.httpRequest(jsonRequest, self.REST_RESOURCE)
		
	
class NexmoResponse:
	'''
	Response from the Nexmo REST API
	---
	message_count 		The number of parts the message was split into.
	messages 			An array containing objects for each message part.
	status 				The return code.
	message_id 			The ID of the message that was submitted (8 to 16 characters).
	to 					The recipient number.
	client_ref 			If you set a custom reference during your request, this will return that value.
	remaining_balance 	The remaining account balance.
	message_price 		The price charged for the submitted message.
	network 			Identifier of a mobile network MCCMNC. Wikipedia list here.
	error_text 			If an error occurred, this will explain in readable terms the error encountered.
	@author	memtrip
	'''	
	def __init__(self, response):	
		# raw and data type (formatted) response	 		
		self.rawResponse = response
		self.formattedResponse = json.load(response)
		
		# response field values 		
		self.message_count = None
		self.messages = None
		self.status = None
		self.message_id = None
		self.to = None
		self.client_ref = None
		self.remaining_balance = None
		self.message_price = None
		self.network = None
		self.error_text = None
		
		# response field constants
		MESSAGE_COUNT = "message-count"
		MESSAGES = "messages"
		STATUS = "status"
		MESSAGE_ID = "message-id"
		TO = "to"
		CLIENT_REF = "client-ref"
		REMAINING_BALANCE ="remaining-balance"
		MESSAGE_PRICE = "message-price"
		NETWORK = "network"
		ERROR_TEXT = "error-text"
	
		print self.rawResponse.getvalue()
	
		for key, value in self.formattedResponse.iteritems():
			if key == MESSAGE_COUNT:
				self.message_count = value
			elif key == MESSAGES:
				self.messages = []				
				if (value and len(value) > 0):
					for message in value:
						self.messages.append(message)
					
			elif key == STATUS:
				self.status = value
			elif key == MESSAGE_ID:
				self.message_id = value
			elif key == TO:
				self.to = value
			elif key == CLIENT_REF:
				self.client_ref = value
			elif key == REMAINING_BALANCE:
				self.remaining_balance = value
			elif key == MESSAGE_PRICE:
				self.message_price= value
			elif key == NETWORK:
				self.network = value
			elif key == ERROR_TEXT:
				self.error_text = value
		
	def __getitem__(self, index):
		'''
		Allow the variables in this class to be accessed by index, e.g.
		print nexmoResponse['status']
		'''
		return self.__dict__[index]
		
	def getRawResponse(self):
		'''
		@return	The raw JSON response 
		'''
		return self.rawResponse.getvalue()
	
	def getFormattedResponse(self):
		'''
		@return	The JSON response parsed as a python data set
		'''
		return self.formattedResponse
	
	def isValid(self):
		'''
		@return	Has the api returned an error?
		'''
		isValid = True
		if (self.messages and len(self.messages) > 0):
			for message in self.messages:
				if "error-text" in message:
					isValid = False
					break
			
		return isValid