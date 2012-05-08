def jsonp(klass):
    """
    Modifies the original tornado request handler class to be able to
    seamlessly handle jsonp requests, with 'jsonp' in the request params.

    @param klass: RequestHandler.class
    @return modifiedklass: RequestHandler.class
    """
    orig_write = klass.write

    def write(self, chunk):
        callback = self.get_argument('jsonp', None)
        if callback and isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        elif isinstance(chunk, dict):
            # Make sure to set content-type otherwise tornado will set it to
            # text/javascript.
            chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        # At this point chunk is guaranteed to be a basestring
        if callback:
            chunk = callback + "(" + chunk + ");"
        orig_write(self, chunk)

    klass.write = write
    return klass
