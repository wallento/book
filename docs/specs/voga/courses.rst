.. doctest docs/specs/voga/courses.rst
.. _voga.specs.courses:

=======================
Activities in Lino Voga
=======================

This document specifies how the :mod:`lino_xl.lib.courses` plugin is
being used in :ref:`voga`.

.. contents::
  :local:

Examples in this document use the :mod:`lino_book.projects.roger` demo
project.

>>> from lino import startup
>>> startup('lino_book.projects.roger.settings.doctests')
>>> from lino.api.doctest import *



Implementation
==============

>>> dd.plugins.courses
lino_voga.lib.roger.courses (extends_models=['Pupil', 'Enrolment', 'Line'])

>>> dd.plugins.courses.__class__.__bases__
(<class 'lino_voga.lib.courses.Plugin'>,)


Course areas
============

The :class:`CourseAreas` choicelist in :ref:`voga` defines the
following areas:

>>> rt.show(courses.CourseAreas)
======= ========== ========== ==================
 value   name       text       Table
------- ---------- ---------- ------------------
 C       default    Courses    courses.Courses
 H       hikes      Hikes      courses.Hikes
 J       journeys   Journeys   courses.Journeys
======= ========== ========== ==================
<BLANKLINE>

    

Pupils and teachers
===================

Lino Voga adds specific models for teachers and pupils.
A teacher is a person with a `teacher_type`.
A pupil is a person with a `pupil_type`.

The :mod:`lino_xl.lib.courses` plugin has two settings
:attr:`teacher_model <lino_xl.lib.courses.Plugin.teacher_model>` and
:attr:`pupil_model <lino_xl.lib.courses.Plugin.pupil_model>`:


>>> dd.plugins.courses.teacher_model
<class 'lino_voga.lib.courses.models.Teacher'>

>>> dd.plugins.courses.pupil_model
<class 'lino_voga.lib.roger.courses.models.Pupil'>


The demo database has 35 pupils and 9 teachers:

>>> rt.models.courses.Pupil.objects.count()
35
>>> rt.models.courses.Teacher.objects.count()
9


>>> rt.show('courses.Teachers')
==================== =============================== =================
 Name                 Address                         Instructor Type
-------------------- ------------------------------- -----------------
 Hans Altenberg       Aachener Straße, 4700 Eupen
 Charlotte Collard    Auf dem Spitzberg, 4700 Eupen
 Daniel Emonts        Bellmerin, 4700 Eupen
 Germaine Gernegroß   Buchenweg, 4700 Eupen
 Josef Jonas          Gülcherstraße, 4700 Eupen
 Marc Malmendier      Heidhöhe, 4700 Eupen
 Edgard Radermacher   4730 Raeren
 Tom Thess            4700 Eupen
 David da Vinci       4730 Raeren
==================== =============================== =================
<BLANKLINE>


>>> ses = rt.login('robin')

>>> ses.show(rt.models.courses.PupilTypes)
==== =========== ============= ================== ==================
 ID   Reference   Designation   Designation (de)   Designation (fr)
---- ----------- ------------- ------------------ ------------------
 1    M           Member        Mitglied           Member
 2    H           Helper        Helfer             Helper
 3    N           Non-member    Nicht-Mitglied     Non-member
==== =========== ============= ================== ==================
<BLANKLINE>

>>> ses.show(rt.models.courses.TeacherTypes)
==== =========== ================== ======================= ======================
 ID   Reference   Designation        Designation (de)        Designation (fr)
---- ----------- ------------------ ----------------------- ----------------------
 1    S           Independant        Selbstständig           Indépendant
 2    EP          Voluntary (flat)   Ehrenamtlich pauschal   Volontaire (forfait)
 3    ER          Voluntary (real)   Ehrenamtlich real       Volontaire (réel)
 4    LBA         LEA                LBA                     ALE
==== =========== ================== ======================= ======================
<BLANKLINE>


See also :doc:`pupils`.


