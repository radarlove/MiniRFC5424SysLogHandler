# MiniRFC5424SysLogHandler
Minimal approach to RFC5424 compliant logs
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
