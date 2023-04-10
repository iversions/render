import os
import glob
import pdfplumber
import pathlib
from pathlib import Path
import json
#import configparser
import pandas as pd
from checkdt import checkdate
import time
import datetime
# from datetime import datetime
import re
from string import ascii_lowercase
from itertools import groupby
from ast import literal_eval
import pyodbc

#config_obj = configparser.ConfigParser()
#config_obj.read('/home/shashi/Documents/WorkingFolder/venv/afcons/configfile/configfile.ini')
#dbparam = config_obj['mssql']
#fol_loc = config_obj['folder_path']
#badchar = config_obj['bad_char']

server = 'tcp:sql.prosares.net'
database = 'Afcons_SIP_DB'
username = 'Afcons_User'
password = 'Nimd@!008'

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
cursor = conn.cursor()


# def checkdate(string):
#     for format in ["%b %d, %Y", "%d-%b-%Y","%d-%m-%Y", "%m-%d-%Y", "%d-%b-%y","%d/%b/%Y", "%m/%d/%Y","%d-%m-%y","%d/%m/%y"]:
#         try:
#             return datetime.datetime.strptime(string, format).date()
#         except ValueError:
#             continue
#     raise ValueError(string)

lowcase = set(ascii_lowercase)

def find_regex(p):
    nvar = []
    for c in p:
        if c.isdigit():
            nvar.append("d")
        elif c.isalnum():
            nvar.append("w")
        elif c in lowcase:
            nvar.append("t")
        else:
            nvar.append(c)
    grp = groupby(nvar)
    return ''.join(f'\\{what}{{{how_many}}}'
                   if how_many>1 else f'\\{what}'
                   for what, how_many in ((g[0],len(list(g[1]))) for g in grp))

