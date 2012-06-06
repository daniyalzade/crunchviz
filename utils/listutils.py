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

def adv_enumerate(list_,
        start=0,
        end=None,
        frequency=100,
        use_print=False,
        get_tuple=False,
        ):
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
    for i, item in enumerate(list_, start=start):
        if not i % frequency:
            _display_msg("completed %s/%s" % (i, len_))
        if end and i >= end:
            raise StopIteration
        yield (i, item) if get_tuple else item
