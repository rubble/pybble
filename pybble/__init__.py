__all__ = ["rubble"]

# imports
import requests, json, datetime
from urllib.parse import urlparse, urljoin

class RubbleREST:
	"""
	The Rubble web services use HTTP Basic authentication for
	everything except for the URL paths /rubble/service/cluster-probe
	and /rubble/webdav/www/, which may be accessed without
	authentication. The cluster-probe service is intended for calls
	from the Azure load balancer to determine server
	responsiveness. The www WebDAV folder is intented for central
	management of various web resources that can be cached by the
	reverse proxy frontend. [This folder is not yet implemented, the
	files are currently duplicated on each frontend instance.]

	The authentication credentials consist of an API key and a
	secret. They function as the username and password in the HTTP
	Basic protocol. Application developers sign up in a separate web
	app where they can generate their own API keys and secrets. There
	are also master credentials used for bootstrapping and for
	intra-cluster communication.  A class to talk to the rubble
	service.
	"""
	def __init__(self, auth, config={}):

		# User must supply API key to talk to rubble
		self.auth = auth
				
		self.config = {
			"base_url": "https://rubble2.labs.viditeck.com/",
			"pid": 1408,
			"verify_SSL": True,
			"headers": {
				"user-agent": "pybble",
				"content-type": "application/json",
			}
		}

		# merge configs passed in onto the defaults
		self.config.update(config)

		# api url
		self.config['api_url'] = urljoin(self.config['base_url'], "rubble/service/")
		
		return None
	   

	def now():
		"""
		Get now as a microseconds since the UNIX epoch.
		"""
		return int(datetime.datetime.now().strftime("%s")) * 1000 
		

	def call(self, terms, format=text, **kwargs):
		"""
		Arguements
		----------
		
		terms

			Rubble facts or more generally Herbrand terms, that Rubble
			should evaluate. These can either be set as a nested list
			otherwise known as JSON-encoded Rubble facts:

				[["completed","task23"],
				 ["device_category","1","Mobile device"],
				 ["leap_year"],
				 "daylight_saving",
				 ["f",["g","h"],["i","j","k"]]

			Or as plain Rubble rules:

				completed(task23);
				device_category(1,"Mobile device");
				leap_year;
				daylight_saving;
				f(g(h),i(j,k));

			See http://clip.dia.fi.upm.es/~vocal/public_info/seminar_notes/node32.html

		Synchronously sends a message consisting of Herbrand terms to
		the designated channel. The response is a JSON Object
		{"output":[…]} on success, or {"error":"MESSAGE"} if an error
		occurred.

		If the rules triggered by this message results in new outgoing
		messages to the pseudo-channel default, the terms in these
		messages are delivered to the client in the response property
		output, encoded as a JSON array.

		The message is not enqueued, but rather bypasses any pending
		enqueued messages and is delivered in the same transaction as
		the request.

		The content-type of the request body can be either
		application/json or text/plain. In the latter case the terms
		are encoded in Rubble source-code syntax instead of JSON. For
		a description of the JSON Rubble format, see Appendix A,
		JSON-encoded Rubble facts.

		"""

		# create the payload and update with kwargs
		payload = {
			'channel': 'pid(%s)' % self.config['pid']
		}

		payload = payload.update(kwargs)
        
		if 'pid' in kwargs: 
			payload['channel'] = 'pid(%d)' % kwargs['channel']
			
		# join the api url to the method call
		url = urljoin(self.config['api_url'], 'call')

		# todo: verify is currently false because rubble 2 doens't have a valid cert
		return requests.post(url, json=terms, headers=headers, params=payload, auth=self.auth, verify=self.config.verify_SSL) 

	def send(self, terms, **kwargs):
		"""
		Sends a message consisting of JSON-encoded Herbrand terms to the
		designated channel. The content-type of the request body must be
		application/json. For a description of the JSON Rubble format, see
		Appendix A, JSON-encoded Rubble facts.

        The response is an empty JSON object {} on success, or
		{"error":"MESSAGE"} if an error occurred. Note: success only
		means that the message was successfully enqueued. Due to the
		asynchronous nature of message sending, some errors may occur
		after the API response has been committed.
		"""

		# create the payload and only add params if they are included
		payload = {
			'channel': 'pid(%s)' % self.config['pid']
		}

		if 'when' in kwargs: 
			payload['when'] = kwargs['when']
        
		if 'pid' in kwargs: 
			payload['channel'] = 'pid(%d)' % kwargs['channel']
			
		if 'wrap_input_from' in kwargs:
			payload['wrap-input-from'] = kwargs['wrap_input_from']

		# join the api url to the method call
		url = urljoin(self.config['api_url'], 'call')

		# todo: verify is currently false because rubble 2 doens't have a valid cert
		return requests.post(url, json=terms, params=payload, auth=self.auth, verify=self.config.verify_SSL)


	def domaininfo(self):
		"""Returns a JSON object that contains some information about the
		client's credentials. 

		This is easiest described via an example. Suppose an
		application authenticates with the API key Fv32O6HN9Abz and
		the secret password WvAQtZjIOAVnPluc, and this API key belongs
		to an account named acme. Then the response from this call
		will be {"domain":"acme","apikey":"Fv32O6HN9Abz"}.

		"""
		url = urljoin(self.config['api_url'], 'domaininfo')
		
		return requests.get(url, auth=self.auth)

	def process_create(self, rulesref, **kwargs): 
		"""
		Creates a new Rubble process. The request body must have
		content-type application/json and consist of a JSON object.

		Keyword arguements
		-----------------------
		
		rulesref 

		    A string that specifies the rule file that contains
			the Rubble code which controls this process. This string should
			have either the format file:/PATH or the format
			file://DOMAIN/PATH. For compatibility with RFC 3986 the variant
			for var in collection:
			mat file:///PATH is accepted as equivalent to the single-slash
			format.

		factsformat (optional)
		
		    Specifies the storage format of the Rubble process state for
			this process. If provided, this property is either one of the
			strings native, xml, json, or the number 1 or 2. The
			alternatives xml or 2 cause the facts to be stored internally
			in XML format and require the facts property to be supplied as
			a string containing the initial XML code. The alternatives
			native or 1 cause the facts to be stored internally in Rubble
			native format and require the facts property to be supplied as
			a string containing the initial Rubble code. The alternative
			json causes the facts to be stored internally in Rubble native
			format and requires the facts property to be supplied as a
			JSON array (see Appendix A, JSON-encoded Rubble facts). The
			default value for factsformat is json.

		facts (optional)
		
	        The initial process state, in the syntax specified by
			factsformat. The default syntax is a JSON array (see Appendix
			A, JSON-encoded Rubble facts). The default value is an empty
			set of facts. An empty string is always legal here, in the XML
			case it will be automatically converted into the empty root
			element <rubble/>.

		trapstate (optional)
		
			An optional string containing an XML document that represents
			any exceptional processing state. If this string is omitted or
			left blank, normal processing will be assumed. See
			documentation of process for details. This property is
			typically omitted at process creation.

		The response is a JSON object.
		
		Response body properties
		------------------------

		pid
		
	        The process ID of the newly created process. Note: this is a
			JSON string (of digits), not a JSON number.

		"""
		payload = {
			'rulesref': rulesref,
		}

		# add kwargs as params to the payload
		payload = payload.update(**kwargs)

        # join the api url to the method call
		url = urljoin(self.config['api_url'], 'processcreate')

        return requests.post(url, params=payload, auth=self.auth, verify=self.config.verify_SSL)


		def process_update(self, rulesref, pid, **kwargs):
			"""
			Updates a Rubble process. The request body must have content-type
			application/json and consist of a JSON object.

			Arguments
			---------

			pid
			
				The process ID of the process to update. Note: this must
				be a JSON string (of digits), not a JSON number.

			rulesref
			
			    See docstring for processcreate.

			Keyword arguements
			------------------
			
			factsformat (optional)
			
			    See documentation for processcreate.

			facts (optional)

			    See documentation for processcreate.

			trapstate (optional)
			    
                See documentation for processcreate.

			Note: the optional properties are defaulted in the same
			way as for processcreate, i.e. they are not defaulted to
			their stored values.

			The response is an empty JSON object {} on success, or
			{"error":"Unauthorized access"} if the caller didn't have
			permission.

			"""
			
			payload = {
				"pid": str(pid),
				"rulesref": rulesref,
			}

			# add kwargs as params to the payload
			payload = payload.update(**kwargs)

			# join the api url to the method call
			url = urljoin(self.config['api_url'], 'processupdate')

			return requests.post(url, params=payload, auth=self.auth, verify=self.config.verify_SSL)

			
			