Enrolments
==========

>>> rt.show('courses.EnrolmentStates')
======= =========== =========== =============
 value   name        text        Button text
------- ----------- ----------- -------------
 10      requested   Requested
 11      trying      Trying
 20      confirmed   Confirmed
 30      cancelled   Cancelled
======= =========== =========== =============
<BLANKLINE>


>>> rt.show('courses.EnrolmentStates', language="de")
====== =========== =========== =============
 Wert   name        Text        Button text
------ ----------- ----------- -------------
 10     requested   Angefragt
 11     trying      Test
 20     confirmed   Bestätigt
 30     cancelled   Storniert
====== =========== =========== =============
<BLANKLINE>



The fee of a course
===================

Per course and per enrolment we get a new field :attr:`fee`.

Number of places
================

The :attr:`max_places<lino_xl.lib.courses.models.Course.max_places>`
(:ddref:`courses.Course.max_places`) field of a *course* contains the
number of available places.

It is a simple integer value and expresses an *absolute* upper limit
which cannot be bypassed. Lino will refuse to confirm an enrolment if
this limit is reached. Here is a user statement about this:

    Also im Prinzip nehmen wir bei den Computerkursen maximal 10 Leute
    an. Da wir aber überall über 12 Geräte verfügen, können wir immer
    im Bedarfsfall um 2 Personen aufstocken. Also bei PC-Kursen setzen 
    wir das Maximum immer auf 12. Als Regel gilt dann, dass wir immer nur
    10 annehmen, aber falls unbedingt erforderlich auf 12 gehen
    können.

Every *enrolment* has a field
:attr:`places<lino_xl.lib.courses.models.Enrolment.places>`
(:ddref:`courses.Enrolment.places`) which expresses how many places
this enrolment takes. This is usually 1, but for certain types of
courses, e.g. bus travels, it can happen that one enrolment is for two
or more persons.


Waiting things
==============


The following is waiting for :ticket:`526` before it can work:

>>> # demo_get('robin', 'choices/courses/Courses/city', 'bla', 0)


CoursesByLine
=============

There are two Yoga courses:

>>> obj = courses.Line.objects.get(pk=10)
>>> obj
Line #10 ('Yoga')
        
>>> rt.show(rt.models.courses.CoursesByLine, obj)
==================================== ============== ================== ============= ====================
 Description                          When           Room               Times         Instructor
------------------------------------ -------------- ------------------ ------------- --------------------
 *024C Yoga* / *Marc Malmendier*      Every Monday   Conferences room   18:00-19:30   Marc Malmendier
 *025C Yoga* / *Edgard Radermacher*   Every Friday   Conferences room   19:00-20:30   Edgard Radermacher
==================================== ============== ================== ============= ====================
<BLANKLINE>


>>> ContentType = rt.models.contenttypes.ContentType
>>> json_fields = 'count rows title success no_data_text param_values'
>>> kw = dict(fmt='json', limit=10, start=0)
>>> mt = ContentType.objects.get_for_model(courses.Line).pk
>>> demo_get('robin',
...          'api/courses/CoursesByLine', json_fields, 3, 
...          mt=mt, mk=obj.pk, **kw)


Status report
=============

The status report gives an overview of active courses.

(TODO: demo fixture should avoid negative free places)

>>> rt.show(rt.models.courses.StatusReport)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
~~~~~~~~
Journeys
~~~~~~~~
<BLANKLINE>
====================================== ======================= ======= ================== =========== ============= =========== ========
 Description                            When                    Times   Available places   Confirmed   Free places   Requested   Trying
-------------------------------------- ----------------------- ------- ------------------ ----------- ------------- ----------- --------
 *001 Greece 2014* / *Hans Altenberg*   14/08/2014-20/08/2014                              3                         0           0
 **Total (1 rows)**                                                     **0**              **3**       **0**         **0**       **0**
