import logging
import logging.handlers
import socket
import time

fqdn = socket.getfqdn()

class MiniSysLogHandler(logging.handlers.SysLogHandler):
    """ The SysLogHandler that ships in the Python stdlib doesn't generate
    RFC5424 compliant messages whether wanting to use STRUCTURED-DATA or not.

    This subclasses that handler and overrides emit() in order to generate
    compliant messages.

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

    That library also has external dependencies on pytz and won't run on Python
    2.6 due to a dependency on OrderedDict.

    """
  
    def __init__(self,
                address=('127.0.0.1', 514),
                appname = '-',
                procid = '-',
                msgid = '-',
                sd=False):
        """ Allow setting of APPNAME, PROCID, and MSGID at init. 
        XXX This version actually always sets MSGID to the loglevel (eg INFO, CRIT)        
        """

        self.address = address
        self.appname = appname
        self.msgid = msgid
        self.procid = procid
        self.sd = sd
        super(MiniSysLogHandler, self).__init__(address=self.address)
    
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
            msg = self.format(record)
            if self.ident:
                msg = self.ident + msg
            if self.append_nul:
                msg += '\000'

            # We need to convert record level to lowercase, maybe this will
            # change in the future.

            prio = '<%d>1 ' % self.encodePriority(
                                self.facility,
                                self.mapPriority(record.levelname))

            prio = prio.encode('utf-8')

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
                msg = prio + '%s %s %s %s - %s' % (ts,
                                                   fqdn,
                                                   self.appname,
                                                   self.procid,
                                                   record.levelname,
                                                   msg)
            
                
            msg = prio + msg
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
    syslog = MiniSysLogHandler(appname='CoolApp', procid='TAG', sd=False)
    logger.addHandler(syslog)
    logger.setLevel(logging.INFO)
    logger.info(' A basic message, without structured-data')
    logger.sd = True  # 
    logger.info('[ourSDID@32473 super="cala" fraja="listic"]')




