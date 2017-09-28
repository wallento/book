.. _specs.coachings:

========================
The ``coachings`` plugin
========================

..  To run only this test:

    $ doctest docs/specs/coachings.rst
    
    
    >>> import lino
    >>> lino.startup('lino_book.projects.adg.settings.doctests')
    >>> from lino.api.doctest import *
    >>> from django.db.models import Q


The :mod:`lino_xl.lib.coachings` plugin adds functionality for
managing "coachings".  A coaching is when a "coach" (a system user)
engages in regular, structured conversation with a "client".


.. contents::
  :local:



.. currentmodule:: lino_xl.lib.coachings
                   

Database structure
==================


.. class:: ClientContactBase

    Also used by :class:`aids.RefundPartner
    <lino_welfare.modlib.aids.models.RefundPartner>`.


.. class:: Coachable

    Base class for coachable client. The model specified as
    :attr:`client_model <Plugin.client_model>` must implement this.

    .. attribute:: client_state

        Pointer to ClientStates

    .. method:: get_coachings(self, period=None, *args, **flt)
                
        Return a queryset with the coachings of this client. If
        `period` is not `None`, it must be a tuple of two date
        objects. Any additional arguments are applied as filter of the
        queryset.

    .. method:: get_primary_coach(self)
                
        Return the one and only primary coach of this client (or
        `None` if there's less or more than one).

    .. method:: setup_auto_event(self, evt)

        Implements :meth:`EventGenerator.setup_auto_event
        <lino_xl.lib.cal.EventGenerator.setup_auto_event>`.

        This implements the rule that suggested evaluation events should
        be for the *currently responsible* coach if the contract's
        author no longer coaches that client.  This is relevant if
        coach changes while contract is active.

        The **currently responsible coach** is the user for which
        there is a coaching which has :attr:`does_integ
        <lino_xl.lib.coachings.CoachingType.does_integ>` set to
        `True`..

        
        
           
.. class:: ClientStates
           
    The list of **client states**.
    
    >>> rt.show(coachings.ClientStates)
    ======= ========== ============
     value   name       text
    ------- ---------- ------------
     10      newcomer   Newcomer
     20      coached    Registered
     30      former     Ended
     40      refused    Abandoned
    ======= ========== ============
    <BLANKLINE>
    
    
.. class:: ClientEvents

    The list of **observable client events**.

    >>> rt.show(coachings.ClientEvents)
    ========== ========== ==========
     value      name       text
    ---------- ---------- ----------
     active     active     Coaching
     created    created    Created
     modified   modified   Modified
     note       note       Note
    ========== ========== ==========
    <BLANKLINE>

    .. attribute:: created
                   
        Select clients whose record has been *created* during the observed
        period.
                   
    .. attribute:: modified
                   
        The choice for :class:`ClientEvents` which selects clients whose
        main record has been *modified* during the observed period.


           
.. class:: CoachingType

    The **type** of a coaching can be used for expressing different
    types of responsibilities. For example in :ref:`welfare` they
    differentiate between "General Social Service" and "Integration
    Service".

    .. attribute:: does_integ

        Whether coachings of this type are to be considered as
        integration work.

        This is used when generating calendar events for evaluation
        meetings (see
        :meth:`lino_xl.lib.coaching.Coachable.setup_auto_event`)

           
.. class:: CoachingEnding

   A **Coaching termination reason** expresses why a coaching has been
   terminated.

   >>> rt.show(coachings.CoachingTypes)
   No data to display
   
   
.. class:: Coaching

    A Coaching ("Begleitung" in German and "intervention" in French)
    is when a given client is being coached by a given user during a
    given period.

    For example in :ref:`welfare` that used is a social assistant.

.. class:: ClientContact


    A **client contact** is when a given partner has a given role for
    a given client.

    .. attribute:: client

        The :class:`Client`.

    .. attribute:: type
    
        The type of contact. Pointer to :class:`ClientContactType`.

    .. attribute:: company

        The organization.

    .. attribute:: contact_person
    
        The contact person in the organization.

    .. attribute:: contact_role
    
        The role of the contact person in the organization.

           
.. class:: ClientContactType
           
    A **client contact type** is the type or "role" which must be
    specified for a given :class:`ClientContact`.

    .. attribute:: can_refund

    Whether persons of this type can be used as doctor of a refund
    confirmation. Injected by :mod:`lino_welfare.modlib.aids`.

           
Configuration
=============

.. class:: Plugin

    .. attribute:: client_model = 'contacts.Person'

       The model to which :attr:`Coaching.client` points to.


Miscellaneous
=============


.. class:: CoachingsUser
           
    A user who has access to basic coachings functionality.


.. class:: CoachingsStaff
   
    A user who can configure coachings functionality.

.. class:: ClientCoachingsChecker
   
    Coached clients should not be obsolete.  Only coached clients
    should have active coachings.


Injects
=======

The :mod:`lino_xl.lib.coachings` plugin injects the following fields
into models of other plugins.

.. currentmodule:: lino.modlib

.. class:: users.User
    :noindex:

    .. attribute:: coaching_type

        The coaching type used for new coachings of this user.

    .. attribute:: coaching_supervisor

        Notify me when a coach has been assigned.

    
.. class:: contacts.Partner
    :noindex:

    .. attribute:: client_contact_type