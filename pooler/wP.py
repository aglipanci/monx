from urllib2 import Request, urlopen, URLError, HTTPError
from socket import error as SocketError
import errno

import sys
import pika
import json
import time
import signal

def checkHttpStatus(httpStatObject):
	# duke parur errno.h nga headerat e kernelit variojne nga 35 deri te 133 momentalisht 
	# + errorcodet e http 
	error_list = {
			'EUSERS'          :       'Too many users',
			'ENOTSOCK'        :       'Socket operation on non-socket', 
			'EDESTADDRREQ'    :       'Destination address required',
			'EMSGSIZE'        :       'Message too long',
			'EPROTOTYPE'      :       'Protocol wrong type for socket',
			'ENOPROTOOPT'     :       'Protocol not available',
			'EPROTONOSUPPORT' :       'Protocol not supported',
			'ESOCKTNOSUPPORT' :       'Socket type not supported',
			'EOPNOTSUPP'      :       'Operation not supported on transport endpoint',
			'EPFNOSUPPORT'    :       'Protocol family not supported',
			'EAFNOSUPPORT'    :       'Address family not supported by protocol',
			'EADDRINUSE'      :       'Address already in use',
			'EADDRNOTAVAIL'   :       'Cannot assign requested address',
			'ENETDOWN'        :       'Network is down',
			'ENETUNREACH'     :       'Network is unreachable',
			'ENETRESET'       :       'Network dropped connection because of reset',
			'ECONNABORTED'    :       'Software caused connection abort',
			'ECONNRESET'      :       'Connection reset by peer',
			'ENOBUFS'         :       'No buffer space available',
			'EISCONN'         :       'Transport endpoint is already connected',
			'ENOTCONN'        :       'Transport endpoint is not connected',
			'ESHUTDOWN'       :       'Cannot send after transport endpoint shutdown',
			'ETOOMANYREFS'    :       'Too many references: cannot splice',
			'ETIMEDOUT'       :       'Connection timed out',
			'ECONNREFUSED'    :       'Connection refused',
			'EHOSTDOWN'       :       'Host is down',
			'EHOSTUNREACH'    :       'No route to host',
			'EALREADY'        :       'Operation already in progress',
			'EINPROGRESS'     :       'Operation now in progress',
			'ESTALE'          :       'Stale file handle',
			'EUCLEAN'         :       'Structure needs cleaning', 
			'ENOTNAM'         :       'Not a XENIX named type file', 
			'ENAVAIL'         :       'No XENIX semaphores available',
			'EISNAM'          :       'Is a named type file',
			'EREMOTEIO'       :       'Remote I/O error',
			'EDQUOT'          :       'Quota exceeded',
			'ENOTFOUND'       :       'Unable to resolve host',
			'200': 'Status OK',
			'201': 'Created',
			'202': 'Accepted',
			'203': 'Non-Authoritative Information',
			'204': 'No Content',
			'205': 'Reset Content',
			'206': 'Partial Content',
			'207': 'Multi-Status',
			'208': 'Already Reported',
			'300': 'Multiple Choices',
			'301': 'Moved Permanently',
			'302': 'Found',
			'303': 'See Other',
			'304': 'Not Modified',
			'305': 'Use Proxy',
			'306': '(Unused) Redirect',
			'307': 'Temporary Redirect',
			'308': 'Permanent Redirect',
			'400': 'Bad Request',
			'401': 'Unauthorized',
			'402': 'Payment Required',
			'403': 'Forbidden',
			'404': 'Not Found',
			'405': 'Method Not Allowed',
			'406': 'Not Acceptable',
			'407': 'Proxy Authentication Required',
			'408': 'Request Timeout',
			'409': 'Conflict',
			'410': 'Gone',
			'411': 'Length Required',
			'412': 'Precondition Failed',
			'413': 'Payload Too Large',
			'414': 'URI Too Long',
			'415': 'Unsupported Media Type',
			'416': 'Range Not Satisfiable',
			'417': 'Expectation Failed',
			'420': 'Method Failure (Spring Framework) | Enhance Your Calm (Twitter)',
			'421': 'Misdirected Request',
			'422': 'Unprocessable Entity',
			'423': 'Locked',
			'424': 'Failed Dependency',
			'426': 'Upgrade Required',
			'428': 'Precondition Required',
			'429': 'Too Many Requests',
			'431': 'Request Header Fields Too Large',
			'440': 'IIS Login Timeout',
			'449': 'IIS Retry With',
			'450': 'IIS Blocked by Windows Parental Controls (Microsoft)',
			'451': 'Unavailable for Legal Reasons || IIS Redirect',
			'498': 'Invalid Token (Esri)',
			'499': 'Token Required (Esri)',
			'500': 'Internal Server Error',
			'501': 'Not Implemented',
			'502': 'Bad Gateway',
			'503': 'Service Unavailable',
			'504': 'Gateway Timeout',
			'505': 'HTTP Version Not Supported',
			'506': 'Variant Also Negotiates',
			'507': 'Insufficient Storage',
			'508': 'Loop Detected',
			'509': 'Bandwidth Limit Exceeded (Apache Web Server/cPanel)',
			'510': 'Not Extended',
			'511': 'Network Authentication Required',
			'520': 'CloudFlare Unknown Error',
			'521': 'CloudFlare Web Server Is Down',
			'522': 'CloudFlare Connection Timed Out',
			'523': 'CloudFlare Origin Is Unreachable',
			'524': 'CloudFlare A Timeout Occurred',
			'525': 'CloudFlare SSL Handshake Failed',
			'526': 'CloudFlare Invalid SSL Certificate'
			}

	req = Request(httpStatObject['host'], headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0' })

	try:
			response = urlopen(req)
	except HTTPError as e:
	# error layer 7 
			if str(e.code) in error_list :
				return {'message': error_list[str(e.code)]+ ' ' + str(e.code) , 'status_code' : str(e.code), 'status': 'ERROR'}
			else:
				return {'message': 'HTTP issues, error code: ' + str(e.code) , 'status_code' : str(e.reason), 'status': 'ERROR'}	    
	except URLError as e:
	# errore layer 4 
			return {'message': 'Connectivity issues, error code: ' + str(e.reason) , 'status_code' : str(e.reason), 'status': 'ERROR'}	    
	except SocketError as e:
			return {'message': 'Socket issue, error code: ' + str(e.errno) , 'status_code' : str(e.errno), 'status': 'ERROR'}
	else:
			return {'message': 'Status OK ', 'status_code' : response.code, 'status': 'OK'}




def post_to_api(pdata):
	api_url = 'http://localhost:3000/api/service-data/add'
	data = {
		'message': pdata['message'],
		'status': pdata['status'],
		'service_id': pdata['service_id'],
		'user': pdata['user'],
		'status_code': pdata['status_code'],
		'name': pdata['name']
	}

	req = Request(api_url)
	req.add_header('Content-Type','application/json')
	try:
		urlopen(req,json.dumps({'data' : data}))
	except HTTPError as e:
		print 'HTTP Issue while posting to API ' + str(e)
	except URLError as e:
		print 'L4 Issue while posting to API ' + str(e)
	except SocketError as e:
		print 'Socket Issue while posting to API ' + str(e)


# TODO: port scan, ssl check, smtp, ping and other stuff like that
def processWork(tC):
	if(tC['type'] == "blacklist"):
		data = monxBlacklist(tC)
	if(tC['type'] == "http_status"):
		data = checkHttpStatus(tC)
	# if(tC.type == "icmp_ping"){
	#   monxPing(tC)
	# if(tC.type == "api_route_check"):
	#   // kontrollo 3-4 URL ne grup te nje API sipas nje pathi
	# if(tC.type == "api_response_time"):
	#   //monxPing(tC)
	data['user'] = tC['user']
	data['name'] = tC['name']
	data['service_id'] = tC['_id']
	#print data
	post_to_api(data)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='service_checks', durable=False)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
		print(" [x] Received %r" % body)
		print json.loads(body)    
		processWork(json.loads(body))
		time.sleep(body.count(b'.'))
		print(" [x] Done")
		ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='service_checks')
channel.start_consuming()
