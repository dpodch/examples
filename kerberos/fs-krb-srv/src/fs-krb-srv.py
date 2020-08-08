from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer # python2
#from http.server import BaseHTTPRequestHandler, HTTPServer # python3
import threading
import ssl
import re
import string
import kerberos
import sys, os


def ERROR(str):
    print("ERROR " + str)
    
def utf8len(s):
    return len(s.encode('utf-8'))
    
class KerberosAPI(object):
    SERVICE_TYPE_DEFAULT = 'HTTP'

    def __init__(
            self,
            hostname,
            service_type = SERVICE_TYPE_DEFAULT
    ):
        self._hostname = hostname
        self._service_type = service_type

    def _split_principal(cls, principal):
        try:
            splits = principal.split('/')
            service_type = splits[0]
            splits = splits[1].split('@')
            service = splits[0].upper()
            realm = splits[1]
        except IndexError:
            ERROR("Invalid Kerberos principal:" + principal)
            raise ValueError('Authentication System Failure: Invalid Kerberos principal: %s' % principal)
        return '%s@%s' % (service_type, service,), realm

    def check_ticket(self, ticket):

        init_context_res = chech_ticket_res = -1
        principal = realm = orig_service = target_name = service = ''
        
        try:
            principal = kerberos.getServerPrincipalDetails(self._service_type, self._hostname)
            orig_service, realm = self._split_principal(principal)
            init_context_res, context = kerberos.authGSSServerInit('')
            chech_ticket_res = kerberos.authGSSServerStep(context, ticket)
            target_name = kerberos.authGSSServerTargetName(context)
            service, _ = self._split_principal(target_name)
            response = kerberos.authGSSServerResponse(context)
            principal = kerberos.authGSSServerUserName(context)
            kerberos.authGSSServerClean(context)
                
        except kerberos.GSSError:
            if init_context_res != 1:
                ERROR("Error init kerberos context")
            elif chech_ticket_res == -1:
                ERROR("Ticket is not correct:" + ticket)
            elif service.lower() != orig_service.lower():
                ERROR('Bad credentials: wrong target name ' + target_name)
            return '', '', ''
        
        except kerberos.KrbError:
            ERROR ("Internal kerberos error")
            return '', '', ''
        
        # del kerberos
        username, realm = principal.split('@')
        return response, username, realm
    
    def get_ticket(self, hostname, service_type):
        status, context = kerberos.authGSSClientInit('%s@%s' % (service_type, hostname,))

        if not status:
            ERROR('Kerberos: Could not initialize context')
            return ''

        status = kerberos.authGSSClientStep(context, '')
        if status:
            ERROR('Kerberos: Client step failed')
            return ''

        ticket = kerberos.authGSSClientResponse(context)
        kerberos.authGSSClientClean(context)
        
        return ticket;


def parseNegotiateHeader(header):
    key = re.subn("negotiate", '', header, 0, flags=re.IGNORECASE)[0]
    key = re.subn(" ", '', key, 0, flags=re.IGNORECASE)[0]
    return key

class Handler(BaseHTTPRequestHandler):
    
    @classmethod
    def setHost(self, host):
        self._hostname = host
        
    def doCheck(self):
        auth_header=self.headers.get('Authorization')
        
        if not auth_header:
            self.send_response(400)
            self.send_header("WWW-Authenticate", "Negotiate")
            self.end_headers()
            self.wfile.write(bytes("Authorization is not set"))
            return
        
        key = parseNegotiateHeader(auth_header)
        
        if not key:
            self.send_error(400, "Negotiate key is not set")
            return
        
        api = KerberosAPI(self._hostname)
        
        response, username, realm = api.check_ticket(key)
        
        if not username or not realm:
            self.send_error(401,  "Authorization failed")
            return
             
        self.send_response(200);
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("KRB_USER_NAME", username)
        self.send_header("KRB_REALM", realm)
        self.end_headers()
        self.wfile.write(bytes("response:" + response + "\n"))
        self.wfile.write(bytes("username:" + username + "\n"))
        self.wfile.write(bytes("realm:" + realm + "\n"))
        

    def doKey(self):
        
        access_hostname=self.headers.get('AccessHost')
        if not access_hostname:
            print ("AccessHost header is empty")
            self.send_error(400,  "AccessHost header is empty")
            return
            
        api = KerberosAPI(self._hostname)
        ticket = api.get_ticket(access_hostname, "HTTP");
       
        if not ticket:
            domain_user_nane=os.environ['DOMAIN_USER']
            print ("user: ", domain_user_nane, " is not access to host ", access_hostname)
            self.send_error(401, "Not access to host")
            return
        
        self.send_response(200);
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", utf8len(ticket))
        self.end_headers()
        
        self.wfile.write(bytes(ticket))
        
    def doHelp(self):
        
        try:
            file = open("help.txt", "r")
        except IOError:
            print ("Error open help file")
            self.send_error(500, "Error open help file")
            return
        
        try:
            file = open("help.txt", "r")
            helpMessage = file.read()
        except IOError:  
            print ("Error read help file")
            self.send_error(500, "Error read help file")
            
        if not helpMessage:
            print ("Help file message is empty")
            self.send_error(500, "Help file message is empty")
            return
            
        self.send_response(200);
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        
        self.wfile.write(bytes(helpMessage))
    
    def do_GET(self):
        
        if self.path == "/check":
            self.doCheck()
        elif self.path == "/key":
            self.doKey()
        elif self.path == "/help":
            self.doHelp()
        else:
            self.send_error(400)
       
host=os.environ['HOST_FSKRBSRV_DOMAIN_NAME'] 
port=int(os.environ['HOST_FSKRBSRV_PORT'])

if not host:
    print ("Error not set HOST_FSKRBSRV_DOMAIN_NAME environment")
    sys.exit(os.EX_CONFIG)
    
if port == 0 or not port:
    print ("Error not set HOST_FSKRBSRV_PORT environment")
    sys.exit(os.EX_CONFIG)

print("Running server 127.0.0.1", ":", port, " ...")
print("Domain host usage: ", host)

krbHandler = Handler
krbHandler.setHost(host)
HTTPServer(('127.0.0.1', port), krbHandler).serve_forever()

print("Server is stopped!")
