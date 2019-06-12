import logging
import logging.handlers
import socket
import time

fqdn = socket.getfqdn()

class MiniSysLogHandler(logging.handlers.SysLogHandler):
    """ The SysLogHandler that ships in the Python stdlib doesn't generate
    RFC5424 compliant messages whether wanting to use STRUCTURED-DATA or not.

    This subclasses that handler and overrides emit() in order to generate
    compliant messages with a minimalistic approach.

    Using the following in rsyslog.conf::

	$ActionFileDefaultTemplate RSYSLOG_SyslogProtocol23Format

    will print the full message to /var/log/messages or similar.

    The MiniSysLogHandler accepts arguments like MSGID at initialization, so no
    arguments or dictionaries need to be added to every invocation.  The normal
    call signature is used::

    logger.info('my info message')
    logger.debug('my debug message')

    Developers not familiar with RFC5424 will generate compliant logs by
    default.

    Another library exists to do this called:

     rfc5424-syslog-handler
     
    but changes the call signature to one requiring other arguments (e.g.
    extra=somedict)

    That library also has external dependencies on pytz.

    This one assumes Zulu time, or UTC.


    Sample usage::

            if __name__ == '__main__':

                logger = logging.getLogger('minilogger')
                syslog = MiniSysLogHandler(appname='CoolApp', procid='TAG')
                logger.addHandler(syslog)
                logger.setLevel(logging.INFO)
                logger.info('A basic message, without structured-data')
                syslog.sd = True # 
                logger.info('[ourSDID@32473 super="cala" fraja="listic"]')

    /var/log/messages::
	
	<14>1 2019-06-12T22:07:17.772Z img0 CoolApp TAG INFO - A basic message, without structured-data
	<14>1 2019-06-12T22:07:17.772Z img0 CoolApp TAG INFO [ourSDID@32473 super="cala" fraja="listic"] 

    """
  
    def __init__(self,
                appname = '-',
                procid = '-',
                msgid = '-',
                address=('127.0.0.1', 514),
                sd=False):
        """ Allow setting of APPNAME, PROCID, and MSGID at init. 
        XXX This version actually always sets MSGID to the loglevel (eg INFO, CRIT)        
        """

        self.address = address
        self.appname = appname
        self.msgid = msgid
        self.procid = procid
        self.sd = sd
        super(MiniSysLogHandler, self).__init__()
    
    def get_timestamp(self, record):
        """ RFC 5424 timestamp with milliseconds from the LogRecord.  There is only ZULU time. """

        ct = time.gmtime(record.created)
        t = time.strftime('%Y-%m-%dT%H:%M:%S', ct)
        s = '%s.%03dZ' % (t, record.msecs)
        return s
    

    def emit(self, record):
        """
        Emit an RFC 5424 compliant record.

        The record is formatted, and then sent to the syslog server. If
        exception information is present, it is NOT sent to the server.
        """
        try:

            msg = self.format(record) + '\000'

            # We need to convert record level to lowercase, maybe this will
            # change in the future.

            prio = '<%d>1 ' % self.encodePriority(
                                self.facility,
                                self.mapPriority(record.levelname))


            if type(msg) is unicode:
                msg = msg.encode('utf-8')
            ts = self.get_timestamp(record)

            # Message is a string. Convert to bytes as required by RFC 5424
            msg = msg.encode('utf-8')

            if self.sd is True:
                msg = prio + '%s %s %s %s %s %s' % (ts,
                                                   fqdn,
                                                   self.appname,
                                                   self.procid,
                                                   record.levelname,
                                                   msg)
            else:
                msg = prio + '%s %s %s %s %s - %s' % (ts,
                                                   fqdn,
                                                   self.appname,
                                                   self.procid,
                                                   record.levelname,
                                                   msg)
                
            if self.unixsocket:
                try:
                    self.socket.send(msg)
                except OSError:
                    self.socket.close()
                    self._connect_unixsocket(self.address)
                    self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                self.socket.sendto(msg, self.address)
            else:
                self.socket.sendall(msg)
        except Exception:
            self.handleError(record)



if __name__ == '__main__':

    logger = logging.getLogger('minilogger')
    syslog = MiniSysLogHandler(appname='CoolApp', procid='TAG')
    logger.addHandler(syslog)
    logger.setLevel(logging.INFO)
    logger.info('A basic message, without structured-data')
    syslog.sd = True # 
    logger.info('[ourSDID@32473 super="cala" fraja="listic"]')


    #grep CoolApp /var/log/messages::
    
    #<14>1 2019-06-12T22:07:17.772Z img0 CoolApp TAG INFO - A basic message, without structured-data
    #<14>1 2019-06-12T22:07:17.772Z img0 CoolApp TAG INFO [ourSDID@32473 super="cala" fraja="listic"] 

