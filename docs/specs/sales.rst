.. doctest docs/specs/sales.rst
.. _cosi.specs.sales:

================
Product invoices
================

A **product invoice** is an invoice whose rows usually refer to a
*product* (which indirectly maps to a ledger account according to
configurable rules).  This is in contrast to *account invoices* whose
rows directly point to ledger accounts and don't need any products.

Snippets in this document are tested on the
:mod:`lino_book.projects.pierre` demo project.

>>> from lino import startup
>>> startup('lino_book.projects.pierre.settings.doctests')
>>> from lino.api.doctest import *
>>> ses = rt.login('robin')



The plugin
==========

Lino implements product invoices in the :mod:`lino_xl.lib.sales`
plugin.  The internal codename "sales" is for historical reasons, you
might generate product invoices for other trade types as well.

The plugin needs and automatically installs the
:mod:`lino_xl.lib.products` plugin.

It also needs and installs :mod:`lino_xl.lib.vat` (and not
:mod:`lino_xl.lib.vatless`).  Which means that if you want product
invoices, you cannot *not* also install the VAT framework.  If the
site owner is not subject to VAT, you can hide the VAT fields and
define a VAT rate of 0 for everything.

>>> dd.plugins.sales.needs_plugins
['lino_xl.lib.products', 'lino_xl.lib.vat']

This plugin is needed and extended by :mod:`lino_xl.lib.invoicing`
which adds automatic generation of such product invoices.

>>> dd.plugins.invoicing.needs_plugins
['lino_xl.lib.sales']


Product invoices
================

A **product invoice** is a legal document which describes that
something (the invoice items) has been sold to a given business
partner (called the customer).  The partner can be either a private
person or an organization.

.. class:: VatProductInvoice

    The Django model representing a *product invoice*.

    Inherits from :class:`lino_xl.lib.ledger.Voucher`.

    Virtual fields:

    .. attribute:: balance_before

       The balance of previous payments or debts. On a printed
       invoice, this amount should be mentioned and added to the
       invoice's amount in order to get the total amount to pay.

    .. attribute:: balance_to_pay

       The balance of all movements matching this invoice.

    Methods:

    .. method:: get_print_items(self, ar):
                
        For usage in an appy template::

            do text
            from table(obj.get_print_items(ar))

           
.. class:: InvoiceItem
           
    The Django model representing an *item* of a *product invoice*.

    
.. class:: InvoiceDetail

    The Lino layout representing the detail view of a *product invoice*.
           
.. class:: Invoices
           
.. class:: InvoicesByJournal
    Shows all invoices of a given journal (whose `voucher_type` must be
    :class:`VatProductInvoice`)
           
.. class:: DueInvoices
           
    Shows all due product invoices.

           
.. class:: ProductDocItem

    Mixin for voucher items which potentially refer to a product.

    .. attribute:: product

       The product that is being sold or purchased.
       
    .. attribute:: description

       A multi-line rich text to be printed in the resulting printable
       document.

    .. attribute:: discount

           
.. class:: ItemsByInvoicePrint

    The table used to render items in a printable document.

    .. attribute:: description_print

        TODO: write more about it.

.. class:: ItemsByInvoicePrintNoQtyColumn
           
    Alternative column layout to be used when printing an invoice.

.. class:: SalesDocument

    Common base class for :class:`lino_xl.lib.orders.Order` and
    :class:`VatProductInvoice`.
           
    Inherits from :class:`lino_xl.lib.vat.mixins.VatDocument` and
    :class:`ino_xl.lib.excerpts.mixinsCertifiable`.

    Subclasses must either add themselves a :attr:`date` field (as
    does :class:`Order <lino_xl.lib.orders.Order>`) or inherit it from
    Voucher (as does :class:`VatProductInvoice`).

    Note that this class sets :attr:`edit_totals
    <lino_xl.lib.vat.VatDocument.edit_totals>` to False.

    .. attribute:: print_items_table = None

        The table (column layout) to use in the printed document.

        :class:`ItemsByInvoicePrint`
        :class:`ItemsByInvoicePrintNoQtyColumn`


Paper types
===========

