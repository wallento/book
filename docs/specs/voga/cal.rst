.. doctest docs/specs/voga/cal.rst
.. _voga.tested.cal:

===================================
Calendar functionality in Lino Voga
===================================

.. doctest initialization:

   >>> from lino import startup
   >>> startup('lino_book.projects.roger.settings.demo')
   >>> from lino.api.doctest import *

This document describes how :ref:`voga` extends the default calendar
functions (documented separately in :ref:`book.specs.cal`).

.. currentmodule:: lino_voga.lib.cal


Workflow
========

The following workflow of calendar entries and guests (presences) are
defined in :mod:`lino_voga.lib.cal.workflows`.

>>> rt.show(cal.EntryStates)
======= ============ ============ ============= =================== ======== ============= =========
 value   name         text         Button text   Edit participants   Stable   Transparent   No auto
------- ------------ ------------ ------------- ------------------- -------- ------------- ---------
 10      suggested    Suggested    ?             Yes                 No       No            No
 20      draft        Draft        ☐             Yes                 No       No            No
 50      took_place   Took place   ☑             Yes                 Yes      No            No
 70      cancelled    Cancelled    ☒             No                  Yes      Yes           Yes
======= ============ ============ ============= =================== ======== ============= =========
<BLANKLINE>

>>> rt.show(cal.GuestStates)
======= ========= ============ ========= =============
 value   name      Afterwards   text      Button text
------- --------- ------------ --------- -------------
 10      invited   No           Invited   ?
 40      present   Yes          Present   ☑
 50      missing   Yes          Missing   ☉
 60      excused   No           Excused   ⚕
======= ========= ============ ========= =============
<BLANKLINE>


Rooms
=====


.. class:: Room

    Extends :class:`lino_xl.lib.cal.Room` by adding one field:

    .. attribute:: fee

        The default fee to pay when renting this room to an external
        organization.

    
>>> show_fields(cal.Room, 'name calendar fee company')
+---------------+--------------+---------------------------------------------------------------+
| Internal name | Verbose name | Help text                                                     |
+===============+==============+===============================================================+
| name          | Designation  | The designation of the room. This should (but is not required |
|               |              | to) be unique.                                                |
+---------------+--------------+---------------------------------------------------------------+
| calendar      | Calendar     | Calendar where events in this room are published.             |
+---------------+--------------+---------------------------------------------------------------+
| fee           | Tariff       | The default fee to pay when renting this room to an external  |
|               |              | organization.                                                 |
+---------------+--------------+---------------------------------------------------------------+
| company       | Responsible  | Pointer to Company.                                           |
+---------------+--------------+---------------------------------------------------------------+
         

The following rooms are defined in the
:mod:`lino_book.projects.roger.settings.fixtures.voga` demo fixture.

>>> ses = rt.login('robin')
>>> ses.show(cal.Rooms)  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS -REPORT_NDIFF
================== ================== ===================== ================== =================== ============================= ==============================
 Designation        Designation (de)   Designation (fr)      Calendar           Tariff              Responsible                   Locality
------------------ ------------------ --------------------- ------------------ ------------------- ----------------------------- ------------------------------
 Mirrored room      Spiegelsaal        Salle miroîtée        Mirrored room      Spiegelraum Eupen   Lern- und Begegnungszentrum   4700 Eupen
 Computer room      Computersaal       Salle informatique    Computer room      Rent per meeting    Lern- und Begegnungszentrum   4700 Eupen
 Conferences room   Konferenzraum      Salle de conférence   Conferences room                       Lern- und Begegnungszentrum   4750 Butgenbach / Bütgenbach
 Computer room      Computersaal       Salle informatique    Computer room                          Lern- und Begegnungszentrum   4750 Butgenbach / Bütgenbach
 Computer room      Computersaal       Salle informatique    Computer room                          Zur Klüüs                     4720 Kelmis / La Calamine
 Computer room      Computersaal       Salle informatique    Computer room                          Sport- und Freizeitzentrum    4780 Sankt Vith / Saint-Vith
 Outside            Draußen            Outside               Outside
================== ================== ===================== ================== =================== ============================= ==============================
<BLANKLINE>

(The last room, because it has no company, caused a bug which was fixed on
:blogref:`20140920`)



Automatic calender events
=========================

For the following examples we select an activity which did not yet
start, i.e. which starts after :meth:`lino.core.site.Site.today`.

>>> for obj in courses.Course.objects.filter(start_date__gte=dd.today()):
...     print("Activity #{} starts {} and has {} events".format(obj.id, obj.start_date, obj.max_events))
...     # doctest: +NORMALIZE_WHITESPACE
Activity #12 starts 2015-07-11 and has 10 events
Activity #13 starts 2015-07-11 and has 10 events
Activity #14 starts 2015-07-11 and has 10 events
Activity #15 starts 2015-07-11 and has 10 events
Activity #16 starts 2015-07-11 and has 10 events
Activity #17 starts 2015-07-11 and has 10 events
Activity #26 starts 2015-06-19 and has 5 events

Let's take the first of them:

>>> obj = courses.Course.objects.get(pk=12)

..

    Repair from previous incomplete test runs if necessary.

    >>> response = obj.do_update_events()
    >>> response['success']
    True


>>> ses.show(cal.EntriesByController, obj, column_names="when_text state", nosummary=True)
======================== ===========
 When                     State
------------------------ -----------
 Mon 21/03/2016 (11:00)   Suggested
 Mon 04/04/2016 (11:00)   Suggested
 Mon 11/04/2016 (11:00)   Suggested
 Mon 18/04/2016 (11:00)   Suggested
 Mon 25/04/2016 (11:00)   Suggested
 Mon 02/05/2016 (11:00)   Suggested
 Mon 09/05/2016 (11:00)   Suggested
 Mon 23/05/2016 (11:00)   Suggested
 Mon 30/05/2016 (11:00)   Suggested
 Mon 06/06/2016 (11:00)   Suggested
