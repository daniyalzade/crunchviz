import logging

def _display_msg(msg, use_print=False):
    """
    @param msg: str
    @param use_print: bool
    """
    if use_print:
        print msg
        return
    logging.info(msg)

def iterate_with_progress(list_, frequency=100, use_print=False):
    """
    @param list_: list
    @param frequency: int
    @param use_print: bool
    @return: Generator
    """
    len_ = 'NA'
    try:
        len_ = len(list_)
    except TypeError:
        pass
    for i, item in enumerate(list_):
        if not i % frequency:
            _display_msg("completed %s/%s" % (i, len_))
        yield item