.. class:: PaperType

    Describes a paper type (document template) to be used when
    printing an invoice.

    A sample use case is to differentiate between invoices to get
    printed either on a company letterpaper for expedition via paper
    mail or into an email-friendly pdf file.

    Inherits from :class:`lino.utils.mldbc.mixins.BabelNamed`.


    .. attribute:: templates_group = 'sales/VatProductInvoice'

        A class attribute.

    .. attribute:: template
           
    
    

Trade types
===========

The plugin updates your :attr:`lino_xl.lib.ledger.TradeTypes.sales`,
causing two additional database fields to be injected to
:class:`lino_xl.lib.products.Product`.

The first injected field is the sales price of a product:

>>> translation.activate('en')
>>> print(ledger.TradeTypes.sales.price_field_name)
sales_price
>>> print(ledger.TradeTypes.sales.price_field_label)
Sales price
>>> products.Product._meta.get_field('sales_price')
<lino.core.fields.PriceField: sales_price>

The other injected field is the sales base account of a product:

>>> print(ledger.TradeTypes.sales.base_account_field_name)
sales_account
>>> print(ledger.TradeTypes.sales.base_account_field_label)
Sales account
>>> products.Product._meta.get_field('sales_account')
<django.db.models.fields.related.ForeignKey: sales_account>



The invoicing address of a partner
==================================

The plugin also injects a field :attr:`invoice_recipient
<lino.modlib.contacts.models.Partner.invoice_recipient>` to the
:class:`contacts.Partner <lino.modlib.contacts.models.Partner>` model:

.. attribute:: lino.modlib.contacts.models.Partner.invoice_recipient

  The recipient of invoices (invoicing address).




The sales journal
=================

>>> rt.show('ledger.Journals', column_names="ref name trade_type")
=========== ========================= =============================== =====================
 Reference   Designation               Designation (en)                Trade type
----------- ------------------------- ------------------------------- ---------------------
 SLS         Factures vente            Sales invoices                  Sales
 SLC         Sales credit notes        Sales credit notes              Sales
 PRC         Factures achat            Purchase invoices               Purchases
 PMO         Bestbank Payment Orders   Bestbank Payment Orders         Bank payment orders
 CSH         Caisse                    Cash
 BNK         Bestbank                  Bestbank
 MSC         Opérations diverses       Miscellaneous Journal Entries
 VAT         Déclarations TVA          VAT declarations                Taxes
=========== ========================= =============================== =====================
<BLANKLINE>


>>> jnl = rt.models.ledger.Journal.get_by_ref("SLS")
>>> rt.show('sales.InvoicesByJournal', jnl) 
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
===================== ============ ============ =================================== ================= ============== ================
 No.                   Entry date   Due date     Partner                             Total incl. VAT   Subject line   Workflow
