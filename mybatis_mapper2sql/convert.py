import re

from .params import get_params

query_types = ['sql', 'select', 'insert', 'update', 'delete']


def convert_children(mybatis_mapper, child, **kwargs):
    """
    Get children info
    :param mybatis_mapper:
    :param child:
    :param kwargs:
    :return:
    """
    if child.tag in query_types:
        return convert_parameters(child, text=True, tail=True)
    elif child.tag == 'include':
        return convert_include(mybatis_mapper, child, properties=kwargs.get('properties'))
    elif child.tag == 'if':
        return convert_if(mybatis_mapper, child)
    elif child.tag in ('choose', 'when', 'otherwise'):
        return convert_choose_when_otherwise(mybatis_mapper, child)
    elif child.tag in ('trim', 'where', 'set'):
        return convert_trim_where_set(mybatis_mapper, child)
    elif child.tag == 'foreach':
        return convert_foreach(mybatis_mapper, child)
    elif child.tag == 'bind':
        return convert_bind(child)
    else:
        return ''


def convert_parameters(child, text=False, tail=False):
    """
    Get child text or tail
    :param child:
    :param text:
    :param tail:
    :return:
    """
    p = re.compile('\S')
    # Remove empty info
    child_text = child.text if child.text else ''
    child_tail = child.tail if child.tail else ''
    child_text = child_text if p.search(child_text) else ''
    child_tail = child_tail if p.search(child_tail) else ''
    # all
    if text and tail:
        convert_string = child_text + child_tail
    # only_text
    elif text:
        convert_string = child_text
    # only_tail
    elif tail:
        convert_string = child_tail
    else:
        convert_string = ''
    # replace params
    params = get_params(child)
    params['all'] = params['#'] + params['$']
    for param in params['all']:
        convert_string = convert_string.replace(param['full_name'], str(param['mock_value']))
    # convert CDATA string
    convert_cdata(convert_string)
    return convert_string


def convert_include(mybatis_mapper, child, properties=None):
    # Add Properties
    properties = properties if properties else dict()
    for next_child in child:
        if next_child.tag == 'property':
            properties[next_child.attrib.get('name')] = next_child.attrib.get('value')
    convert_string = ''
    include_child_id = child.attrib.get('refid')
    for change in ['#', '$']:
        string_regex = '\\' + change + '\{.+?\}'
        if re.match(string_regex, include_child_id):
            include_child_id = include_child_id.replace(change + '{', '').replace('}', '')
            include_child_id = properties.get(include_child_id)
            break
    include_child = mybatis_mapper.get(include_child_id)
    convert_string += convert_children(mybatis_mapper, include_child)
    # add include text
    convert_string += convert_parameters(child, text=True)
    for next_child in include_child:
        convert_string += convert_children(mybatis_mapper, next_child, properties=properties)
    # add include tail
    convert_string += convert_parameters(child, tail=True)
    return convert_string


def convert_if(mybatis_mapper, child):
    convert_string = ''
    test = child.attrib.get('test')
    # Add if text
    convert_string += convert_parameters(child, text=True)
    for next_child in child:
        convert_string += convert_children(mybatis_mapper, next_child)
    convert_string += '-- if(' + test + ')\n'
    # Add if tail
    convert_string += convert_parameters(child, tail=True)
    return convert_string


def convert_choose_when_otherwise(mybatis_mapper, child):
    convert_string = ''
    for next_child in child:
        if next_child.tag == 'when':
            test = next_child.attrib.get('test')
            convert_string += convert_parameters(next_child, text=True, tail=True)
            convert_string += '-- if(' + test + ')'
        elif next_child.tag == 'otherwise':
            convert_string += convert_parameters(next_child, text=True, tail=True)
            convert_string += '-- otherwise'
        convert_string += convert_children(mybatis_mapper, next_child)
    return convert_string


def convert_trim_where_set(mybatis_mapper, child):
    if child.tag == 'trim':
        prefix = child.attrib.get('prefix')
        prefix_overrides = child.attrib.get('prefixOverrides')
        suffix_overrides = child.attrib.get('suffix_overrides')
    elif child.tag == 'set':
        prefix = 'SET'
        prefix_overrides = None
        suffix_overrides = ','
    elif child.tag == 'where':
        prefix = 'WHERE'
        prefix_overrides = 'and|or'
        suffix_overrides = None
    else:
        return ''

    convert_string = ''
    # Add trim/where/set text
    convert_string += convert_parameters(child, text=True)
    # Convert children first
    for next_child in child:
        convert_string += convert_children(mybatis_mapper, next_child)
    # Remove prefixOverrides
    if prefix_overrides:
        regex = '^[\s]*?' + prefix_overrides
        convert_string = re.sub(regex, '', convert_string, count=1, flags=re.I)
    # Remove suffixOverrides
    if suffix_overrides:
        regex = suffix_overrides + '(\s+--.+)?$'
        convert_string = re.sub(regex, r'\1', convert_string, count=1, flags=re.I)
    # Add Prefix if String is not empty
    if re.search('\S', convert_string):
        convert_string = prefix + ' ' + convert_string
    # Add trim/where/set tail
    convert_string += convert_parameters(child, tail=True)
    return convert_string


def convert_foreach(mybatis_mapper, child):
    collection = child.attrib.get('collection')
    item = child.attrib.get('item')
    index = child.attrib.get('index')
    open = child.attrib.get('open', '')
    close = child.attrib.get('close', '')
    separator = child.attrib.get('separator')
    convert_string = ''
    # Add foreach text
    convert_string += convert_parameters(child, text=True)
    for next_child in child:
        convert_string += convert_children(mybatis_mapper, next_child)
    # Add two items
    convert_string = open + convert_string + separator + convert_string + close
    # Add foreach tail
    convert_string += convert_parameters(child, tail=True)
    return convert_string


def convert_bind(child):
    """
    :param child:
    :return:
    """
    name = child.attrib.get('name')
    value = child.attrib.get('value')
    convert_string = ''
    convert_string += convert_parameters(child, tail=True)
    convert_string = convert_string.replace(name, value)
    return convert_string


def convert_cdata(string, reverse=False):
    """
    Replace CDATA String
    :param string:
    :param reverse:
    :return:
    """
    if reverse:
        string = string.replace('&', '&amp;')
        string = string.replace('<', '&lt;')
        string = string.replace('>', '&gt;')
        string = string.replace('"', '&quot;')
    else:
        string = string.replace('&amp;', '&')
        string = string.replace('&lt;', '<')
        string = string.replace('&gt;', '>', )
        string = string.replace('&quot;', '"')
    return string
