import datetime
import time

def get_dotted(data, field, default=None, delimiter='.'):
    """Get a nested subfield inside data using Mongo style dotted notation
    notation. For example:
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        get_dotted_field(data, 'b.d.e') => 3
    """
    if not delimiter in field:
        return data.get(field, default)

    components = field.split(delimiter)
    components.reverse()
    while components and isinstance(data, dict):
        data = data.get(components.pop())

    # If there are components left, the final dest wasn't reached.
    if components or data == None:
        return default
    return data

def set_dotted(data, field, value, delimiter='.'):
    """Set a nested subfield inside data using Mongo style dotted notation
    notation. For example:
        data = {'a': 1, 'b': {'c': 2, 'd': {'e': 3}}}
        set_dotted_field(data, 'b.d.e', 4)
        data == {'a': 1, 'b': {'c': 2, 'd': {'e': 4}}}
    """
    if not delimiter in field:
        data[field] = value
    else:
        next_field, remaining_fields = field.split(delimiter, 1)

        # If next_field isn't there, create it so we can move on.
        if next_field not in data:
            data[next_field] = {}

        set_dotted(data[next_field], remaining_fields, value, delimiter=delimiter)

def make_jsonable(data, human_readable=False):
    """Make jsonable data. As of now, it'll convert:
    * Dicts with values that aren't jsonable to jsonable
      values, recursively.
    * Datetime objects into seconds since epoch, unless 'human_readable' is
        specified, in which case it's a nice string.

    @param human_readable: If True, turn dates into readable strings.
    @return dict
    """
    if type(data) == datetime.datetime:
        if not human_readable:
            data = time.mktime(data.timetuple())
        else:
            data = data.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, dict):
        # Dont blindly make it a dict, since data could be of type SON
        to_return = dict(data)
        for key in data:
            jsonable_key = make_jsonable(key, human_readable)
            del to_return[key]
            to_return[jsonable_key] = make_jsonable(data[key], human_readable)
        data = to_return
    elif isinstance(data, tuple):
        data = tuple([make_jsonable(i, human_readable) for i in data])
    elif isinstance(data, list):
        data = list(data) # copy it first
        for i, item in enumerate(data):
            data[i] = make_jsonable(item, human_readable)
    return data