def corefc(path,vname):
    conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM dbo.Training1 WHERE UNIQUENAME = ? AND IsActive = ?""",(vname,1,))
    row  = cursor.fetchall()
    fdata = row[0]
    Id,VendorName,VendorGSTIN,InvoiceNumber,InvoiceNoRegex,InvoiceNoLength,InvoiceNoPrefix,InvoiceNoSuffix,\
        InvoiceDate,InvoiceDateRegex,InvoiceDateLength,InvoiceDatePrefix,InvoiceDateSuffix,PNRNo,PNRNoLength,\
            PNRNoSuffix,PNRNoPrefix,PassengerName,PassengerNameSuffix,PassengerNamePrefix,SectorFrom,SectorFromSuffix,\
                SectorFromPrefix,SectorTo,SectorToSuffix,SectorToPrefix,TaxableValue,NonTaxableValue,CGST,CGSTPrefix,SGST,\
                    SGSTPrefix,IGST,IGSTPrefix,Total,HSNCode,IsActive,CreatedBy,CreatedDateUtc,ModifiedBy,ModifiedDateUtc,\
                        PassengerName1,PassengerName2,SenderEmailID,EmployeeCode,EmployeeName,ProviderName,PhoneNumberefix,\
                            PhoneNumber,SubscribersName1,SubscribersName2,SubscribersNamePrefix,BillNumber,BillNoRegex,\
                                BillNoLength,BillNoPrefix,BillNoSuffix,BillDate,BillDateRegex,BillDateLength,BillDatePrefix,\
                                    BillDateSuffix,BillPeriod,BillPeriodPrefix,BillPeriodsuffix,BillAmount,T_CGST,T_CGSTPrefix,\
                                        T_SGST,T_SGSTPrefix,T_IGST,T_IGSTPrefix,T_Total,InvoiceNumberSplit,cccInvoiceNumberPosition,InvoiceNoprefixposition,\
                                            InvoiceNosuffixposition,InvoiceDatePosition,InvoiceDateprefixposition,InvoiceDatesuffixposition,PNRNumberPosition,\
                                                PNRNoprefixposition,PNRsuffixposition,PassengerNamePosition,PassengerNamepreffixposition,PassengerNamesuffixposition,\
                                                    Sectorfromsuffixposition,Sectorfrompreffixposition,Sectortopreffixposition,Sectortosuffixposition,GSTListNo,\
                                                        InvoiceAmount,SectortoPosition,SectorfromPosition,pan,gstregex,UniqueName = fdata

    conn.close()
    # return fdata

    INP1 = InvoiceNoprefixposition.split(',')[0]# Inv no preffix
    INP1 = int(INP1)
    INP2 = InvoiceNoprefixposition.split(',')[1]# Inv no preffix
    INP2 = int(INP2)

    INS1 = InvoiceNosuffixposition.split(',')[0]# Inv no suffix
    INS1 = int(INS1)
    INS2 = InvoiceNosuffixposition.split(',')[1]# Inv no suffix
    INS2 = int(INS2)

    IDP1 = InvoiceDateprefixposition.split(',')[0]# Inv dt preffix
    IDP1 = int(IDP1)
    IDP2 = InvoiceDateprefixposition.split(',')[1]# Inv dt preffix
    IDP2 = int(IDP2)

    IDS1 = InvoiceDatesuffixposition.split(',')[0]# Inv dt suffix
    IDS1 = int(IDS1)
    IDS2 = InvoiceDatesuffixposition.split(',')[1]# Inv dt suffix
    IDS2 = int(IDS2)

    IT1 = Total.split(',')[0]# Inv ttl list no
    IT1 = int(IT1)
    IT2 = Total.split(',')[1]# Inv ttl location within list
    IT2 = int(IT2)

    # INV_NO_SPLIT = rr1['AA'][2] #Inv no splitter

    INV_NO_POSITION = cccInvoiceNumberPosition# Inv no position
    INV_NO_POSITION = int(INV_NO_POSITION)

    INV_DATE_POSITION = InvoiceDatePosition# Inv dt position
    INV_DATE_POSITION = int(INV_DATE_POSITION)

    PASSENGER_NAME_POSITION = PassengerNamePosition# Inv name position

# p0= pdfplumber.open(pdfpath)
    with pdfplumber.open(path) as p0:
        firstpage = p0.pages[0]
        charst = firstpage.extract_words()
        forgst = firstpage.extract_text()
        invc3 = firstpage.extract_table()

    invc2 = [[item.replace(u'\xa0', ' ') if isinstance(item, str) else item for item in items] for items in invc3]
    # return invc3,invc2
    T1 = 0
    T2 = 0
    T3 = 0
    T4 = 0
    T5 = 0
    T6 = 0

    u = 0
    z = []
    for x in charst:
        w = charst[u]['text']
        u+=1
        z.append(w)
    K =':'
    while(K in z):
        z.remove(K)

    newz = [item.replace("\xad","-") for item in z]    

    vgst = ''
    y = re.findall(gstregex,forgst)
    for i in y:
        if pan in i:
            vgst = i
    print('found in text',vgst)

    if BillNumber == "1":
        INN1 = BillNoRegex.split(',')[0]
        INN1 = int(IT1)
        INN2 = BillNoRegex.split(',')[1]
        INN2 = int(IT2)
        aaa = invc3[INN1][INN2]
        print('Invoice Number is :',invc3[INN1][INN2])

    elif BillNumber == '0': 
        w = 0
        for inv in newz:
            w+=1
            if inv == InvoiceNumber:
                aaa = newz[w+INV_NO_POSITION]
                print('Invoice Number is:',aaa)
                break

    testreg = find_regex(aaa)
    testtxt = aaa
    pref1 = w+INP1
    pref2 = w+INP2
    suff1 = w+INS1
    suff2 = w+INS2
    if testreg == InvoiceNoRegex:
        T1+=25
    
    zz = re.search(testreg,testtxt)

    if len(zz.group()) == literal_eval(InvoiceNoLength):
        T1+=25

    if InvoiceNoPrefix == " ".join(str(i) for i in newz[pref1:pref2]):
        T1+=25

    if InvoiceNoSuffix == " ".join(str(i) for i in newz[suff1:suff2]):
        T1+=25
    
    finvno = aaa.replace(':','')

    print(f'Invoice Number is: {aaa}, with confidence level of {T1}%') 

    # print('\n')

    if BillNoLength == '1':
        IND1 = BillNoPrefix.split(',')[0]
        IND1 = int(IT1)
        IND2 = BillNoPrefix.split(',')[1]
        IND2 = int(IT2)
        bbb = invc3[IND1][IND2]
        print('Invoice date is :',invc3[IND1][IND2])

    elif BillNoLength == '0':
        x = 0
        for inv in newz:
            x+=1
            if inv == InvoiceDate:
                bbb = newz[x+INV_DATE_POSITION]
                break
    
    abcd = checkdate(bbb)
    invdate = abcd.strftime('%d-%b-%Y')

    testreg = find_regex(bbb)
    testtxt = bbb

    prefD1 = x+IDP1
    prefD2 = x+IDP2
    suffD1 = x+IDS1
    suffD2 = x+IDS2


    if testreg == InvoiceDateRegex:
        T2+=25

    zz = re.search(testreg,testtxt)

    if len(zz.group()) == literal_eval(InvoiceDateLength):
        T2+=25

    if InvoiceDatePrefix == " ".join(str(i) for i in newz[prefD1:prefD2]):
        T2+=25

    if InvoiceDateSuffix == " ".join(str(i) for i in newz[suffD1:suffD2]):
        T2+=25

    print(f'Invoice Date is: {bbb}, with confidence level of {T2}%') 

    if PNRNo == '-' and BillNoSuffix == '0':
        ccc = ''
        print('No PNR')

    elif BillNoSuffix == '1':
        PNR1 = BillDate.split(',')[0]
        PNR1 = int(PNR1)
        #print('PNR1',PNR1)
        PNR2 = BillDate.split(',')[1]
        PNR2 = int(PNR2)
        #print('PNR2',PNR2)
        ccc = invc3[PNR1][PNR2]
        print('PNR Number is :',invc3[PNR1][PNR2])

    elif PNRNo != '-' and BillNoSuffix == '0':

        PNR_NO_POSITION = PNRNumberPosition
        PNR_NO_POSITION = int(PNR_NO_POSITION)
        
        PP1 = PNRNoprefixposition.split(',')[0]
        PP1 = int(PP1)
        PP2 = PNRNoprefixposition.split(',')[1]
        PP2 = int(PP2)

        PS1 = PNRsuffixposition.split(',')[0]
        PS1 = int(PS1)
        PS2 = PNRsuffixposition.split(',')[1]
        PS2 = int(PS2)

        y = 0
        for inv in newz:
            y+=1
            if inv == PNRNo:
                ccc = newz[y+PNR_NO_POSITION]
                break

        prefPNR1 = y+PP1
        prefPNR2 = y+PP2
        suffPNR1 = y+PS1
        suffPNR2 = y+PS2         
        
        testreg = find_regex(ccc)
        testtxt = ccc

        zz = re.search(testreg,testtxt)

        # PNRNoLength = int(PNRNoLength)
        if len(zz.group()) == literal_eval(PNRNoLength):
            T3+=33.33
            print('whats this'," ".join(str(i) for i in newz[prefPNR1:prefPNR2]))
            print('then whats this'," ".join(str(i) for i in newz[suffPNR1:suffPNR2]))

        if PNRNoPrefix == " ".join(str(i) for i in newz[prefPNR1:prefPNR2]):
            T3+=33.33

        if PNRNoSuffix == " ".join(str(i) for i in newz[suffPNR1:suffPNR2]):
            T3+=33.34

        print(f'PNR Number is: {ccc}, with confidence level of {T3}%') 

    if PassengerName == '-' and BillDateRegex == '0':
        fpname = ''
        print('no passenger name')
    
    elif BillDateRegex == '1':
        PN1 = BillDateLength.split(',')[0]
        PN1 = int(PN1)
        #print('PN1',PN1)
        PN2 = BillDateLength.split(',')[1]
        PN2 = int(PN2)
        #print('PN2',PN2)
        fpname = invc3[PN1][PN2]
        print(fpname)
    elif PassengerName != '-' and  BillDateRegex == '0':

        PNP1 = PassengerNamepreffixposition.split(',')[0]
        PNP1 = int(PNP1)
        PNP2 = PassengerNamepreffixposition.split(',')[1]
        PNP2 = int(PNP2)


        PNS1 = PassengerNamesuffixposition.split(',')[0]
        PNS1 = int(PNS1)
        PNS2 = PassengerNamesuffixposition.split(',')[1]
        PNS2 = int(PNS2)

        a = 0
        for inv in newz:
            a+=1
            if inv == PassengerName:
                ddd = newz[a:]
                name1 = 0
                yyy = []
                for aa in ddd:
                    if ddd[name1] == PassengerName2:
                        cc = name1
                    name1+=1
                break                            

        prefPNAME1 = a+PNP1
        prefPNAME2 = a+PNP2
        suffPNAME1 = a+PNS1
        suffPNAME2 = a+PNS2

        if PassengerNamePrefix == " ".join(str(i) for i in newz[prefPNAME1:prefPNAME2]):
            T4+=100
        fpname = " ".join(str(i) for i in ddd[:cc] )
        print(fpname)
        print(f'''Passenger Name is: { " ".join(str(i) for i in ddd[:cc] )},with confidence level of {T4}%''') 

    if BillDatePrefix == '1':
        SF1 = BillDateSuffix.split(',')[0]
        SF1 = int(SF1)
        #print('PN1',PN1)
        SF2 = BillDateSuffix.split(',')[1]
        SF2 = int(SF2)
        #print('PN2',PN2)
        fsectorfrom = invc3[SF1][SF2]
        print(fsectorfrom)

    elif SectorFrom != '-' and BillDatePrefix == '0':

        SECTOR_FROM_POSITION = SectorfromPosition
        SECTOR_FROM_POSITION = int(SECTOR_FROM_POSITION)

        SFP1 = Sectorfromsuffixposition.split(',')[0]
        SFP1 = int(SFP1)
        SFP2 = Sectorfromsuffixposition.split(',')[1]
        SFP2 = int(SFP2)

        SFS1 = Sectorfrompreffixposition.split(',')[0]
        SFS1 = int(SFS1)
        SFS2 = Sectorfrompreffixposition.split(',')[1]
        SFS2 = int(SFS2)
        c = 0
        for inv in newz:
            c+=1
            if inv == SectorFrom:
                fff = newz[c+SECTOR_FROM_POSITION]
                break

        if SectorFromSuffix == " ".join(str(i) for i in  newz[c+SFP1:c+SFP2]):
            T5+=50
            print(1)
        
        if SectorFromPrefix == " ".join(str(i) for i in  newz[c+SFS1:c+SFS2]):
            T5+=50
            print(2)
        fsectorfrom = fff
        print(f'Sector From: {fff}, with confidence level of {T5}%') 

    elif SectorFrom == '-' and BillDatePrefix == '0':
        fsectorfrom = ''
        print('No Sector from')

    print('\n')

    if BillPeriod == '1':
        ST1 = BillPeriodPrefix.split(',')[0]
        ST1 = int(ST1)
        #print('PN1',PN1)
        ST2 = BillPeriodPrefix.split(',')[1]
        ST2 = int(ST2)
        #print('PN2',PN2)
        fsectorto = invc3[ST1][ST2]
        print(fsectorto)

    elif SectorTo != '-' and  BillPeriod == '0':

        SECTOR_TO_POSITION = SectortoPosition
        SECTOR_TO_POSITION = int(SECTOR_TO_POSITION)

        STS1 = Sectortopreffixposition.split(',')[0]
        STS1 = int(STS1)
        STS2 = Sectortopreffixposition.split(',')[1]
        STS2 = int(STS2)

        STP1 = Sectortosuffixposition.split(',')[0]
        STP1 = int(STP1)
        STP2 = Sectortosuffixposition.split(',')[1]
        STP2 = int(STP2)

        c = 0
        for inv in newz:
            c+=1
            if inv == SectorTo:
                fff = newz[c+SECTOR_TO_POSITION]
                break

        if SectorToPrefix == " ".join(str(i) for i in  newz[c+STS1:c+STS2]):
            T6+=50
            print(1)
        
        if SectorToSuffix == " ".join(str(i) for i in  newz[c+STP1:c+STP2]):
            T6+=50
            print(2)
        fsectorto = fff
        print(f'Sector To: {fff}, with confidence level of {T6}%') 

    elif SectorTo == '-' and BillPeriod == '0':
        fsectorto = ''
        print('No Sector To')

    print('\n')

    CCGST = 0
    SSGST = 0
    IIGST = 0
               
    if GSTListNo == '0' and CGSTPrefix == '-' and   IGSTPrefix == '-': #needs review
    # if GSTListNo == '-':  
        print('No GST')
    
    elif 'TATA SIA Airlines Limited' in forgst:
        CCGST = invc3[17][1]
        SSGST = invc3[19][1]
        IIGST = invc3[21][1]

    else:
        GST_LIST_VALUE = GSTListNo
        GST_LIST_VALUE = int(GST_LIST_VALUE)
    # GST_LIST_VALUE = literal_eval(GST_LIST_VALUE)
        if CGSTPrefix in invc2[GST_LIST_VALUE]:
            d = 0
            for inv in invc2[GST_LIST_VALUE]:
                d+=1
                if inv == CGSTPrefix:
                    ggg = invc2[GST_LIST_VALUE][d]
                    CCGST = ggg.replace(',','')
                    # CCGST = aaa.replace(':','')
                    SSGST = ggg.replace(',','')
                    print('No IGST in Invoice')
                    print(CCGST,SSGST)
                    break

        elif IGSTPrefix in invc2[GST_LIST_VALUE]:
            d = 0
            for inv in invc2[GST_LIST_VALUE]:
                d+=1
                if inv == IGSTPrefix:
                    ggg = invc2[GST_LIST_VALUE][d]
                    IIGST = ggg.replace(',','')
                    print(IIGST)
                    print('No SGST in Invoice')
                    print('No CGST in Invoice')
                    break

    print('\n')
    try:

        if (TaxableValue == NonTaxableValue and InvoiceAmount == '-' ):
            IA1 = TaxableValue.split(',')[0]
            IA1 = int(IA1)
            IA2 = TaxableValue.split(',')[1]
            IA2 = int(IA2)

            if '\n' in invc2[IA1][IA2]:
                Invoice_Amount = float(invc2[IA1][IA2].split('\n')[0])+ float(invc2[IA1][IA2].split('\n')[1])
                # Invoice_Amount = Invoice_Amount.replace(',','')
                print('Invoice Amount is:',Invoice_Amount)

        elif (TaxableValue == NonTaxableValue =='-'):
            IA1 = InvoiceAmount.split(',')[0]
            IA1 = int(IA1)
            IA2 = InvoiceAmount.split(',')[1]
            IA2 = int(IA2)
            Invoice_Amount = invc2[IA1][IA2]

        elif (TaxableValue != NonTaxableValue and InvoiceAmount =='-'):
            IA1 = TaxableValue.split(',')[0]
            IA1 = int(IA1)
            IA2 = TaxableValue.split(',')[1]
            IA2 = int(IA2)
            IA3 = NonTaxableValue.split(',')[0]
            IA3 = int(IA3)
            IA4 = NonTaxableValue.split(',')[1]
            IA4 = int(IA4)
            qwr = invc2[IA1][IA2].replace(',','')
            qwr = float(qwr)
            
            qwr1 = invc2[IA3][IA4].replace(',','')
            qwr1 = float(qwr1)
            
            Invoice_Amount = qwr+ qwr1
            print('Invoice Amount is:',Invoice_Amount)
        
        # return Invoice_Amount
        Invoice_Amount_str = str(Invoice_Amount)
        Invoice_Amount_str = Invoice_Amount_str.replace(',','')    
        # return(Invoice_Amount)

        fTotal = invc2[IT1][IT2]
        fTotal_str = str(fTotal)
        fTotal_str = fTotal_str.replace(',','')
        # print(fTotal_str)
    except IndexError as invind:
        Invoice_Amount_str = ''
        fTotal_str = ''
    print(Invoice_Amount_str)

    fhsncode = 0

    if HSNCode == '-':
        fhsncode = ''
        print('No HSN Code')
    else:
        HSN1 = HSNCode.split(',')[0]
        HSN1 = int(HSN1)
        HSN2 = HSNCode.split(',')[1]
        HSN2 = int(HSN2)
        fhsncode = invc2[HSN1][HSN2]

    data = [
        {
            "AttributeName": "Vendor Name",
            "AttributeInternalName": "VendorName",
            "AttributeType": "Text",
            "AttributeValue": VendorName,
            "AttributeAccuracy": 100
        },
        {
            "AttributeName": "GSTIN",
            "AttributeInternalName": "GSTIN",
            "AttributeType": "Text",
            "AttributeValue": vgst,
            "AttributeAccuracy": 100
        },
        {
            "AttributeName": "Invoice Number",
            "AttributeInternalName": "InvoiceNo",
            "AttributeType": "Text",
            "AttributeValue": finvno,
            "AttributeAccuracy": T1
        },
        {
            "AttributeName": "Invoice Date",
            "AttributeInternalName": "InvoiceDate",
            "AttributeType": "Date",
            "AttributeValue": invdate,
            "AttributeAccuracy": T2
        },
        {
            "AttributeName": "PNR Number",
            "AttributeInternalName": "PNRNo",
            "AttributeType": "Text",
            "AttributeValue": ccc,
            "AttributeAccuracy": T3
        },
        {
            "AttributeName": "Passenger Name",
            "AttributeInternalName": "PassengerName",
            "AttributeType": "Text",
            "AttributeValue": fpname,
            "AttributeAccuracy": T4
        },
        {
            "AttributeName": "Sector From",
            "AttributeInternalName": "SectorFrom",
            "AttributeType": "Text",
            "AttributeValue": fsectorfrom,
            "AttributeAccuracy": T5
        },
        {
            "AttributeName": "Sector To",
            "AttributeInternalName": "SectorTo",
            "AttributeType": "Text",
            "AttributeValue": fsectorto,
            "AttributeAccuracy": T6
        },
        {
            "AttributeName": "CGST",
            "AttributeInternalName": "CGST",
            "AttributeType": "Text",
            "AttributeValue": CCGST,
            "AttributeAccuracy": ''
        },
        {
            "AttributeName": "SGST",
            "AttributeInternalName": "SGST",
            "AttributeType": "Text",
            "AttributeValue": SSGST,
            "AttributeAccuracy": ''
        },
        {
            "AttributeName": "IGST",
            "AttributeInternalName": "IGST",
            "AttributeType": "Text",
            "AttributeValue": IIGST,
            "AttributeAccuracy": ''
        },
        {
            "AttributeName": "Invoice Amount",
            "AttributeInternalName": "InvoiceAmount",
            "AttributeType": "Text",
            "AttributeValue": Invoice_Amount_str,
            "AttributeAccuracy": 100
        },
        {
            "AttributeName": "Total Amount",
            "AttributeInternalName": "TotalAmount",
            "AttributeType": "Text",
            "AttributeValue": fTotal_str,
            "AttributeAccuracy": 100
        },
        {
            "AttributeName": "HSN Code",
            "AttributeInternalName": "HSNCode",
            "AttributeType": "Text",
            "AttributeValue": fhsncode,
            "AttributeAccuracy": 100
        }
        ]

    jstring = json.dumps(data,indent=4)
    p0.close()
    return(jstring)
