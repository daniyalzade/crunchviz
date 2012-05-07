"""A collection of utility methods for configuring logging.
"""
import logging
import logging.handlers

LOG_FORMAT = '%(asctime)s %(levelname)s pid:%(process)d, file:%(filename)s:%(lineno)d> %(message)s'

status_logger = logging.getLogger("status_logger")
stats_logger = logging.getLogger("stats_logger")

_peripheral_loggers = {
    'stats': stats_logger,
    'status': status_logger,
}

def type_of(inst, klass):
    return inst.__class__.__name__ == klass.__name__

def append_to_filename(filename, to_append):
    return filename.replace(".log", "_%s.log" % to_append)

def _get_stream_handler(logger):
    """
    Return the first stream handler the logger has, and None ow
    """
    for handler in logger.handlers:
        if type_of(handler, logging.StreamHandler):
            return handler
    return None

def _configure_error_recipients(formatter, **kwargs):
    error_recipients = kwargs.get('error_recipients', None)
    if not error_recipients:
        return
    smtp_handler = logging.handlers.SMTPHandler('localhost',
                                                'dev2@chartbeat.com',
                                                error_recipients,
                                                'Log[ERROR]'
                                                )
    smtp_handler.setLevel(logging.FATAL)
    smtp_handler.setFormatter(formatter)
    logging.getLogger().addHandler(smtp_handler)
    logging.info('configured error_recipients: %s' % error_recipients)

def _configure_stream_handler(level, formatter):
    """
    Add a stream handler if it does not already exist
    """
    root_logger = logging.getLogger()
    handler = _get_stream_handler(root_logger)
    if handler:
        handler.setLevel(level)
        handler.setFormatter(formatter)
        return
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)


def _get_log_level_from_string(string):
    """
    @param string: string
    @return int, logging level (backed by logging.LEVEL constant)
    """
    loglevel = string.lower()
    if loglevel == 'debug': return logging.DEBUG
    if loglevel == 'info': return logging.INFO
    if loglevel == 'warning': return logging.WARNING
    if loglevel == 'error': return logging.ERROR
    if loglevel == 'fatal': return logging.FATAL

    return logging.INFO


def _get_log_level(options):
    """
    @param options: pychartbeat.Options
    @return log_level: int (backed by logging.LEVEL constant)
    """
    if 'loglevel' in options and options.loglevel:
        loglevel = options.loglevel.lower()
        if loglevel == 'debug': return logging.DEBUG
        if loglevel == 'info': return logging.INFO
        if loglevel == 'warning': return logging.WARNING
        if loglevel == 'error': return logging.ERROR
        if loglevel == 'fatal': return logging.FATAL
    if 'debug' in options:
        return logging.DEBUG if options.debug else logging.INFO
    return logging.INFO

def _options_to_config(options):
    logging_config = {'filename' : options.log_file} if 'log_file' in options else {}
    logging_config['console'] = options.console if 'console' in options else False
    error_recipients = options.error_recipients if 'error_recipients' in options else None
    logging_config['error_recipients'] = error_recipients
    logging_config['level'] = _get_log_level(options)
    if 'console_level' in options:
        logging_config['console_level'] = _get_log_level_from_string(options.console_level)
    return logging_config

def _configure_peripheral_logger(filename, level, logger_type):
    peripheral_logger = _peripheral_loggers[logger_type]
    filename = append_to_filename(filename, logger_type)
    fh = logging.FileHandler(filename)
    fh.setLevel(level)
    peripheral_logger.addHandler(fh)

def basicConfig(level=logging.INFO,
                options = None,
                console = True,
                error_log = None,
                enable_status_logger = False,
                enable_stats_logger = False,
                remove_handlers=False,
                **kwargs):
    """
    Utility method for configuring logging. Note that the allowed arguments
    are (and should better be) a supperset of python's logging.basicConfig

    @param level: Logging level
    @param error_log: If provided configures another file handler to
    output error logs to the provided file name
    @param extra_args: Optional.
    """
    if options:
        basicConfig(**_options_to_config(options))
        return
    logging_format = kwargs.get('format', LOG_FORMAT)
    logging.getLogger().setLevel(level)
    formatter = logging.Formatter(logging_format)
    #Even if no stream handlers given, logging just logs to STDOUT. So,
    #if don't want to log, just set the handler level high

    console_level = kwargs.get('console_level')
    stream_level = logging.CRITICAL
    if console_level:
        stream_level = console_level
    elif console:
        stream_level = level

    _configure_stream_handler(stream_level, formatter)

    if remove_handlers:
        for h in logging.getLogger().handlers:
            logging.getLogger().removeHandler(h)

    if kwargs.get('filename', None):
        filename = kwargs['filename']
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logging.getLogger().addHandler(fh)
        #TODO: Change the portion below to use _peripheral_logger_configuration
        if enable_status_logger:
            filename = append_to_filename(filename, "status")
            fh = logging.FileHandler(filename )
            fh.setLevel(level)
            fh.setFormatter(formatter)
            status_logger.addHandler(fh)
            for handler in logging.getLogger().handlers:
                if type(handler) == logging.FileHandler:
                    status_logger.addHandler(handler)


    if error_log:
        eh = logging.FileHandler(error_log)
        eh.setLevel(logging.WARN)
        eh.setFormatter(formatter)
        logging.getLogger().addHandler(eh)

    _configure_error_recipients(formatter, **kwargs)

    logging.debug('logging configured')