======================== ===========
<BLANKLINE>


We run the :class:`UpdateEvents <lino_xl.lib.cal.mixins.UpdateEvents>`
action a first time and verify that the events remain unchanged (if
the following fails, make sure you've run :cmd:`inv prep` before
running :cmd:`inv test`).

>>> res = obj.do_update_events()
>>> res['success']
True
>>> print(res['info_message'])
Update Events for 012 Rücken (Swimming)...
Generating events between 2015-07-13 and 2020-05-22 (max. 10).
0 row(s) have been updated.
>>> ses.show(cal.EntriesByController, obj, column_names="when_text summary state", nosummary=True)
======================== =================== ===========
 When                     Short description   State
------------------------ ------------------- -----------
 Mon 21/03/2016 (11:00)   012 Hour 1          Suggested
 Mon 04/04/2016 (11:00)   012 Hour 2          Suggested
 Mon 11/04/2016 (11:00)   012 Hour 3          Suggested
 Mon 18/04/2016 (11:00)   012 Hour 4          Suggested
 Mon 25/04/2016 (11:00)   012 Hour 5          Suggested
 Mon 02/05/2016 (11:00)   012 Hour 6          Suggested
 Mon 09/05/2016 (11:00)   012 Hour 7          Suggested
 Mon 23/05/2016 (11:00)   012 Hour 8          Suggested
 Mon 30/05/2016 (11:00)   012 Hour 9          Suggested
 Mon 06/06/2016 (11:00)   012 Hour 10         Suggested
======================== =================== ===========
<BLANKLINE>

We select the event no 4 (2013-12-23, 20140519):

>>> qs = obj.get_existing_auto_events()
>>> e = qs.get(start_date=i2d(20160418))

Yes, the state is "suggested":

>>> print(e.state)
Suggested

Now we move that event to the next available date (the week after in
our case):

>>> response = e.move_next()
>>> response['success']
True
>>> print(response['info_message'])
Move down for Activity #12 012 Hour 4...
Generating events between 2015-07-13 and 2020-05-22 (max. 10).
1 row(s) have been updated.


The state is now "draft":

>>> print(e.state)
Draft

Note that all subsequent events have also been moved to their next
available date.

>>> ses.show(cal.EntriesByController, obj, column_names="when_text summary state", nosummary=True)
======================== =================== ===========
 When                     Short description   State
------------------------ ------------------- -----------
 Mon 21/03/2016 (11:00)   012 Hour 1          Suggested
 Mon 04/04/2016 (11:00)   012 Hour 2          Suggested
 Mon 11/04/2016 (11:00)   012 Hour 3          Suggested
 Mon 25/04/2016 (11:00)   012 Hour 4          Draft
 Mon 02/05/2016 (11:00)   012 Hour 5          Suggested
 Mon 09/05/2016 (11:00)   012 Hour 6          Suggested
 Mon 23/05/2016 (11:00)   012 Hour 7          Suggested
 Mon 30/05/2016 (11:00)   012 Hour 8          Suggested
 Mon 06/06/2016 (11:00)   012 Hour 9          Suggested
 Mon 13/06/2016 (11:00)   012 Hour 10         Suggested
======================== =================== ===========
<BLANKLINE>

The state "Draft" is normal: it indicates that the event has been
manually modified.

Note that 2016-05-16 is a holiday:

>>> cal.Event.objects.filter(start_date=i2d(20160516))
<QuerySet [Event #86 ('Recurring event #12 Pentecost')]>

.. Now for this test, in order to restore original state, we click on
   the "Reset" button:

    >>> e.state = cal.EntryStates.suggested
    >>> e.save()

    and re-run UpdateEvents a last time:

    >>> res = obj.do_update_events()
    >>> res['success']
    True
    >>> ses.show(cal.EntriesByController, obj, column_names="when_text state", nosummary=True)
    ======================== ===========
     When                     State
    ------------------------ -----------
     Mon 21/03/2016 (11:00)   Suggested
     Mon 04/04/2016 (11:00)   Suggested
     Mon 11/04/2016 (11:00)   Suggested
     Mon 18/04/2016 (11:00)   Suggested
     Mon 25/04/2016 (11:00)   Suggested
     Mon 02/05/2016 (11:00)   Suggested
     Mon 09/05/2016 (11:00)   Suggested
     Mon 23/05/2016 (11:00)   Suggested
     Mon 30/05/2016 (11:00)   Suggested
     Mon 06/06/2016 (11:00)   Suggested
    ======================== ===========
    <BLANKLINE>


A sortable virtual field
========================

The :attr:`when_text <lino_xl.lib.cal.Event.when_text>` field of a
calendar entry is sortable despite the fact that it is virtual.

>>> de = rt.models.cal.Events.get_data_elem('when_text')

>>> de.__class__
<class 'lino.core.fields.VirtualField'>
>>> rmu(de.sortable_by)
['start_date', 'start_time']


>>> de.return_type.__class__
<class 'lino.core.fields.DisplayField'>
>>> rmu(de.return_type.sortable_by)
['start_date', 'start_time']


>>> th = rt.models.cal.Events.get_handle()
>>> col = th.get_columns()[0]
>>> col.__class__
<class 'lino.core.elems.DisplayElement'>
>>> col.name
'when_text'
>>> rmu(col.field.sortable_by)
['start_date', 'start_time']

>>> col.sortable
True