====================================== ======================= ======= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~~~~
Computer
~~~~~~~~
<BLANKLINE>
============================================================ ================= ============= ================== =========== ============= =========== ========
 Description                                                  When              Times         Available places   Confirmed   Free places   Requested   Trying
------------------------------------------------------------ ----------------- ------------- ------------------ ----------- ------------- ----------- --------
 *003 comp (First Steps)* / *Daniel Emonts*                   Every Monday      13:30-15:00   3                  2           1             0           0
 *004 comp (First Steps)* / *Germaine Gernegroß*              Every Wednesday   17:30-19:00   3                  3           0             1           0
 *005 comp (First Steps)* / *Josef Jonas*                     Every Friday      13:30-15:00   3                  2           1             0           0
 *006C WWW (Internet for beginners)* / *Marc Malmendier*      Every Monday      13:30-15:00   4                  2           2             1           0
 *007C WWW (Internet for beginners)* / *Edgard Radermacher*   Every Wednesday   17:30-19:00   4                  2           2             0           0
 *008C WWW (Internet for beginners)* / *Tom Thess*            Every Friday      13:30-15:00   4                  3           1             0           0
 **Total (6 rows)**                                                                           **21**             **14**      **7**         **2**       **0**
============================================================ ================= ============= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~
Sport
~~~~~
<BLANKLINE>
========================================================= ================= ============= ================== =========== ============= =========== ========
 Description                                               When              Times         Available places   Confirmed   Free places   Requested   Trying
--------------------------------------------------------- ----------------- ------------- ------------------ ----------- ------------- ----------- --------
 *009C BT (Belly dancing)* / *David da Vinci*              Every Wednesday   19:00-20:00   10                 3           7             0           0
 *010C FG (Functional gymnastics)* / *Hans Altenberg*      Every Monday      11:00-12:00   5                  2           3             0           0
 *011C FG (Functional gymnastics)* / *Charlotte Collard*   Every Monday      13:30-14:30   5                  2           3             1           0
 *012 Rücken (Swimming)* / *Daniel Emonts*                 Every Monday      11:00-12:00   20                 3           17            0           0
 *013 Rücken (Swimming)* / *Germaine Gernegroß*            Every Monday      13:30-14:30   20                 3           17            1           0
 *014 Rücken (Swimming)* / *Josef Jonas*                   Every Tuesday     11:00-12:00   20                 3           17            0           0
 *015 Rücken (Swimming)* / *Marc Malmendier*               Every Tuesday     13:30-14:30   20                 0           20            0           0
 *016 Rücken (Swimming)* / *Edgard Radermacher*            Every Thursday    11:00-12:00   20                 3           17            0           0
 *017 Rücken (Swimming)* / *Tom Thess*                     Every Thursday    13:30-14:30   20                 3           17            1           0
 *018 SV (Self-defence)* / *David da Vinci*                Every Friday      18:00-19:00   12                 2           10            0           0
 *019 SV (Self-defence)* / *Hans Altenberg*                Every Friday      19:00-20:00   12                 3           9             0           0
 **Total (11 rows)**                                                                       **164**            **27**      **137**       **3**       **0**
========================================================= ================= ============= ================== =========== ============= =========== ========
<BLANKLINE>
~~~~~~~~~~
Meditation
~~~~~~~~~~
<BLANKLINE>
============================================================== ============== ============= ================== =========== ============= =========== ========
 Description                                                    When           Times         Available places   Confirmed   Free places   Requested   Trying
-------------------------------------------------------------- -------------- ------------- ------------------ ----------- ------------- ----------- --------
 *020C GLQ (GuoLin-Qigong)* / *Charlotte Collard*               Every Monday   18:00-19:30                      0                         0           0
 *021C GLQ (GuoLin-Qigong)* / *Daniel Emonts*                   Every Friday   19:00-20:30                      2                         1           0
 *022C MED (Finding your inner peace)* / *Germaine Gernegroß*   Every Monday   18:00-19:30   30                 2           28            0           0
 *023C MED (Finding your inner peace)* / *Josef Jonas*          Every Friday   19:00-20:30   30                 3           27            0           0
 *024C Yoga* / *Marc Malmendier*                                Every Monday   18:00-19:30   20                 2           18            0           0
 *025C Yoga* / *Edgard Radermacher*                             Every Friday   19:00-20:30   20                 2           18            1           0
 **Total (6 rows)**                                                                          **100**            **11**      **91**        **2**       **0**
