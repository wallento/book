.. doctest docs/specs/voga/sales.rst
.. _voga.specs.sales:

=====================================
The :mod:`lino_voga.lib.sales` plugin
=====================================

The :mod:`lino_voga.lib.sales` plugin extends :mod:`lino_xl.lib.sales`
for usage in :ref:`voga`.

See also :doc:`invoicing`.


About this document
===================

Code examples in this document use the :mod:`lino_book.projects.roger`
demo project:

>>> from lino import startup
>>> startup('lino_book.projects.roger.settings.doctests')
>>> from lino.api.doctest import *
    
>>> dd.plugins.sales
lino_voga.lib.sales (extends_models=['InvoiceItem'])


Here are all our sales invoices:

>>> jnl = rt.models.ledger.Journal.get_by_ref('SLS')
>>> rt.show(sales.InvoicesByJournal, jnl)  #doctest: +ELLIPSIS
===================== ============ ============ =================================== ================= ============== ================
 No.                   Entry date   Due date     Partner                             Total incl. VAT   Subject line   Workflow
--------------------- ------------ ------------ ----------------------------------- ----------------- -------------- ----------------
 24/2015               01/03/2015   30/05/2015   Radermacher Hedi                    20,00                            **Registered**
 23/2015               01/03/2015   31/03/2015   Laschet Laura                       40,00                            **Registered**
 22/2015               01/03/2015   31/03/2015   Evers Eberhart                      48,00                            **Registered**
 21/2015               01/03/2015   01/03/2015   di Rupo Didier                      48,00                            **Registered**
 20/2015               01/03/2015   31/03/2015   Radermacher Guido                   50,00                            **Registered**
 19/2015               01/03/2015   30/05/2015   Jacobs Jacqueline                   48,00                            **Registered**
 18/2015               01/03/2015   30/04/2015   Emonts-Gast Erna                    64,00                            **Registered**
 17/2015               01/02/2015   02/04/2015   Emonts-Gast Erna                    128,00                           **Registered**
 16/2015               01/02/2015   08/02/2015   Meier Marie-Louise                  48,00                            **Registered**
 15/2015               01/02/2015   08/02/2015   Kaivers Karl                        50,00                            **Registered**
 ...
 4/2015                01/01/2015   31/01/2015   Charlier Ulrike                     148,00                           **Registered**
 3/2015                01/01/2015   31/01/2015   Radermacher Guido                   114,00                           **Registered**
 2/2015                01/01/2015   31/01/2015   Jonas Josef                         64,00                            **Registered**
 1/2015                01/01/2015   31/01/2015   Dupont Jean                         98,00                            **Registered**
 63/2014               01/12/2014   31/12/2014   Radermacher Guido                   50,00                            **Registered**
 62/2014               01/12/2014   08/12/2014   Kaivers Karl                        50,00                            **Registered**
 61/2014               01/12/2014   31/12/2014   Charlier Ulrike                     148,00                           **Registered**
 ...
 14/2014               01/04/2014   08/04/2014   Meier Marie-Louise                  20,00                            **Registered**
 13/2014               01/04/2014   01/05/2014   Dobbelstein-Demeulenaere Dorothée   20,00                            **Registered**
 12/2014               01/04/2014   30/06/2014   Engels Edgar                        50,00                            **Registered**
 11/2014               01/04/2014   31/05/2014   Emonts-Gast Erna                    64,00                            **Registered**
 10/2014               01/04/2014   01/05/2014   Dupont Jean                         114,00                           **Registered**
 9/2014                01/03/2014   01/03/2014   di Rupo Didier                      20,00                            **Registered**
 8/2014                01/03/2014   30/05/2014   Engels Edgar                        20,00                            **Registered**
 7/2014                01/03/2014   31/03/2014   Dupont Jean                         50,00                            **Registered**
 6/2014                01/02/2014   02/05/2014   Engels Edgar                        50,00                            **Registered**
 5/2014                01/02/2014   02/04/2014   Emonts-Gast Erna                    64,00                            **Registered**
 4/2014                01/02/2014   03/03/2014   Dupont Jean                         114,00                           **Registered**
 3/2014                01/01/2014   02/03/2014   Emonts-Gast Erna                    114,00                           **Registered**
 2/2014                01/01/2014   01/04/2014   Engels Edgar                        214,00                           **Registered**
 1/2014                01/01/2014   31/01/2014   Dupont Jean                         114,00                           **Registered**
 **Total (87 rows)**                                                                 **6 983,00**
===================== ============ ============ =================================== ================= ============== ================
<BLANKLINE>


The :class:`lino_xl.lib.sales.DueInvoices` table shows a list of
invoices that aren't (completeley) paid.  The following ones are there
obviously due to a payment difference.

>>> rt.show(sales.DueInvoices)
==================== =========== ======== =============== ================= ================ ================
 Due date             Reference   No.      Partner         Total incl. VAT   Balance before   Balance to pay
-------------------- ----------- -------- --------------- ----------------- ---------------- ----------------
 31/03/2015           SLS         23       Laschet Laura   40,00                              0,60
 **Total (1 rows)**               **23**                   **40,00**                          **0,60**
==================== =========== ======== =============== ================= ================ ================
<BLANKLINE>


Printing invoices
=================

We take a sales invoice, clear the cache, ask Lino to print it and 
check whether we get the expected response.

>>> import lxml.usedoctest
>>> ses = settings.SITE.login("robin")
>>> dd.translation.activate('en')
>>> obj = sales.VatProductInvoice.objects.all()[0]
>>> obj.clear_cache()
>>> d = ses.run(obj.do_print)
... #doctest: +ELLIPSIS
appy.pod render .../sales/config/sales/VatProductInvoice/Default.odt -> .../media/cache/appypdf/sales.VatProductInvoice-125.pdf

>>> d['success']
True

>>> print(d['message'])
Your printable document (<a href="/media/cache/appypdf/sales.VatProductInvoice-125.pdf">sales.VatProductInvoice-125.pdf</a>) should now open in a new browser window. If it doesn't, please ask your system administrator.

Your printable document (filename sales.VatProductInvoice-125.pdf) should now open in a new browser window. If it doesn't, please consult <a href="http://www.lino-framework.org/help/print.html" target="_blank">the documentation</a> or ask your system administrator.

Note that this test should fail if you run the test suite without a 
LibreOffice server running.




>>> rt.show(invoicing.SalesRules)
==================== =================== ============
 Partner              Invoicing address   Paper type
-------------------- ------------------- ------------
 Arens Annette
 Faymonville Luc      Engels Edgar
 Radermacher Alfons   Emonts-Gast Erna
 Martelaer Mark       Dupont Jean
==================== =================== ============
<BLANKLINE>