--------------------- ------------ ------------ ----------------------------------- ----------------- -------------- ----------------
 15/2017               12/03/2017   18/03/2017   da Vinci David                      770,00                           **Registered**
 14/2017               11/03/2017   17/03/2017   da Vinci David                      465,96                           **Registered**
 13/2017               10/03/2017   09/03/2017   di Rupo Didier                      639,92                           **Registered**
 12/2017               09/03/2017   07/04/2017   Radermacher Jean                    3 599,71                         **Registered**
 11/2017               08/03/2017   31/03/2017   Radermacher Inge                    726,00                           **Registered**
 10/2017               07/03/2017   04/06/2017   Radermacher Hedi                    525,00                           **Registered**
 9/2017                14/02/2017   14/04/2017   Radermacher Hans                    951,82                           **Registered**
 8/2017                13/02/2017   14/03/2017   Radermacher Guido                   2 349,81                         **Registered**
 7/2017                12/02/2017   21/02/2017   Radermacher Fritz                   1 599,92                         **Registered**
 6/2017                11/02/2017   20/02/2017   Radermacher Fritz                   990,00                           **Registered**
 5/2017                10/02/2017   16/02/2017   Radermacher Edgard                  338,68                           **Registered**
 4/2017                09/02/2017   08/02/2017   Radermacher Daniela                 1 199,85                         **Registered**
 3/2017                08/02/2017   09/03/2017   Radermacher Christian               3 319,78                         **Registered**
 2/2017                07/02/2017   28/02/2017   Radermacher Berta                   535,00                           **Registered**
 1/2017                07/01/2017   06/04/2017   Radermacher Alfons                  280,00                           **Registered**
 57/2016               10/12/2016   07/02/2017   Emonts-Gast Erna                    822,57                           **Registered**
 56/2016               09/12/2016   07/01/2017   Emontspool Erwin                    2 039,82                         **Registered**
 ...
 12/2016               08/04/2016   07/05/2016   Moulin Rouge                        951,82                           **Registered**
 11/2016               07/04/2016   16/04/2016   Reinhards Baumschule                2 349,81                         **Registered**
 10/2016               07/03/2016   13/03/2016   Bernd Brechts Bücherladen           1 599,92                         **Registered**
 9/2016                10/02/2016   09/02/2016   Hans Flott & Co                     1 197,90                         **Registered**
 8/2016                09/02/2016   09/03/2016   Van Achter NV                       279,90                           **Registered**
 7/2016                08/02/2016   29/02/2016   Donderweer BV                       1 199,85                         **Registered**
 6/2016                07/02/2016   06/05/2016   Garage Mergelsberg                  4 016,93                         **Registered**
 5/2016                11/01/2016   10/03/2016   Bäckerei Schmitz                    535,00                           **Registered**
 4/2016                10/01/2016   08/02/2016   Bäckerei Mießen                     280,00                           **Registered**
 3/2016                09/01/2016   18/01/2016   Bäckerei Ausdemwald                 679,81                           **Registered**
 2/2016                08/01/2016   14/01/2016   Rumma & Ko OÜ                       2 039,82                         **Registered**
 1/2016                07/01/2016   06/01/2016   Bestbank                            2 999,85                         **Registered**
 **Total (72 rows)**                                                                 **98 409,82**
===================== ============ ============ =================================== ================= ============== ================
<BLANKLINE>


>>> mt = contenttypes.ContentType.objects.get_for_model(sales.VatProductInvoice).id
>>> obj = sales.VatProductInvoice.objects.get(journal__ref="SLS", number=20)

>>> url = '/api/sales/InvoicesByJournal/{0}'.format(obj.id)
>>> url += '?mt={0}&mk={1}&an=detail&fmt=json'.format(mt, obj.journal.id)
>>> test_client.force_login(rt.login('robin').user)
>>> res = test_client.get(url, REMOTE_USER='robin')
>>> # res.content
>>> r = check_json_result(res, "navinfo data disable_delete id title")
>>> print(r['title'])
Sales invoices (SLS) » SLS 20/2016


IllegalText: The <text:section> element does not allow text
===========================================================

The following reproduces a situation which caused above error
until :blogref:`20151111`. 

TODO: it is currently disabled for different reasons: leaves dangling
temporary directories, does not reproduce the problem (probably
because we must clear the cache).

>> obj = rt.models.sales.VatProductInvoice.objects.all()[0]
>> obj
VatProductInvoice #1 ('SLS#1')
>> from lino.modlib.appypod.appy_renderer import AppyRenderer
>> tplfile = rt.find_config_file('sales/VatProductInvoice/Default.odt')
>> context = dict()
>> outfile = "tmp.odt"
>> renderer = AppyRenderer(ses, tplfile, context, outfile)
>> ar = rt.models.sales.ItemsByInvoicePrint.request(obj)
>> print(renderer.insert_table(ar))  #doctest: +ELLIPSIS
<table:table ...</table:table-rows></table:table>


>> item = obj.items.all()[0]
>> item.description = """
... <p>intro:</p><ol><li>first</li><li>second</li></ol>
... <p></p>
... """
>> item.save()
>> print(renderer.insert_table(ar))  #doctest: +ELLIPSIS
Traceback (most recent call last):
...
IllegalText: The <text:section> element does not allow text


The language of an invoice
==========================

The language of an invoice not necessary that of the user who enters
the invoice. It is either the partner's :attr:`language
<lino.modlib.contacts.models.Partner.language>` or (if this is empty)
the Site's :meth:`get_default_language
<lino.core.site.Site.get_default_language>`.

