.. doctest docs/specs/ledger.rst
.. _xl.specs.ledger:
.. _cosi.specs.ledger:
.. _cosi.tested.ledger:

==============
General Ledger
==============

.. currentmodule:: lino_xl.lib.ledger
                   
The :mod:`lino_xl.lib.ledger` plugin adds basic notions for
accounting: accounts, journals, vouchers and movements.
       
Table of contents:

.. contents::
   :depth: 1
   :local:

Examples in this document use the :mod:`lino_book.projects.pierre`
demo project.

>>> from lino import startup
>>> startup('lino_book.projects.pierre.settings.demo')
>>> from lino.api.doctest import *
>>> ses = rt.login("robin")
>>> translation.activate('en')
      

Overview
========

A **ledger** is a book in which the monetary transactions of a
business are posted in the form of debits and credits (from `1
<http://www.thefreedictionary.com/ledger>`__).

In Lino, the ledger is implemented by three database models:

- A **movement** is an atomic "transfer" of a given *amount* of money
  from (or to) a given *account* on a given date.  It is just a
  *conceptual* transfer, not a cash or bank transfer.

  Moving money *from* (out of) an account is called "to debit", moving
  money *to* an account is called "to credit".

- Movements are never created individually but by registering a
  **voucher**.  Examples of *vouchers* include invoices, bank
  statements, or payment orders.
  
  A *voucher* is any document which serves as legal proof for a
  **ledger transaction**.  A ledger transaction consists of *at least
  two* movements, and the sum of *debited* money in these movements
  must equal the sum of *credited* money.

  Vouchers are stored in the database using some subclass of the
  :class:`Voucher` model. Note that the voucher model is never being
  used directly.

- When a voucher is registered, it receives a sequence number in a
  :class:`Journal`.  A journal is a series of vouchers, numbered
  sequentially and in chronological order.

There are some secondary models and choicelists:  

- Each ledger movement happens in a given **fiscal year**.
  MatchRule, LedgerInfo
  
And then there are many subtle ways for looking at this data.

- :class:`GeneralAccountsBalance`, :class:`CustomerAccountsBalance` and
  :class:`SupplierAccountsBalance`

- :class:`Debtors` and :class:`Creditors` are tables with one row for
  each partner who has a positive balance (either debit or credit).
  Accessible via :menuselection:`Reports --> Ledger --> Debtors` and
  :menuselection:`Reports --> Ledger --> Creditors`

Accounts
========

