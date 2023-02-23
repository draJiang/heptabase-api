import markup
from cStringIO import StringIO

class Form(object):
    """a simple class for HTML forms"""

    type_validators = {} # validators inherit to type

    def __init__(self, method='post', action=None, submit='Submit', post_html=''):
        """
        * post_html: html to include before the submit button
        """
        self.method = method
        self.action = action
        self.submit = submit
        self.post_html = post_html
        self.elements = []
        self.validators = {} # keys=tuples of names; values=validators

    def __call__(self, errors=None):
        """render the form"""
        retval = StringIO()
        print >> retval

        def name_field(element):
            if not element['name']:
                return ''
            title={}
            help = element.get('help')
            if help:
                title['title'] = help
            return markup.span(markup.strong('%s:' % element['name']), **title)

        # print the form as a table
        table = [ [ name_field(element), element['html'] ]
                  for element in self.elements ]
        if errors:
            for row, element in zip(table, self.elements):
                error = errors.get(element['name'], '')
                if error:
                    if not isinstance(error, basestring):
                        if len(error) == 1:
                            error = error[0]
                        else:
                            error = markup.listify(error)
                    error = markup.div(error, **{ 'class': 'error' })
                row.append(error)
            
        print >> retval, markup.tablify(table)
        print >> retval, self.post_html

        # each form has a submit button
        # XXX this should probably be more customizable
        print >> retval, markup.input(None, type='submit', name='submit',
                                      value=self.submit),

        args = { 'method': self.method,
                 'enctype': 'multipart/form-data'}
        if self.action is not None:
            args['action'] = self.action
        return markup.form(retval.getvalue(), **args)

    ### functions for validation

    def validate(self, post):
        """validate the form from the (POST) data
        post should be a dictionary (MultiDict)
        returns a dictionary of errors (empty dict == success)
        validator functions can denote failure in three ways:
        * raise an exception (currently any[!])
        * return a string -- assumed to be an error string
        * return False -- the error
        """

        errors = {}

        def add_error(name, error):
            if not errors.has_key(name):
                errors[name] = []
            errors[name].append(error)

        for names, validators in self.validators.items():
            args = [ post.get(arg) for arg in names ]
            error = None

            for validator in validators:
                try:
                    validation = validator(*args)
                except Exception, e: # horrible!
                    error = str(e)
                else:
                    if isinstance(validation, basestring):
                        error = validation # error string
                    elif validation == False:
                        error = "Illegal value for %s" % name
                if error:
                    for name in names:
                        add_error(name, error)
                    
        return errors

    ### functions to add form elements
    # each of these should be decorated to have:
    # * a name/label
    # * a validator (optional)
    # (depending on type, an additional validator may be implied)

    def textfield(self, name, value=None, **kw):
        kwargs = dict(name=name, type='text')
        if value is not None:
            kwargs['value'] = value
            kwargs['size'] = '%d' % len(value)
        kwargs.update(kw)
        return markup.input(None, **kwargs)

    def password(self, name):
        return markup.input(None, type='password', name=name)

    def hidden(self, name, value):
        return markup.input(None, type='hidden', name=name, value=value)

    def file_upload(self, name):
        return markup.input(None, type='file', name=name)

    def menu(self, name, items):
        # first item is selected by default
        retval = '\n'.join([ markup.option(item) for item in items])
        return markup.select('\n%s\n' % retval, name=name)

    def checkboxes(self, name, items, checked=set()):
        retval = []
        checked = set(checked)
        for item in items:
            kw = { 'name': name, 'value': item, 'type': 'checkbox' }
            if item in checked:
                kw['checked'] = 'checked'

            # XXX hacky;  ideally, one would use a list with no bullets
            retval.append('%s%s<br/>' % (markup.input(None, **kw), item))
            
        return '\n'.join(retval)

    def radiobuttons(self, name, items, checked=None, joiner='<br/>'):
        if checked is None:
            checked = items[0]
        joiner = "%s\n" % joiner
        retval = []
        for item in items:
            title = None
            if hasattr(item, '__iter__'):
                item, title = item
            kw = dict(type='radio', name=name, value=item)
            if item == checked:
                kw['checked'] = None

            # display contextual help
            if title:
                title = dict(title=title)
            else:
                title = {}
                
            retval.append(markup.span('%s%s' % (item, markup.input(**kw)),
                          **title))
            
        return joiner.join(retval)

    def add_password_confirmation(self, password='Password',
                                  confirmation='Confirm password',
                                  validators=None):
        """add password and confirm password fields"""
        if validators is None:
            validators = []
        validators.append(lambda x: bool(x.strip()) or "Please provide a password")
        self.add_element('password', password)
        self.add_element('password', confirmation)
        self.validators[(password,)] = validators
        match = lambda x, y: (x == y) or "Fields don't match"
        self.validators[(password, confirmation)] = [ match ]

    
    def add_element(self, func, name, *args, **kwargs):

        if isinstance(func, basestring):
            func_name = func
            func = getattr(self, func)
        else:
            func_name = func.func_name

        # form validators
        validators = self.type_validators.get(func_name, [])
        validators.extend(kwargs.pop('validators', []))
        self.validators[(name, )] = validators

        # don't diplay hidden elements
        if func_name == 'hidden':
            self.elements.append(dict(name='', 
                                      html=func(name, *args, **kwargs)))
            return

        # allow contextual help
        help = kwargs.pop('help', None)

        # allow alternate input names
        # XXX breaks validation?
        input_name = kwargs.pop('input_name', name)

        self.elements.append(dict(name=name, 
                                  html=func(input_name, *args, **kwargs),
                                  help=help))

    # TODO: add validation
    def add_elements(self, name, funcs, args, kwargs, help=None):
        """add multiple elements to the form
        * name: master name; element names will be derived from this
        * funcs: list of html-returning functions to add
        * args: list of positional args: [ [ args1 ], [ args2], ... ]
        * kwargs: dictionary of kwargs: [ { kwargs1 }, { kwargs2 }, ... ]
        """
        html = StringIO()
        
        for func, index in zip(funcs, range(len(funcs))):
            # no validation (yet)
            if isinstance(func, basestring):
                func = getattr(self, func)
            print >> html, func('%s-%d' % (name, index), *args[index],
                                **kwargs[index])
        self.elements.append(dict(name=name,
                                  html=html.getvalue(),
                                  help=help))


    