============================================================== ============== ============= ================== =========== ============= =========== ========
<BLANKLINE>






Free places
===========

Note the *free places* field which is not always trivial.  Basicially
it contains `max_places - number of confirmed enrolments`.  But it
also looks at the `end_date` of these enrolments.

List of courses which have a confirmed ended enrolment and a limited
number of places:

>>> qs = courses.Enrolment.objects.filter(end_date__lt=dd.today(),
...     state=courses.EnrolmentStates.confirmed, course__max_places__isnull=False)
>>> for obj in qs:
...     print("{} {} {} {}".format(
...         obj.course.id, obj.course.max_places,
...         obj.course.confirmed,
...         obj.course.get_free_places(dd.today())))
9 10 3 7
19 12 3 9
5 3 2 1
22 30 2 28
25 20 2 18
10 5 2 3
8 4 3 1
3 3 2 1
23 30 3 27
7 4 2 2
18 12 2 10
6 4 2 2
24 20 2 18

In course #5 there are **3** confirmed enrolments, but (on 2015-05-22)
only **2** of them are actually taking a place because one has already
ended.

>>> obj = courses.Course.objects.get(pk=5)
>>> rt.show(courses.EnrolmentsByCourse, obj, column_names="pupil start_date end_date places state")
======================================== ============ ============ ============= ===========
 Participant                              Start date   End date     Places used   State
---------------------------------------- ------------ ------------ ------------- -----------
 Didier di Rupo (MS)                                                1             Confirmed
 Dorothée Dobbelstein-Demeulenaere (ME)                22/04/2014   1             Confirmed
 Josefine Leffin (MEL)                    02/04/2014                1             Confirmed
 **Total (3 rows)**                                                 **3**
======================================== ============ ============ ============= ===========
<BLANKLINE>

>>> print(obj.max_places)
3
>>> print(obj.get_free_places())
1

Above situation is because we are looking at it on 20150522:

>>> print(dd.today())
2015-05-22

The same request on earlier dates yields different results:

On 20140403 nobody has left yet, all 3 places are taken and therefore
no place is free:

>>> print(obj.get_free_places(i2d(20140403)))
0

On 20140422 is Dorothée's last day, so her place is not yet free:

>>> print(obj.get_free_places(i2d(20140422)))
0

But the next day she is gone and her place available again:

>>> print(obj.get_free_places(i2d(20140423)))
1



Filtering pupils
================

>>> print(rt.models.courses.Pupils.params_layout.main)
course partner_list #aged_from #aged_to gender show_members show_lfv show_ckk show_raviva

There are 36 pupils (21 men and 15 women) in our database:

>>> json_fields = 'count rows title success no_data_text param_values'
>>> kwargs = dict(fmt='json', limit=10, start=0)
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 36, **kwargs)

>>> kwargs.update(pv=['', '', 'M', '', '', '', ''])
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 21, **kwargs)

>>> kwargs.update(pv=['', '', 'F', '', '', '', ''])
>>> demo_get('robin', 'api/courses/Pupils', json_fields, 15, **kwargs)


>>> json_fields = 'navinfo disable_delete data id title'
>>> kwargs = dict(fmt='json', an='detail')
>>> demo_get('robin', 'api/courses/Lines/2', json_fields, **kwargs)



.. _voga.presence_sheet:

Presence sheet
==============

The **presence sheet** of a course is a printable document where
course instructors can manually record the presences of the
participants for every event.


