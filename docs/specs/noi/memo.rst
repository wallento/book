.. doctest docs/specs/noi/memo.rst
.. _noi.specs.memo:

=========================
Memo commands in Lino Noi
=========================


>>> from lino import startup
>>> startup('lino_book.projects.team.settings.demo')
>>> from lino.api.doctest import *

The :attr:`description <lino_xl.lib.tickets.Ticket.description>` of a
ticket and the text of a comment (:mod:`short_text
<lino.modlib.comments.Comment.short_text>`) are rich HTML text fields
which can contain simple HTML formatting like links, tables, headers,
enumerations.

And additionally they can contain :mod:`memo markup commands
<lino.utils.memo>`.

A memo markup command is a fragment of text between square brackets
which will be "rendered" (converted into another fragment) when your
description text is being displayed at certain places.

of the form ``[foo bar baz]``. These
memo commands are going to


Lino Noi `memo` command reference
=================================

.. _memo.url:

url
===

Insert a link to an external web page. The first argument is the URL
(mandatory). If no other argument is given, the URL is used as
text. Otherwise the remaining text is used as the link text.

The link will always open in a new window (``target="_blank"``)

Usage examples:

- ``[url http://www.example.com]``
- ``[url http://www.example.com example]``
- ``[url http://www.example.com another example]``

..  test:
    >>> ses = rt.login()
    >>> print(ses.parse_memo("See [url http://www.example.com]."))
    See <a href="http://www.example.com" target="_blank">http://www.example.com</a>.
    >>> print(ses.parse_memo("See [url http://www.example.com example]."))
    See <a href="http://www.example.com" target="_blank">example</a>.
    
    >>> print(ses.parse_memo("""See [url https://www.example.com
    ... another example]."""))
    See <a href="https://www.example.com" target="_blank">another example</a>.

    A possible situation is that you forgot the space:
    
    >>> print(ses.parse_memo("See [urlhttp://www.example.com]."))
    See [urlhttp://www.example.com].


.. _memo.ticket:

ticket
======

Refer to a ticket. Usage example: 

  See ``[ticket 1]``.

Note that the current renderer decides how to render the link. For
example, the default user interface :mod:`lino.modlib.extjs` (or
:mod:`lino_extjs6.extjs6`, depending on our :attr:`default_ui
<lino.core.site.Site.default_ui>` setting) will render it like this:

>>> ses = rt.login('robin',
...     renderer=settings.SITE.kernel.default_ui.renderer)
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="javascript:Lino.tickets.Tickets.detail.run(null,{ &quot;record_id&quot;: 1 })" title="F&#246;&#246; fails to bar when baz">#1</a>.

While the :mod:`lino.modlib.bootstrap3` user interface will render it
like this:

>>> ses = rt.login(renderer=dd.plugins.bootstrap3.renderer)
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="/bs3/tickets/Tickets/1" title="F&#246;&#246; fails to bar when baz">#1</a>.

Or the plain text renderer will render:

>>> ses = rt.login()
>>> print(ses.parse_memo("See [ticket 1]."))
See <a href="Detail" title="F&#246;&#246; fails to bar when baz">#1</a>.


.. _memo.company:

company
=======

Refer to a company. Usage example::

    I met Joe from [company 1] and we agreed...

.. 
    >>> print(rt.login().parse_memo("See [company 1]."))
    See [ERROR Company matching query does not exist. in '[company 1]' at position 4-15].


.. _memo.person:

person
======

Refer to a person. Usage example::

    I met [person 7 Joe] and we agreed...



.. _memo.py:

py
==

Refer to a Python object.

Usage examples:

- ``[py lino]``
- ``[py lino.utils.memo]``
- ``[py lino_xl.lib.tickets.models.Ticket]``
- ``[py lino_xl.lib.tickets.models.Ticket tickets.Ticket]``
  
..  
    >>> ses = rt.login()
    >>> print(ses.parse_memo("[py lino]."))
    <a href="https://github.com/lino-framework/lino/blob/master/lino/__init__.py" target="_blank">lino</a>.
    
    >>> print(ses.parse_memo("[py lino_xl.lib.tickets.models.Ticket]."))
    <a href="https://github.com/lino-framework/xl/blob/master/lino_xl/lib/tickets/models.py" target="_blank">lino_xl.lib.tickets.models.Ticket</a>.
    
    >>> print(ses.parse_memo("[py lino_xl.lib.tickets.models.Ticket.foo]."))
    <a href="Error in Python code (type object 'Ticket' has no attribute 'foo')" target="_blank">lino_xl.lib.tickets.models.Ticket.foo</a>.
    
    >>> print(ses.parse_memo("[py lino_xl.lib.tickets.models.Ticket Ticket]."))
    <a href="https://github.com/lino-framework/xl/blob/master/lino_xl/lib/tickets/models.py" target="_blank">Ticket</a>.

    Non-breaking spaces are removed from command text:
    
    >>> print(ses.parse_memo(u"[py lino]."))
    <a href="https://github.com/lino-framework/lino/blob/master/lino/__init__.py" target="_blank">lino</a>.


.. 
    >>> from lino.utils.diag import analyzer
    >>> print(analyzer.show_memo_commands())
    ... #doctest: +NORMALIZE_WHITESPACE
    <BLANKLINE>
    - [company ...] : 
      Insert a reference to the specified database object.
    <BLANKLINE>
      The first argument is mandatory and specifies the primary key.
      All remaining arguments are used as the text of the link.
    <BLANKLINE>
    - [person ...] : 
      Insert a reference to the specified database object.
    <BLANKLINE>
      The first argument is mandatory and specifies the primary key.
      All remaining arguments are used as the text of the link.
    <BLANKLINE>
    - [ticket ...] : 
      Insert a reference to the specified database object.
    <BLANKLINE>
      The first argument is mandatory and specifies the primary key.
      All remaining arguments are used as the text of the link.
    <BLANKLINE>


The ``obj2memo`` method
=======================

You might want to programmatically generate a text containing memo
markup.

For example when your code knows some database object and you want to
create a description which would refer to your object if rendered with
memo:

>>> ar = rt.login('robin')
>>> obj = rt.models.tickets.Ticket.objects.get(pk=1)
>>> txt = ar.obj2memo(obj)
>>> print(txt)
[ticket 1] (Föö fails to bar when baz)

Let's also check whether the produced text is valid:

>>> print(ar.parse_memo(txt))
<a href="Detail" title="F&#246;&#246; fails to bar when baz">#1</a> (Föö fails to bar when baz)


      
