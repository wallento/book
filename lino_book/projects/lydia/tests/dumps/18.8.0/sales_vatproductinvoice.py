# -*- coding: UTF-8 -*-
logger.info("Loading 24 objects to table sales_vatproductinvoice...")
# fields: voucher_ptr, printed_by, partner, payment_term, match, your_ref, due_date, total_incl, total_base, total_vat, vat_regime, items_edited, language, subject, intro, paper_type
loader.save(create_sales_vatproductinvoice(36,None,101,2,u'',u'',date(2015,1,13),'450.00','450.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(37,None,102,3,u'',u'',date(2015,1,17),'880.00','880.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(38,None,103,4,u'',u'',date(2015,2,7),'1370.00','1370.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(39,None,104,5,u'',u'',date(2015,3,10),'240.00','240.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(40,None,105,6,u'',u'',date(2015,4,10),'765.00','765.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(41,None,106,7,u'',u'',date(2015,2,28),'920.00','920.00','0.00',u'30',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(42,None,107,8,u'',u'',date(2015,3,9),'450.00','450.00','0.00',u'35',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(43,None,108,1,u'',u'',date(2015,2,8),'880.00','880.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(44,None,109,2,u'',u'',date(2015,2,16),'1370.00','1370.00','0.00',u'30',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(45,None,110,3,u'',u'',date(2015,3,16),'240.00','240.00','0.00',u'35',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(46,None,111,4,u'',u'',date(2015,5,6),'765.00','765.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(47,None,112,5,u'',u'',date(2015,6,6),'920.00','920.00','0.00',u'30',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(48,None,113,6,u'',u'',date(2015,7,7),'450.00','450.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(49,None,114,7,u'',u'',date(2015,4,30),'880.00','880.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(50,None,115,8,u'',u'',date(2015,5,10),'1370.00','1370.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(51,None,115,8,u'',u'',date(2015,5,11),'240.00','240.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(52,None,116,1,u'',u'',date(2015,4,12),'765.00','765.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(53,None,117,2,u'',u'',date(2015,4,20),'920.00','920.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(54,None,118,3,u'',u'',date(2015,5,16),'450.00','450.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(55,None,119,4,u'',u'',date(2015,6,6),'880.00','880.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(56,None,120,5,u'',u'',date(2015,7,7),'1370.00','1370.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(57,None,121,6,u'',u'',date(2015,8,7),'240.00','240.00','0.00',u'10',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(58,None,122,7,u'',u'',date(2015,5,31),'765.00','765.00','0.00',u'20',True,u'',u'',u'',None))
loader.save(create_sales_vatproductinvoice(59,None,122,7,u'',u'',date(2015,5,31),'920.00','920.00','0.00',u'20',True,u'',u'',u'',None))

loader.flush_deferred_objects()
