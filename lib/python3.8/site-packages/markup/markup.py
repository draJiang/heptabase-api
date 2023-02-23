from cStringIO import StringIO

def HTMLmarkup(tag, text=None, **attributes):
    """
    markups the text with the tag and
    attributes
    """

    # ideally, this woulod be cached for cascading calls
    s = StringIO()
    
    s.write('<%s' % tag)
    for attribute, value in attributes.items():
        if value is None:
            s.write(' %s' % attribute)
        else:
            s.write(' %s="%s"' % (attribute, value))

    if text:
        if tag in block_level:
            s.write('>\n%s\n</%s>' % (text, tag))
        else:
            s.write('>%s</%s>' % (text, tag))
    else:
        s.write('/>')
    return s.getvalue()

tags = [ 'a',
         'b', 'body', 'br',
         'center',
         'dd', 'div', 'dl', 'dt', 'em',
         'form',
         'h1', 'h2', 'h3', 'head', 'html',
         'i', 'img', 'input',
         'li', 'lh',
         'ol', 'option',
         'p',
         'select', 'span', 'strong',
         'table', 'td', 'textarea', 'th', 'title', 'tr',
         'ul',
         ]

for _i in tags:
    globals()[_i] = lambda x=None, _i=_i, **y: HTMLmarkup(_i, x, **y)

# block-level elements
# from http://htmlhelp.com/reference/html40/block.html
block_level = set(['address',
                   'blockquote',
                   'center',
                   'dir', 'div', 'dl',
                   'fieldset', 'form',
                   'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
                   'isindex',
                   'menu',
                   'noframes', 'noscript',
                   'ol',
                   'p', 'pre',
                   'table',
                   'ul',
                   # not really block level, but act like it is
                   'body',
                   'dd', 'dt',
                   'frameset',
                   'head', 'html',
                   'iframe',
                   'tbody', 'tfoot', 'th', 'thead', 'tr'])

### front ends to tags to make our lives easier
### these don't stomp on tags -- they're just front ends
### (these should go in a separate file)

def image(src, **attributes):
    attributes['src'] = src
    return img(**attributes)

def link(location, description=None, **attributes):
    if description is None:
        description = location
    attributes['href'] = location
    return a(description, **attributes)

def listify(items, ordered=False, **attributes):
    """
    return a HTML list of iterable items
    * ordered: whether the list is a <ol> (True) or an <ul> (False)
    * item_attributes: attributes applied to each list item
    """

    # type of list
    if ordered:
        func = ol
    else:
        func = ul

    item_attributes = attributes.pop('item_attributes', {})
    listitems = [ li(item, **item_attributes) for item in items ]
    return func('\n'.join(listitems), **attributes)

def definition_list(items, header=None, **attributes):
    """definition list
    items can be a dictionary or a list of 2-tuples"""
    # XXX no attributes for header, dts, dds (yet)

    if header is None:
        header = '',
    else:
        header = '%s\n' % lh(header)

    # convert dicts to lists of 2-tuples
    if hasattr(items, 'items'):
        items = items.items() 

    items = [ dt(term) + dd(definition) for term, definition in items ]
    return dl(('\n%s%s\n' % ( header, '\n'.join(items))), **attributes)

def tablify(rows, header=False, item_attributes=None, 
            **attributes):
    """return an HTML table from a iterable of iterable rows"""
    
    if item_attributes is None:
        item_attributes = {}

    retval = []
    if header:
        markup = th
    else:
        markup = td

    for row in rows:
        retval.append('\n'.join([markup(str(item)) for item in row]))
        markup = td

    return table('\n\n'.join([tr(row) for row in retval]))

def wrap(string, pagetitle=None, stylesheets=(), icon=None, head_markup=()):
    """wrap a string in a webpage"""

    _head = ''
    if pagetitle:
        _head += title(pagetitle)
    rel = 'stylesheet'
    for i in stylesheets:
        attributes = dict(rel=rel,
                          type='text/css')        
        if hasattr(i, '__iter__'):
            # assume a 2-tuple
            attributes['href'] = i[0]
            attributes['title'] = i[1]
        else:
            attributes['href'] = i
        _head += '\n' + HTMLmarkup('link', None, **attributes)
        rel = 'alternate stylesheet' # first stylesheet is default
    if icon:
        _head += '\n' + HTMLmarkup('link', None, href=icon)

    if head_markup:
        # additional markup for <head>
        if isinstance(head_markup, basestring):
            _head += '\n' + head_markup
        else:
            for item in head_markup:
                _head += '\n' + item
    if _head:
        _head = head(_head)        

    return html('%s\n\n%s' % ( _head, body(string) ) )