.. class:: Account

    An **account** is the most abstract representation for "something
    where you can place money and retrieve it later".

    An account always has a given balance which can be negative or
    positive.

    In applications which use the :mod:`ledger <lino_xl.lib.ledger>`
    plugin, accounts are used as the target of ledger movements.


    .. attribute:: name

        The multilingual designation of this account, as the users see
        it.

    .. attribute:: ref

        An optional unique name which can be used to reference a given
        account.

    .. attribute:: type

        The *account type* of this account.  This points to an item of
        :class:`CommonAccounts`.
    
    .. attribute:: needs_partner

        Whether bookings to this account need a partner specified.

        For payment orders this causes the contra entry of financial
        documents to be detailed or not (i.e. one contra entry for
        every item or a single contra entry per voucher.

    .. attribute:: default_amount

        The default amount to book in bank statements or journal
        entries when this account has been selected manually. The
        default booking direction is that of the :attr:`type`.
           
    .. attribute:: purchases_allowed
    .. attribute:: sales_allowed
    .. attribute:: wages_allowed
    .. attribute:: FOO_allowed

        These checkboxes indicate whether this account can be used on
        an item of a purchases (or sales or wages or FOO)
        invoice. There is one such checkbox for every trade type
        (:class:`TradeTypes <lino_xl.lib.ledger.TradeTypes>`).  They
        exist only when the :mod:`ledger <lino_xl.lib.ledger>` plugin
        is installed as well.  See also the
        :meth:`get_allowed_accounts
        <lino_xl.lib.ledger.Journal.get_allowed_accounts>` method.

    .. attribute:: needs_ana
                   
        Whether transactions on this account require the user to also
        specify an analytic account.

        This file exists only when :mod:`lino_xl.lib.ana` is
        installed as well.
        
    .. attribute:: ana_account
           
        Which analytic account to suggest for transactions on this
        account.

        This file exists only when :mod:`lino_xl.lib.ana` is
        installed as well.
        
    .. attribute:: sheet_item

        Pointer to the item of the balance sheet or income statement
        that will report the movements of this account.

        This file is a dummy field when :mod:`lino_xl.lib.sheets` is
        not installed.



Common accounts
===============

The `accounts` plugin defines a choicelist of **common accounts**
which are used to reference the database object for certain accounts
which have a special meaning.

.. class:: CommonAccounts

    The global list of common accounts.

    This is a :class:`lino.core.choicelists.ChoiceList`.
    Every item is an instance of :class:`CommonAccount`.

.. class:: CommonAccount
           
    The base class for items of ::class:`CommonAccounts`.
    It defines two additional attributes:

    .. attribute:: clearable
    .. attribute:: needs_partner



Here is the standard list of common accounts in a :ref:`cosi`
application:

>>> rt.show(ledger.CommonAccounts, language="en")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
======= ========================= ========================= =========== ================================
 value   name                      text                      Clearable   Account
------- ------------------------- ------------------------- ----------- --------------------------------
 1000    net_income_loss           Net income (loss)         Yes         (1000) Net income (loss)
 4000    customers                 Customers                 Yes         (4000) Customers
 4300    pending_po                Pending Payment Orders    Yes         (4300) Pending Payment Orders
 4400    suppliers                 Suppliers                 Yes         (4400) Suppliers
 4500    employees                 Employees                 Yes         (4500) Employees
 4600    tax_offices               Tax Offices               Yes         (4600) Tax Offices
 4510    vat_due                   VAT due                   No          (4510) VAT due
 4511    vat_returnable            VAT returnable            No          (4511) VAT returnable
 4512    vat_deductible            VAT deductible            No          (4512) VAT deductible
 4513    due_taxes                 VAT declared              No          (4513) VAT declared
 4900    waiting                   Waiting account           Yes         (4900) Waiting account
 5500    best_bank                 BestBank                  No          (5500) BestBank
 5700    cash                      Cash                      No          (5700) Cash
 6040    purchase_of_goods         Purchase of goods         No          (6040) Purchase of goods
 6010    purchase_of_services      Purchase of services      No          (6010) Purchase of services
 6020    purchase_of_investments   Purchase of investments   No          (6020) Purchase of investments
 6300    wages                     Wages                     No          (6300) Wages
 6900    net_income                Net income                No          (6900) Net income
 7000    sales                     Sales                     No          (7000) Sales
 7900    net_loss                  Net loss                  No          (7900) Net loss
======= ========================= ========================= =========== ================================
<BLANKLINE>

Lino applications can add specific items to that list or potentially
redefine it completely


Debit and credit
================
        
The balance of an account
=========================

The **balance** of an account is the amount of money in that account.

.. data:: DEBIT
.. data:: CREDIT

An account balance is either Debit or Credit.  We represent this
internally as the boolean values `True` and `False`, but define two
names :data:`DEBIT` and :data:`CREDIT` for them:

>>> from lino_xl.lib.ledger.utils import DEBIT, CREDIT
>>> DEBIT
False
>>> CREDIT
True

.. class:: Balance
           
    Light-weight object to represent a balance, i.e. an amount
    together with its booking direction (debit or credit).

    Attributes:

    .. attribute:: d

        The amount of this balance when it is debiting, otherwise zero.

    .. attribute:: c

        The amount of this balance when it is crediting, otherwise zero.

       
A negative value on one side of the balance is automatically moved to
the other side.

>>> from lino_xl.lib.ledger.utils import Balance
>>> Balance(10, -2)
Balance(12,0)



Database fields
===============

.. class:: DebitOrCreditField

    A field that stores the "direction" of a movement, i.e. either
    :data:`DEBIT` or :data:`CREDIT`.

          
.. class:: DebitOrCreditStoreField

    Uused as `lino_atomizer_class` for :class:`DebitOrCreditField`.


Movements
=========


.. class:: Movement

    Represents an accounting movement in the ledger.  See Overview_.

    .. attribute:: value_date

        The date at which this movement is to be entered into the
        ledger.  This is usually the voucher's :attr:`entry_date
        <lino_xl.lib.ledger.models.Voucher.entry_date>`, except
        e.g. for bank statements where each item can have its own
        value date.

    .. attribute:: voucher

        Pointer to the :class:`Voucher` who caused this movement.

    .. attribute:: partner

        Pointer to the partner involved in this movement. This may be
        blank.

    .. attribute:: seqno

        Sequential number within a voucher.

    .. attribute:: account

        Pointer to the :class:`Account` that is being moved by this movement.

    .. attribute:: debit
                   
        Virtual field showing :attr:`amount` if :attr:`dc` is DEBIT.
                   
    .. attribute:: credit
                   
        Virtual field showing :attr:`amount` if :attr:`dc` is CREDIT.
        
    .. attribute:: amount
    .. attribute:: dc

    .. attribute:: match

        Pointer to the :class:`Movement` that is being cleared by this
        movement.

    .. attribute:: cleared

        Whether

    .. attribute:: voucher_partner

        A virtual field which returns the *partner of the voucher*.
        For incoming invoices this is the supplier, for outgoing
        invoices this is the customer, for financial vouchers this is
        empty.

    .. attribute:: voucher_link

        A virtual field which shows a link to the voucher.

    .. attribute:: match_link

        A virtual field which shows a clickable variant of the match
        string. Clicking it will open a table with all movements
        having that match.

           
    .. attribute:: ana_account
           
        The analytic account to move together with this transactions.

        This file exists only when :mod:`lino_xl.lib.ana` is
        installed as well.
        
.. class:: MovementsByPartner

   The summary of this table displays the balance. A negative number
   means that we owe money to this partner, a positive numvber means
   that this partner owes us money.

>>> obj = rt.models.contacts.Partner.objects.get(pk=125)
>>> rt.show(rt.models.ledger.MovementsByPartner, obj)
**1 open movements (1599.92 €)**
>>> rt.show(rt.models.ledger.MovementsByPartner, obj, nosummary=True)
============ =============== =================================== ============== ======== ================= =========
 Value date   Voucher         Description                         Debit          Credit   Match             Cleared
------------ --------------- ----------------------------------- -------------- -------- ----------------- ---------
 10/06/2016   *SLS 28/2016*   *(4000) Customers*                  1 599,92                **SLS 28/2016**   No
                              **Balance 1599.92 (1 movements)**   **1 599,92**
============ =============== =================================== ============== ======== ================= =========
<BLANKLINE>
           
        
Vouchers
========
                
.. class:: Voucher
           
    A Voucher is a document that represents a monetary transaction.

    A voucher is never instantiated using this base model but using
    one of its subclasses. Examples of subclassed are sales.Invoice,
    vat.AccountInvoice (or vatless.AccountInvoice), finan.Statement
    etc...
    
    This model is *not* abstract so that :class:`Movement` can have a
    ForeignKey to a Voucher.

    When the partner of an empty voucher has a purchase account, Lino
    automatically creates a voucher item using this account with empty
    amount.
    

    .. attribute:: state

        The workflow state of this voucher. Choices are defined in
        :class:`VoucherStates`

    .. attribute:: journal

        The journal into which this voucher has been booked. This is a
        mandatory pointer to a :class:`Journal` instance.

    .. attribute:: number

        The sequence number of this voucher in the :attr:`journal`.

        The voucher number is automatically assigned when the voucher
        is saved for the first time.  The voucher number depends on
        whether :attr:`yearly_numbering` is enabled or not.

        There might be surprising numbering if two users create
        vouchers in a same journal at the same time.

    .. attribute:: entry_date

        The date of the journal entry, i.e. when this voucher is to
        journalized or booked.

    .. attribute:: voucher_date

        The date on the voucher (i.e. when it has been issued by its
        emitter).

        This is usually the same as :attr:`entry_date`.  Exceptions
        may be invoices arriving after their fiscal year has been
        closed.  Note that if you change :attr:`entry_date` of a
        voucher, then Lino will set the :attr:`voucher_date` to that
        date.

    .. attribute:: accounting_period

        The accounting period to which this entry is to be assigned
        to.  The default value is determined from :attr:`entry_date`.

        If user changes this field, the :attr:`number` gets
        re-computed because it might change depending on the fiscal
        year of the accounting period.

        """
              

    .. attribute:: narration

        A short explanation which ascertains the subject matter of
        this journal entry.

    .. attribute:: number_with_year


    .. method:: do_and_clear(func, do_clear)
                
        Delete all movements of this voucher, then run the given
        callable `func`, passing it a set with all partners who had at
        least one movement in this voucher. The function is expected
        to add more partners to this set.  Then call `check_clearings`
        for all these partners.

    .. method:: create_movement(item, acc_tuple, project, dc, amount, **kw):
                
        Create a movement for this voucher.

        The specified `item` may be `None` if this the movement is
        caused by more than one item.  It is used by
        :class:`DatedFinancialVoucher
        <lino_xl.lib.finan.DatedFinancialVoucher>`.
                
    .. method:: get_partner()
                
        Return the partner related to this voucher.  Overridden by
        PartnerRelated vouchers.
                
    .. method:: get_wanted_movements()
                
        Subclasses must implement this.  Supposed to return or yield a
        list of unsaved :class:`Movement` instances.

    .. method:: get_mti_leaf(self):
                
        Return the specialized form of this voucher.

        From any :class:`Voucher` instance we can get the actual
        document (Invoice, PaymentOrder, BankStatement, ...) by
        calling this method.


           
Journals
========

A **journal** is a named sequence of numbered *vouchers*.

>>> ses.show(ledger.Journals,
...     column_names="ref name trade_type account dc")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ========================= =============================== ===================== =============================== ===========================
 Reference   Designation               Designation (en)                Trade type            Account                         Primary booking direction
----------- ------------------------- ------------------------------- --------------------- ------------------------------- ---------------------------
 SLS         Factures vente            Sales invoices                  Sales                                                 Credit
 SLC         Sales credit notes        Sales credit notes              Sales                                                 Debit
 PRC         Factures achat            Purchase invoices               Purchases                                             Debit
 PMO         Bestbank Payment Orders   Bestbank Payment Orders         Bank payment orders   (4300) Pending Payment Orders   Debit
 CSH         Caisse                    Cash                                                  (5700) Cash                     Credit
 BNK         Bestbank                  Bestbank                                              (5500) BestBank                 Credit
 MSC         Opérations diverses       Miscellaneous Journal Entries                         (5700) Cash                     Credit
 VAT         Déclarations TVA          VAT declarations                Taxes                 (4513) VAT declared             Debit
=========== ========================= =============================== ===================== =============================== ===========================
<BLANKLINE>

           
.. class:: Journal

    **Fields:**

    .. attribute:: ref
    .. attribute:: trade_type

        Pointer to :class:`TradeTypes`.

    .. attribute:: voucher_type

        Pointer to an item of :class:`VoucherTypes`.

    .. attribute:: journal_group

        Pointer to an item of :class:`JournalGroups`.

    .. attribute:: yearly_numbering

        Whether the
        :attr:`number<lino_xl.lib.ledger.models.Voucher.number>` of
        vouchers should restart at 1 every year.

    .. attribute:: force_sequence

    .. attribute:: account
                   
        The account to use for the counter-movements generated by
        vouchers in this journal.

    .. attribute:: partner

        The partner to use as default partner for all vouchers in this
        journal.

        If you want Lino to suggest the cleaning of payment orders,
        then create an organization representing your bank and have
        this field point to that partner.  Note that the journal must
        also have an :attr:`account` with :attr:`Acccount.needs_partner`
        enabled in order to prevent Lino from generating
        detailed counter-entries (one per item). Clearing a payment
        order makes sense only with one counter-entry with the sum of
        all movements.
                   
    .. attribute:: printed_name
    .. attribute:: dc

        The primary booking direction.

        In a journal of *sales invoices* this should be *Debit*
        (checked), because a positive invoice total should be
        *debited* from the customer's account.

        In a journal of *purchase invoices* this should be *Credit*
        (not checked), because a positive invoice total should be
        *credited* to the supplier's account.

        In a journal of *bank statements* this should be *Debit*
        (checked), because a positive balance change should be
        *debited* from the bank's general account.

        In a journal of *payment orders* this should be *Credit* (not
        checked), because a positive total means an "expense" and
        should be *credited* from the journal's general account.

        In all financial vouchers, the amount of every item increases
        the total if its direction is opposite of the primary
        direction.

    .. attribute:: auto_check_clearings

        Whether to automatically check and update the 'cleared' status
        of involved transactions when (de)registering a voucher of
        this journal.

        This can be temporarily disabled e.g. by batch actions in
        order to save time.

    .. attribute:: auto_fill_suggestions

        Whether to automatically fill voucher item from due payments
        of the partner when entering a financial voucher.
        
    .. attribute:: template

        See :attr:`PrintableType.template
        <lino.mixins.printable.PrintableType.template>`.



Debit or credit
===============

The "PCSD" rule: A *purchase* invoice *credits* the supplier's
account, a *sales* invoice *debits* the customer's account.

>>> obj = vat.VatAccountInvoice.objects.order_by('id')[0]
>>> rt.show(ledger.MovementsByVoucher, obj)
============================= ========== =========== =========== ================ =========
 Account                       Partner    Debit       Credit      Match            Cleared
----------------------------- ---------- ----------- ----------- ---------------- ---------
 (4400) Suppliers              Bestbank               40,00       **PRC 1/2016**   No
 (4512) VAT deductible                    6,94                                     Yes
 (6010) Purchase of services              33,06                                    Yes
                                          **40,00**   **40,00**
============================= ========== =========== =========== ================ =========
<BLANKLINE>

>>> obj = sales.VatProductInvoice.objects.order_by('id')[0]
>>> rt.show(ledger.MovementsByVoucher, obj)
================== ========== ============== ============== ================ =========
 Account            Partner    Debit          Credit         Match            Cleared
------------------ ---------- -------------- -------------- ---------------- ---------
 (4000) Customers   Bestbank   2 999,85                      **SLS 1/2016**   No
 (4510) VAT due                               520,64                          Yes
 (7000) Sales                                 2 479,21                        Yes
                               **2 999,85**   **2 999,85**
================== ========== ============== ============== ================ =========
<BLANKLINE>

So the balance of a supplier's account (when open) is usually on the
*credit* side (they gave us money) while a customer's balance is
usually on the *debit* side (they owe us money).
                 
>>> from lino_xl.lib.ledger.utils import DCLABELS
>>> print(DCLABELS[ledger.TradeTypes.purchases.dc])
Credit
>>> print(DCLABELS[ledger.TradeTypes.sales.dc])
Debit



Other database models
=====================

.. class:: LedgerInfo

    A little model which holds ledger specific information per user.

    .. attribute:: user
                   
        OneToOneField pointing to the user.
        
    .. attribute:: entry_date

        The last value this user typed as :attr:`entry_date
        <Voucher.entry_date>` of a voucher.  It is the default value
        for every new voucher.

    .. classmethod:: get_by_user(self, user)


Match rules
===========

.. class:: MatchRule

    A **match rule** specifies that a movement into given account can
    be cleared using a given journal.


Payment terms
=============


.. class:: PaymentTerm
           
    The **payment term** of an invoice is a convention on how the
    invoice should be paid.

    The following fields define the default value for `due_date`:

    .. attribute:: days

        Number of days to add to :attr:`voucher_date`.

    .. attribute:: months

        Number of months to add to :attr:`voucher_date`.

    .. attribute:: end_of_month

        Whether to move :attr:`voucher_date` to the end of month.

    .. attribute:: printed_text

        Used in :xfile:`sales/VatProductInvoice/trailer.html` as
        follows::

            {% if obj.payment_term.printed_text %}
            {{parse(obj.payment_term.printed_text)}}
            {% else %}
            {{_("Payment terms")}} : {{obj.payment_term}}
            {% endif %}

    The :attr:`printed_text` field is important when using
    **prepayments** or other more complex payment terms.  Lino uses a
    rather simple approach to handle prepayment invoices: only the
    global amount and the final due date is stored in the database,
    all intermediate amounts and due dates are just generated in the
    printable document. You just define one :class:`PaymentTerm
    <lino_xl.lib.ledger.models.PaymentTerm>` row for each prepayment
    formula and configure your :attr:`printed_text` field. For
    example::

        Prepayment <b>30%</b> 
        ({{(obj.total_incl*30)/100}} {{obj.currency}})
        due on <b>{{fds(obj.due_date)}}</b>, remaining 
        {{obj.total_incl - (obj.total_incl*30)/100}} {{obj.currency}}
        due 10 days before delivery.

Accounting periods
==================

.. class:: AccountingPeriod

    An **accounting period** is the smallest time slice to be observed
    (declare) in accounting reports. Usually it corresponds to one
    *month*. Except for some small companies which declare per
    quarter.

    For each period it is possible to specify the exact dates during
    which it is allowed to register vouchers into this period, and
    also its "state": whether it is "closed" or not.

    .. attribute:: start_date
    .. attribute:: end_date
    .. attribute:: state
    .. attribute:: year
    .. attribute:: ref
    
Actors
======

          
.. class:: Journals

   The default table showing all instances of :class:`Journal`.

.. class:: ByJournal

   Mixin for journal-based tables of vouchers.
           
.. class:: Vouchers

    The base table for all tables working on :class:`Voucher`.
               
.. class:: ExpectedMovements

    A virtual table of :class:`DueMovement` rows, showing
    all "expected" "movements (payments)".

    Subclasses are :class:`DebtsByAccount` and :class:`DebtsByPartner`.

    Also subclassed by
    :class:`lino_xl.lib.finan.SuggestionsByVoucher`.

    .. attribute:: date_until
    .. attribute:: trade_type
    .. attribute:: from_journal
    .. attribute:: for_journal
    .. attribute:: account
    .. attribute:: partner
    .. attribute:: project
    .. attribute:: show_sepa

           
.. class:: DebtsByAccount

    The :class:`ExpectedMovements` accessible by clicking the "Debts"
    action button on an account.

.. class:: DebtsByPartner

    This is the table being printed in a Payment Reminder.  Usually
    this table has one row per sales invoice which is not fully paid.
    But several invoices ("debts") may be grouped by match.  If the
    partner has purchase invoices, these are deduced from the balance.

    This table is accessible by clicking the "Debts" action button on
    a Partner.

.. class:: PartnerVouchers    

    Base class for tables of partner vouchers.

    .. attribute:: cleared

        - Yes : show only completely cleared vouchers.
        - No : show only vouchers with at least one open partner movement.
        - empty: don't care about movements.


.. class:: AccountsBalance

    A virtual table, the base class for different reports that show a
    list of accounts with the following columns:

      ref description old_d old_c during_d during_c new_d new_c

    Subclasses are :class:'GeneralAccountsBalance`,
    :class:'CustomerAccountsBalance` and
    :class:'SupplierAccountsBalance`.

.. class:: GeneralAccountsBalance

    An :class:`AccountsBalance` for general accounts.           

.. class:: PartnerAccountsBalance
           
    An :class:`AccountsBalance` for partner accounts.

.. class:: CustomerAccountsBalance
           
    A :class:`PartnerAccountsBalance` for the TradeType "sales".
    
.. class:: SuppliersAccountsBalance

    A :class:`PartnerAccountsBalance` for the TradeType "purchases".

.. class:: DebtorsCreditors

    Abstract base class for different tables showing a list of
    partners with the following columns:

      partner due_date balance actions

.. class:: Debtors

    Shows partners who have some debt against us.
    Inherits from :class:`DebtorsCreditors`.

.. class:: Creditors

    Shows partners who give us some form of credit.
    Inherits from :class:`DebtorsCreditors`.

           


.. _cosi.specs.ledger.movements:


.. _cosi.specs.ledger.vouchers:


.. _cosi.specs.ledger.journals:



Trade types
===========

The **trade type** is one of the basic properties of every ledger
operation which involves an external partner.  Every partner movement
is of one and only one trade type.

The default list of trade types is:

>>> rt.show(ledger.TradeTypes)
======= =========== ===================== ==================================== ================================================ =============================== =====================================
 value   name        text                  Main account                         Base account                                     Product account field           Invoice account field
------- ----------- --------------------- ------------------------------------ ------------------------------------------------ ------------------------------- -------------------------------------
 S       sales       Sales                 *(4000) Customers* (Customers)       *(7000) Sales* (Sales)                           Sales account (sales_account)
 P       purchases   Purchases             *(4400) Suppliers* (Suppliers)       *(6040) Purchase of goods* (Purchase of goods)                                   Purchase account (purchase_account)
 W       wages       Wages                 *(4500) Employees* (Employees)       *(6300) Wages* (Wages)
 T       taxes       Taxes                 *(4600) Tax Offices* (Tax Offices)   *(4513) VAT declared* (VAT declared)
 C       clearings   Clearings
 B       bank_po     Bank payment orders
======= =========== ===================== ==================================== ================================================ =============================== =====================================
<BLANKLINE>

Your application might have a different list.  You can see the
actually configured list for your site via :menuselection:`Explorer
--> Accounting --> Trade types`.


.. class:: TradeTypes
           
    The choicelist with the *trade types* defined for this
    application.

    The default configuration defines the following trade types:

    .. attribute:: sales

        A sale transaction is when you write an invoice to a customer
        and then expect the customer to pay it.

    .. attribute:: purchases

        A purchase transaction is when you get an invoice from a
        provider who expects you to pay it.


    .. attribute:: wages

        A wage transaction is when you write a payroll (declare the
        fact that you owe some wage to an employee) and later pay it
        (e.g. via a payment order).


    .. attribute:: clearings

        A clearing transaction is when an employee declares that he
        paid some invoice for you, and later you pay that money back
        to his account.

Every trade type has the following properties.

.. class:: TradeType
           
    Base class for the choices of :class:`TradeTypes`.

    .. attribute:: dc

        The default booking direction.

    .. attribute:: main_account

        The common account into which the total amount of partner
        vouchers (base + taxes) and their payments should be booked.

    .. attribute:: base_account

        The common account into which the base amount of any operation
        should be booked.
        
    .. attribute:: invoice_account_field_name

        The name of a field to be injected on the :class:`Partner
        <lino_xl.lib.contacts.Partner>` model which points to an
        account to be used instead of the default
        :attr:`base_account`.

    .. attribute:: base_account_field_name

        The name of a field to be injected on the :class:`Product
        <lino.modlib.products.models.Product>` database model which
        points to an account to be used instead of the default
        :attr:`base_account`.
                   
    .. attribute:: price_field

        The name and label of the `price` field to be defined on the
        :class:`Product <lino.modlib.products.Product>` database
        model.


    .. method:: get_product_base_account(product)

        Return the account into which the **base amount** of any
        operation of this rete type should be booked.
        
        This is either the base account defined in the
        :attr:`base_account_field_name` for the given product, or the
        site-wide :attr:`base_account`.
                
    .. method:: get_catalog_price(product)

        Return the catalog price of the given product for operations
        with this trade type.
        
    .. method:: get_partner_invoice_account(partner)
                   
        Return the account to use as default value for account invoice
        items.  This is the :attr:`invoice_account_field` of the given
        partner and can be `None`.




Match rules
===========

A **match rule** specifies that a movement into given account can be
*cleared* using a given journal.

>>> ses.show(ledger.MatchRules)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==== ==================== =====================================
 ID   Account              Journal
---- -------------------- -------------------------------------
 1    (4000) Customers     Sales invoices (SLS)
 2    (4000) Customers     Sales credit notes (SLC)
 3    (4400) Suppliers     Purchase invoices (PRC)
 4    (4000) Customers     Bestbank Payment Orders (PMO)
 5    (4400) Suppliers     Bestbank Payment Orders (PMO)
 6    (6300) Wages         Bestbank Payment Orders (PMO)
 7    (4000) Customers     Cash (CSH)
 8    (4400) Suppliers     Cash (CSH)
 9    (6300) Wages         Cash (CSH)
 10   (4000) Customers     Bestbank (BNK)
 11   (4400) Suppliers     Bestbank (BNK)
 12   (6300) Wages         Bestbank (BNK)
 13   (4000) Customers     Miscellaneous Journal Entries (MSC)
 14   (4400) Suppliers     Miscellaneous Journal Entries (MSC)
 15   (6300) Wages         Miscellaneous Journal Entries (MSC)
 16   (4600) Tax Offices   VAT declarations (VAT)
==== ==================== =====================================
<BLANKLINE>

For example a payment order can be used to clear an open suppliers
invoice or (less frequently) to send back money that a customer had
paid too much:

>>> jnl = ledger.Journal.objects.get(ref="PMO")
>>> rt.show(ledger.MatchRulesByJournal, jnl)
==================
 Account
------------------
 (4000) Customers
 (4400) Suppliers
 (6300) Wages
==================
<BLANKLINE>

Or a sales invoice can be used to clear another sales invoice:

>>> jnl = ledger.Journal.objects.get(ref="SLS")
>>> rt.show(ledger.MatchRulesByJournal, jnl)
==================
 Account
------------------
 (4000) Customers
==================
<BLANKLINE>



Debtors
=======

**Debtors** are partners who received credit from us and therefore are
in debt towards us. The most common debtors are customers,
i.e. partners who received a sales invoice from us and did not yet pay
that invoice.

Two debtors in the list below are not customers: Bestbank and the tax
office.  Bestbank is a debtor because pending payment orders are
booked to this account.  The tax office is a debtor because we had
more VAT deductible (sales) than VAT due (purchases).

>>> ses.show(ledger.Debtors, column_names="partner partner_id balance")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
=================================== ========== ===============
 Partner                             ID         Balance
----------------------------------- ---------- ---------------
 Bestbank                            100        2 382,15
 Mehrwertsteuer-Kontrollamt Eupen    192        7 010,27
 Hans Flott & Co                     108        1 197,90
 Van Achter NV                       107        279,90
 Bernd Brechts Bücherladen           109        1 599,92
 Garage Mergelsberg                  105        1 885,73
 Ausdemwald Alfons                   116        770,00
 Reinhards Baumschule                110        2 349,81
 Arens Annette                       114        4 239,63
 ...
 Radermacher Berta                   154        535,00
 Radermacher Christian               155        3 319,78
 di Rupo Didier                      164        639,92
 Radermacher Guido                   159        2 349,81
 da Vinci David                      165        1 235,96
 Radermacher Inge                    162        726,00
 Radermacher Alfons                  153        280,00
 Radermacher Jean                    163        3 599,71
 Radermacher Hans                    160        951,82
 Radermacher Hedi                    161        525,00
 **Total (62 rows)**                 **8421**   **97 936,71**
=================================== ========== ===============
<BLANKLINE>



The :class:`DebtsByPartner <lino_xl.lib.ledger.DebtsByPartner>` shows
one row per uncleared invoice. For example here is the detail of the
debts for partner 116 from above list:

>>> obj = contacts.Partner.objects.get(pk=116)
>>> obj
Partner #116 ('Ausdemwald Alfons')
>>> ses.show(ledger.DebtsByPartner, obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE -REPORT_UDIFF
==================== ============ ========================== ==========
 Due date             Balance      Debts                      Payments
-------------------- ------------ -------------------------- ----------
 13/04/2016           770,00       `SLS 18/2016 <Detail>`__
 **Total (1 rows)**   **770,00**
==================== ============ ========================== ==========
<BLANKLINE>

This shows that the partner received one sales invoice and did a
partial payment on the same day.


**Creditors** are partners hwo gave us credit, IOW to whom we owe
money.  The most common creditors are providers, i.e. partners who
send us a purchase invoice (which we did not yet pay).

>>> ses.show(ledger.Creditors, column_names="partner partner_id balance")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== ========= ===============
 Partner               ID        Balance
--------------------- --------- ---------------
 Rumma & Ko OÜ         101       91,38
 Bäckerei Ausdemwald   102       8 368,19
 Donderweer BV         106       1 821,15
 Bäckerei Mießen       103       17 771,00
 Bäckerei Schmitz      104       48 194,90
 **Total (5 rows)**    **516**   **76 246,62**
===================== ========= ===============
<BLANKLINE>

Partner 101 from above list is both a supplier and a customer:

>>> obj = contacts.Partner.objects.get(pk=101)
>>> ses.show(ledger.DebtsByPartner, obj)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
===================== ============ ========================= ==========================
 Due date              Balance      Debts                     Payments
--------------------- ------------ ------------------------- --------------------------
 10/01/2016            -141,30                                `PRC 2/2016 <Detail>`__
 14/01/2016            2 039,82     `SLS 2/2016 <Detail>`__
 03/02/2016            -142,00                                `PRC 9/2016 <Detail>`__
 02/04/2016            -143,40                                `PRC 16/2016 <Detail>`__
 30/04/2016            -142,10                                `PRC 23/2016 <Detail>`__
 01/08/2016            -140,20                                `PRC 30/2016 <Detail>`__
 02/08/2016            -141,30                                `PRC 37/2016 <Detail>`__
 02/08/2016            -142,00                                `PRC 44/2016 <Detail>`__
 13/08/2016            -143,40                                `PRC 51/2016 <Detail>`__
 10/09/2016            -142,10                                `PRC 58/2016 <Detail>`__
 03/10/2016            -140,20                                `PRC 65/2016 <Detail>`__
 03/12/2016            -141,30                                `PRC 72/2016 <Detail>`__
 31/12/2016            -142,00                                `PRC 79/2016 <Detail>`__
 03/04/2017            -144,80                                `PRC 2/2017 <Detail>`__
 04/04/2017            -143,50                                `PRC 9/2017 <Detail>`__
 02/04/2017            -141,60                                `PRC 16/2017 <Detail>`__
 **Total (16 rows)**   **-91,38**
===================== ============ ========================= ==========================
<BLANKLINE>

Note that most numbers in above table are negative. A purchase invoice
is a *credit* received from the provider, and we asked a list of
*debts* by partner.


Fiscal years
============

Lino has a table of **fiscal years**.  A fiscal year often corresponds
to the calendar year, but not necessarily.

If :mod:`lino_xl.lib.sheets` is installed, the detail window of a
FiscalYear object shows the financial reports (balance sheet and
income statement) for this year.

.. class:: FiscalYear
           
    .. attribute:: start_date
    .. attribute:: end_date
    .. attribute:: state
                   
.. class:: FiscalYears

    The fiscal years available in this database.


    
The :mod:`lino_xl.lib.ledger.fixtures.std` fixture fills this table
with 5 years starting from :attr:`start_year
<lino_xl.lib.ledger.Plugin.start_year>`.


>>> dd.plugins.ledger.start_year
2016

>>> dd.today()
datetime.date(2017, 3, 12)

>>> dd.today().year + 5
2022

>>> rt.show(ledger.FiscalYears)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============ ============ =======
 Reference   Start date   End date     State
----------- ------------ ------------ -------
 2016        01/01/2016   31/12/2016   Open
 2017        01/01/2017   31/12/2017   Open
 2018        01/01/2018   31/12/2018   Open
 2019        01/01/2019   31/12/2019   Open
 2020        01/01/2020   31/12/2020   Open
 2021        01/01/2021   31/12/2021   Open
 2022        01/01/2022   31/12/2022   Open
=========== ============ ============ =======
<BLANKLINE>


Accounting periods
==================

Each ledger movement happens in a given **accounting period**.  
An accounting period usually corresponds to a month of the calendar.
Accounting periods are automatically created the first time they are
needed by some operation.


>>> rt.show(ledger.AccountingPeriods)
=========== ============ ============ ============= ======= ========
 Reference   Start date   End date     Fiscal year   State   Remark
----------- ------------ ------------ ------------- ------- --------
 2016-01     01/01/2016   31/01/2016   2016          Open
 2016-02     01/02/2016   29/02/2016   2016          Open
 2016-03     01/03/2016   31/03/2016   2016          Open
 2016-04     01/04/2016   30/04/2016   2016          Open
 2016-05     01/05/2016   31/05/2016   2016          Open
 2016-06     01/06/2016   30/06/2016   2016          Open
 2016-07     01/07/2016   31/07/2016   2016          Open
 2016-08     01/08/2016   31/08/2016   2016          Open
 2016-09     01/09/2016   30/09/2016   2016          Open
 2016-10     01/10/2016   31/10/2016   2016          Open
 2016-11     01/11/2016   30/11/2016   2016          Open
 2016-12     01/12/2016   31/12/2016   2016          Open
 2017-01     01/01/2017   31/01/2017   2017          Open
 2017-02     01/02/2017   28/02/2017   2017          Open
 2017-03     01/03/2017   31/03/2017   2017          Open
=========== ============ ============ ============= ======= ========
<BLANKLINE>


The *reference* of a new accounting period is computed by applying the
voucher's entry date to the template defined in the
:attr:`date_to_period_tpl
<lino_xl.lib.ledger.AccountingPeriod.get_for_date>` setting.  The
default implementation leads to the following references:

>>> print(ledger.AccountingPeriod.get_ref_for_date(i2d(19940202)))
1994-02
>>> print(ledger.AccountingPeriod.get_ref_for_date(i2d(20150228)))
2015-02
>>> print(ledger.AccountingPeriod.get_ref_for_date(i2d(20150401)))
2015-04

You may manually create other accounting periods. For example

- `2015-00` might stand for a fictive "opening" period before January
  2015 and after December 2014.

- `2015-13` might stand for January 2016 in a company which is
  changing their fiscal year from "January-December" to "July-June".
  

Payment terms
=============

>>> rt.show('ledger.PaymentTerms')
==================== ======================================= ======================================= ======== ========= ==============
 Reference            Designation                             Designation (en)                        Months   Days      End of month
-------------------- --------------------------------------- --------------------------------------- -------- --------- --------------
 07                   Payment seven days after invoice date   Payment seven days after invoice date   0        7         No
 10                   Payment ten days after invoice date     Payment ten days after invoice date     0        10        No
 30                   Payment 30 days after invoice date      Payment 30 days after invoice date      0        30        No
 60                   Payment 60 days after invoice date      Payment 60 days after invoice date      0        60        No
 90                   Payment 90 days after invoice date      Payment 90 days after invoice date      0        90        No
 EOM                  Payment end of month                    Payment end of month                    0        0         Yes
 P30                  Prepayment 30%                          Prepayment 30%                          0        30        No
 PIA                  Payment in advance                      Payment in advance                      0        0         No
 **Total (8 rows)**                                                                                   **0**    **227**
==================== ======================================= ======================================= ======== ========= ==============
<BLANKLINE>




Journal groups
==============

.. class:: JournalGroups

    The list of possible journal groups.

    This list is used to build the main menu. For each journal group
    there will be a menu item in the main menu.

    Journals whose :attr:`journal_group <Journal.journal_group>` is
    empty will not be available through the main user menu.

    The default configuration has the following journal groups:

    .. attribute:: sales

        For sales journals.

    .. attribute:: purchases

        For purchases journals.

    .. attribute:: wages

        For wages journals.

    .. attribute:: financial

        For financial journals (bank statements and cash reports)

           
.. class:: PeriodStates

    The list of possible states of an accounting period.
    
    .. attribute:: open
                   
    .. attribute:: closed


.. class:: VoucherTypes
           
    A list of the voucher types available in this application. Items
    are instances of :class:VoucherType`.

    The :attr:`voucher_type <lino_xl.lib.ledger.Journal.voucher_type>`
    field of a journal points to an item of this.


           
.. class:: VoucherType
           
    Base class for all items of :class:`VoucherTypes`.
    
    The **voucher type** defines the database model used to store
    vouchers of this type (:attr:`model`).

    But it can be more complex: actually the voucher type is defined
    by its :attr:`table_class`, i.e. application developers can define
    more than one *voucher type* per model by providing alternative
    tables (views) for it.

    Every Lino Cosi application has its own global list of voucher
    types defined in the :class:`VoucherTypes` choicelist.

    .. attribute:: model

        The database model used to store vouchers of this type.
        A subclass of :class:`lino_xl.lib.ledger.models.Voucher``.

    .. attribute:: table_class

        Must be a table on :attr:`model` and with `master_key` set to
        the
        :attr:`journal<lino_xl.lib.ledger.models.Voucher.journal>`.

              

.. class:: VoucherState
           
    Base class for items of :class:`VoucherStates`.

    .. attribute:: editable
                   
        Whether a voucher in this state is editable.
        
    
.. class:: VoucherStates
           
    The list of possible states of a voucher.

    In a default configuration, vouchers can be :attr:`draft`,
    :attr:`registered`, :attr:`cancelled` or :attr:`signed`.

    .. attribute:: draft

        *Draft* vouchers can be modified but are not yet visible as movements
        in the ledger.

    .. attribute:: registered

        *Registered* vouchers cannot be modified, but are visible as
        movements in the ledger.

    .. attribute:: cancelled

        *Cancelled* is similar to *Draft*, except that you cannot edit
        the fields. This is used for invoices which have been sent,
        but the customer signaled that they doen't agree. Instead of
        writing a credit nota, you can decide to just cancel the
        invoice.

    .. attribute:: signed

        The *Signed* state is similar to *registered*, but cannot
        usually be deregistered anymore. This state is not visible in
        the default configuration. In order to make it usable, you
        must define a custom workflow for :class:`VoucherStates`.


           
Model mixins
============


.. class:: SequencedVoucherItem

   A :class:`VoucherItem` which also inherits from
   :class:`lino.mixins.sequenced.Sequenced`.


.. class:: AccountVoucherItem


    Abstract base class for voucher items which point to an account.
    
    This is also a :class:`SequencedVoucherItem`.
    
    This is subclassed by
    :class:`lino_xl.lib.vat.models.InvoiceItem`
    and
    :class:`lino_xl.lib.vatless.models.InvoiceItem`.
           
    It defines the :attr:`account` field and some related methods.

    .. attribute:: account

        ForeignKey pointing to the account (:class:`ledger.Account
        <lino_xl.lib.ledger.Account>`) that is to be moved.

   

.. class:: VoucherItem
           
    Base class for items of a voucher.

    Subclasses must define the following fields:

    .. attribute:: voucher

        Pointer to the voucher which contains this item.  Non
        nullable.  The voucher must be a subclass of
        :class:`ledger.Voucher<lino_xl.lib.ledger.models.Voucher>`.
        The `related_name` must be `'items'`.
    

    .. attribute:: title

        The title of this voucher.

        Currently (because of :djangoticket:`19465`), this field is
        not implemented here but in the subclasses:

        :class:`lino_xl.lib.vat.models.AccountInvoice`
        :class:`lino_xl.lib.vat.models.InvoiceItem`

           
.. class:: Matching

    Model mixin for database objects that are considered *matching
    transactions*.  A **matching transaction** is a transaction that
    points to some other movement which it "clears" at least partially.

    A movement is cleared when its amount equals the sum of all
    matching movements.

    Adds a field :attr:`match` and a chooser for it.  Requires a field
    `partner`.  The default implementation of the chooser for
    :attr:`match` requires a `journal`.

    Base class for :class:`lino_xl.lib.vat.AccountInvoice`
    (and e.g. `lino_xl.lib.sales.Invoice`, `lino_xl.lib.finan.DocItem`)
    
    .. attribute:: match

       Pointer to the :class:`movement
       <lino.modlib.ledger.models.Movement>` which is being cleared by
       this movement.

.. class:: PartnerRelated
           
    Base class for things that are related to one and only one trade
    partner. This is base class for both (1) trade document vouchers
    (e.g. invoices or offers) and (2) for the individual entries of
    financial vouchers and ledger movements.

    .. attribute:: partner

        The recipient of this document. A pointer to
        :class:`lino_xl.lib.contacts.models.Partner`.

    .. attribute:: payment_term

        The payment terms to be used in this document.  A pointer to
        :class:`PaymentTerm`.

    .. attribute:: recipient

        Alias for the partner


.. class:: ProjectRelated

    Model mixin for objects that are related to a :attr:`project`.

    .. attribute:: project

        Pointer to the "project". This field exists only if the
        :attr:`project_model <Plugin.project_model>` setting is
        nonempty.


.. class:: PeriodRange

    Model mixin for objects that consider, cover or observe a range of
    *accounting periods*.

    .. attribute:: start_period

       The period which marks the beginning of the range to
       consider.
                   
    .. attribute:: end_period

       Leave empty if you want only one period (specified in
       :attr:`start_period`). If this is non-empty, all periods
       between and including these two are to be considered.


.. class:: PeriodRangeObservable       

    Model mixin for objects that can be filtered by a range of
    *accounting periods*. This adds two fields start_period and
    end_period to the parameter fields.


.. class:: ItemsByVoucher

    Shows the items of this voucher.

    This is used as base class for slave tables in
    :mod:`lino_xl.lib.finan`,
    :mod:`lino_xl.lib.vat`,
    :mod:`lino_xl.lib.vatless`,
    :mod:`lino_xl.lib.ana`, ...


Utilities
=========

.. class:: DueMovement
           
    A volatile object representing a group of matching movements.

    A **due movement** is a movement which a partner should do in
    order to satisfy their debt.  Or which we should do in order to
    satisfy our debt towards a partner.

    The "matching" movements of a given movement are those whose
    `match`, `partner` and `account` fields have the same values.
    
    These movements are themselves grouped into "debts" and "payments".
    A "debt" increases the debt and a "payment" decreases it.
    
    .. attribute:: match

        The common `match` string of these movments

    .. attribute:: dc

        Whether I mean *my* debts and payments (towards that partner)
        or those *of the partner* (towards me).

    .. attribute:: partner

    .. attribute:: account



           

Plugin attributes
=================

See :class:`lino_xl.lib.ledger.Plugin`.


Mixins
======

.. class:: AccountBalances

    A table which shows a list of general ledger accounts during the
    observed period, showing their old and new balances and the sum of
    debit and credit movements.
           
           
        
.. class:: AccountingPeriodRange

    A parameter panel with two fields:

    .. attribute:: start_period

        Start of observed period range.
                   
    .. attribute:: end_period

        Optional end of observed period range.  Leave empty to
        consider only the Start period.
        
                   

The Y2K problem
===============

Lino supports accounting across milleniums.

>>> FiscalYear = rt.models.ledger.FiscalYear
>>> print(FiscalYear.year2ref(1985))
1985
>>> print(FiscalYear.year2ref(9985))
9985


But there are legacy systems where the year was internally represented
using a two-letter code.

The
:attr:`fix_y2k <lino_xl.lib.ledger.Plugin.fix_y2k>` is either True or
False.



>>> dd.plugins.ledger.fix_y2k
False

>>> dd.plugins.ledger.fix_y2k = True
>>> print(FiscalYear.year2ref(1985))
85
>>> print(FiscalYear.year2ref(1999))
99
>>> print(FiscalYear.year2ref(2000))
A0
>>> print(FiscalYear.year2ref(2015))
B5
>>> print(FiscalYear.year2ref(2135))
N5
>>> print(FiscalYear.year2ref(2259))
Z9
>>> print(FiscalYear.year2ref(2260))
[0

The `on_ledger_movement` signal
===============================

.. data:: on_ledger_movement

    Custom signal sent when a partner has had at least one change in a
    ledger movement.
    
    - `sender`   the database model
    - `instance` the partner

Don't read me
=============

Until 20181016 it was not possible to manually reverse the sort order
of a virtual field having a sortable_by which contained itself a
reversed field.  The :attr:`Movement.credit` field is an example:

>>> rmu(ledger.Movement.get_data_elem('credit').sortable_by)
['-amount', 'value_date']

>>> par = contacts.Partner.objects.get(pk=122)
>>> url = "api/ledger/MovementsByPartner?fmt=json&mk=122&mt=17"
>>> args = ('count rows no_data_text success title param_values', 1)
>>> demo_get('robin', url + "&sort=credit&dir=ASC", *args)

The following failed before 20181016:

>>> demo_get('robin', url + "&sort=credit&dir=DESC", *args)

