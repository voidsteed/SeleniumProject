"""
DO NOT DELETE THIS FILE. THIS IS FOR DEBUGGING.
"""

from money_transfer_fee_query import Money_Transfer_Fee_Query
import time

def main():
    """
    Input:  Company, 
            Origin country,
            Destination_country,
            Sending Amount,
            Pay_method,
            Receive_method = "Back Account" (Cash)
    """
#------------------------western union-------------------
#    wu = Money_Transfer_Fee_Query('wu','US','CN',200,'Bank Account','DEPOSIT')
#    lst = wu.get_country_list()
#    #print "before",len(lst)
#    #lst = lst[10:]
#    print "after",len(lst)
#    for i,c in enumerate(lst):
#        print "----------------------------"
#        print "Country Code: ", c
#        wu1 = Money_Transfer_Fee_Query('wu','US',c, 1000,'Bank Account','DEPOSIT')
#        data1 = wu1.parse()
#        print "INDEX----------------------------",i
#        for key,value in data1.items():
#            print key, value
#        #"Handle exception for trim the list and open a new query"
#--------------------------------------------------------------

#------------------------Money Gram-------------------
#    mg = Money_Transfer_Fee_Query('mgi','US','MEX',200,'Bank Account','DEPOSIT')
#    lst = mg.get_country_list()
#    lst = lst[81:]
#    print "after",len(lst)
#    for i,c in enumerate(lst):
#        print "----------------------------"
#        print "Country Code: ", c
#        mg1 = Money_Transfer_Fee_Query('mgi','US',c, 1000,'Bank Account','DEPOSIT')
#        data_mg = mg1.parse()
#        print "INDEX----------------------------",i
#        for key,value in data_mg.items():
#            print key, value
#--------------------------------------------------------------
#    mg1 = Money_Transfer_Fee_Query('mgi','US','CHN',200,'Bank Account','DEPOSIT')
#    data1 = mg1.parse()
#    print "1----------------------------"
#    for key,value in data1.items():
#        print key, value
#------------------------Xoom-------------------
#    xoom = Money_Transfer_Fee_Query('xoom','US','CN',200,'Bank Account','DEPOSIT')
#    lst = xoom.get_country_list()
#    #print "before",lst
#    lst = lst[26:]
#    print "after",lst
#    for i,c in enumerate(lst):
#        print "----------------------------"
#        print "Country Code: ", c
#        xoom1 = Money_Transfer_Fee_Query('xoom','US',c, 200,'Bank Account','DEPOSIT')
#        data_xoom = xoom1.parse()
#        print "INDEX----------------------------",i
#        for key,value in data_xoom.items():
#            print key, value
#--------------------------------------------------------------


main()
