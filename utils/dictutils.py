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
