==============
About analysis
==============

This document describes some concepts we use when developing Lino
applications.


The functional specification
============================

The "functional specification" of an application is a document which
describes what an application is expected to do.

Writing this document is the job of the **analyst**.  The analyst
communicates directly with the customer and formulates their
needs. The **salesman** uses this document when discussing with the
customer about the price.  The **developer** uses this document in
order to understand what he is being asked to implement.

A functional spec is important when doing software development in a
team.  In a small team the salesman, the analyst and the developer can
be a single person. But even then it is important to write function
specs for your projects because they are part of your general project
description and your offer to the customer.

For a Lino application, the functional specification should include
the following elements.

- A textual description of your **database structure**, i.e. the list
  of *models* (tables) to be used.  Each model has a list of
  *fields* (properties).  
  
  It is important to choose meaningful names and to agree with your
  customer on the meaning of certain words which will be the
  vocabulary used in your application. 

- Another thing to discuss with your customer during analysis is the
  **menu structure** and the content of the **main page** (dashboard).

- On multi-user applications you also need a description of the
  different **user types**.


The prototype
=============

Lino encourages writing quick prototypes. We often write a prototype
for a project even before issuing a first cost estimation.

It is important to get some fictive data which corresponds more or
less to the reality of your customer. Having an appropriate choice of
examples and original documents will help the developer to get a grasp
and to write demo fixtures.

The technical specs
===================

As soon as the developer has written a prototype, they can start
writing and maintaining "technical specs", i.e. a :doc:`tested
<doctests>` Sphinx document tree which uses the demo database in order
to show its content.

Specs are both a **visualisation of your demo data** (which you might
show to your customer) and a **part of the test suite** of your future
application.

Example of a technical spec: :doc:`/specs/projects/lets1`



End-user documentation
======================


- The **layouts** of detail forms are another thing to discuss with
  your customer during analysis, and therefore they should be part of
  a specification.
