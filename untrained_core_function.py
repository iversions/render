import logging
import os
import glob
import pdfplumber
from pathlib import Path
from urllib.error import HTTPError
import shutil
import pathlib
from core_function import corefc
import configparser
from datetime import datetime
from checkdt import checkdate
import datetime
import re
import json
import sys
import time
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.client_request_exception import ClientRequestException
from ast import literal_eval
from string import ascii_lowercase
from itertools import groupby
import pyodbc

config_obj = configparser.ConfigParser()
config_obj.read('/home/shashi/Documents/WorkingFolder/venv/afcons/configfile/configfile.ini')
dbparam = config_obj['mssql']
fol_loc = config_obj['folder_path']
badchar = config_obj['bad_char']
sppaths = config_obj['spdl_path']
spparam = config_obj['spdoclib']
sprlpath = config_obj['sp_relative_path']

spsite = spparam['rootsite']
spdoclib = spparam['site_url']
spusername = spparam['uname']
sppassword = spparam['upass']
cid = spparam['cid']
cs = spparam['cs']

server = dbparam['server']
database = dbparam['database']
username = dbparam['username']
password = dbparam['password']

sproot = sppaths['root']
sptrained = sppaths['trained']
spuntrained = sppaths['untrained']
spprocessed = sppaths['processed']

dirpath = fol_loc['root']
untrained = fol_loc['untrained']
trained = fol_loc['trained']
processed = fol_loc['processed']
lsppath = fol_loc['spdl']

sprptrain = sprlpath['trained']
sprpuntrain = sprlpath['untrained']
sprppro = sprlpath['processed']

# ctx = ClientContext(spdoclib).with_user_credentials(spusername,sppassword)
ctx = ClientContext(spdoclib).with_credentials(ClientCredential(cid, cs))

root_folder = ctx.web.get_folder_by_server_relative_path(sproot)
train_folder = ctx.web.get_folder_by_server_relative_path(sptrained)
untrain_folder = ctx.web.get_folder_by_server_relative_path(spuntrained)
pro_folder = ctx.web.get_folder_by_server_relative_path(spprocessed)


logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

def untrained(rowid,retrain,IsApproved):
    try:
        ffiles = glob.glob(lsppath+'/'+'*')
        for f in ffiles:
            os.remove(f)

        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
        cursor = conn.cursor()
        
        cursor.execute("""SELECT * FROM dbo.RequestDetails WHERE Id = ?""",(rowid,))
        rdata = cursor.fetchall()    
        rowdata = rdata[0]

        Id,RequestNo,InvoiceTypeId,RequestStatusId,TrainingStatusId,DocumentUrl,\
            AdditionalDetails,PromoteField,IsActive,CreatedBy,CreatedDateUtc,\
                ModifiedBy,ModifiedDateUtc,isMailSent,isSapProcessed,Document,DocLibraryId = rowdata
        conn.close()
        ffile_name = os.path.dirname(DocumentUrl)
        filelen=len(ffile_name)
        newlink = DocumentUrl[64:filelen]
        jsdata = json.loads(AdditionalDetails)
        for i in jsdata:
            if i['AttributeInternalName'] == 'VendorName':
                jsvname = i['AttributeValue']
            elif i['AttributeInternalName'] == 'GSTIN':
                jsgstin = i['AttributeValue']
            elif i['AttributeInternalName'] == 'InvoiceNo':
                jsinvno = i['AttributeValue']
            elif i['AttributeInternalName'] == 'InvoiceDate':
                jsinvdate = i['AttributeValue']
            elif i['AttributeInternalName'] == 'PNRNo':
                jspnr = i['AttributeValue']
            elif i['AttributeInternalName'] == 'PassengerName':
                jspname = i['AttributeValue']
            elif i['AttributeInternalName'] == 'SectorFrom':
                jssf = i['AttributeValue']
            elif i['AttributeInternalName'] == 'SectorTo':
                jsst = i['AttributeValue']
            elif i['AttributeInternalName'] == 'CGST':
                jscgst = i['AttributeValue']
            elif i['AttributeInternalName'] == 'SGST':
                jssgst = i['AttributeValue']
            elif i['AttributeInternalName'] == 'IGST':
                jsigst = i['AttributeValue']
            elif i['AttributeInternalName'] == 'InvoiceAmount':
                jsinva = i['AttributeValue']
            elif i['AttributeInternalName'] == 'TotalAmount':
                jsinvta = i['AttributeValue']
            elif i['AttributeInternalName'] == 'HSNCode':
                jshsn = i['AttributeValue']
            elif i['AttributeInternalName'] == 'UniqueName':
                jsuname = i['AttributeValue']

        livefol = ctx.web.get_folder_by_server_relative_path(newlink)
        files = livefol.get_files(True).execute_query()

        # forshare = ''

        for f in files:
            metaurl = f.properties['ServerRelativeUrl']
            finalurl = spsite+metaurl
            file_name = os.path.basename(finalurl)
            savefile = os.path.join(lsppath, file_name)
            if '.pdf' in file_name:
                # print('pdf',file_name)
                forshare = file_name
            elif '.txt' in file_name:
                # print('txt',file_name)
                fordata = file_name

            with open(savefile,'wb') as local_file:
                p_file = ctx.web.get_file_by_server_relative_url(metaurl).download(local_file).execute_query()
        
        
        for pdf_file in glob.glob(os.path.join(lsppath, "*.pdf")):
            getfile = pdf_file
            # print(getfile)
        
        for text_file in glob.glob(os.path.join(lsppath, "*.txt")):
            gettext = text_file
            # print(gettext)

        lfname = len(forshare)
        jfname = DocumentUrl[91:-lfname-1]
        lspsite = len(spsite)
        fol_name = ffile_name[lspsite:]
        link_pro = sprppro+jfname
        link_train = sprptrain+jfname
        sourcefol = ctx.web.get_folder_by_server_relative_url(fol_name)

        page = pdfplumber.open(getfile)
        firstpage = page.pages[0]
        charst = firstpage.extract_words()
        f_ext_text = firstpage.extract_text()
        invc3 = firstpage.extract_table()
        invc2 = [[item.replace(u'\xa0', ' ') if isinstance(item, str) else item for item in items] for items in invc3]
        final_text = f_ext_text.replace('\xad','-')
        training_params = []
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
        # x=0
        # for c in z:
        #     x+=1

        nl = [item for item in z if item !=';']

        v = 0
        for x in nl:
            d = nl[v]
            v+=1

        dtdt = checkdate(jsinvdate)
        for f in ["%d %b %Y","%b %d, %Y", "%d-%b-%Y","%d-%m-%Y", "%m-%d-%Y", "%d-%b-%y","%d/%b/%Y", "%m/%d/%Y","%d-%m-%y","%d/%m/%y"]:
            if dtdt.strftime(f) in final_text:
                cleandt = dtdt.strftime(f)
                # print(dtdt.strftime(f))
                break

        InvoiceNumber = jsinvno
        InvoiceDate = cleandt
        PNRno = jspnr
        PassName = jspname
        Sfrom = jssf
        Sto = jsst
        Cgst = jscgst
        Sgst = jssgst
        Igst = jsigst
        subtotal = jsinva
        Total_ = jsinvta
        HSN = jshsn

        w = 0
        for inv in newz:
            w+=1
            if inv == InvoiceNumber:
                aaa = newz[w-1]
                break
        
        training_params.append(newz[w-2]) #inv position 00 
        invnoreg = find_regex(aaa)
        print(invnoreg)
        testtxt = aaa

        zz = re.search(invnoreg,testtxt)

        training_params.append('-') #inv no split 01
        training_params.append(0) #inv no position 02
        training_params.append(invnoreg) #inv no regex 03
        training_params.append(len(zz.group())) #inv no length 04
        training_params.append('-2,-1') #inv no prefix position 05
        training_params.append(" ".join(str(i) for i in newz[w-2:w-1])) #inv no prefix 06
        training_params.append('0,1') #inv no suffix position 07 
        training_params.append(" ".join(str(i) for i in newz[w:w+1])) #inv no suffix 08

        x = 0
        for inv in newz:
            x+=1
            # pri
            if inv == InvoiceDate:
                bbb = newz[x-1]
                break

        training_params.append(newz[x-2]) #inv date 09

        invdtreg = find_regex(bbb)
        testtxt = bbb
        

        zz = re.search(invdtreg,testtxt)

        training_params.append(0) #inv date position 10
        training_params.append(invdtreg) #inv date regex 11
        training_params.append(len(zz.group())) #inv date length 12
        training_params.append((-2,-1)) #inv date prefix position 13 
        training_params.append(" ".join(str(i) for i in newz[w:w+1])) #inv date prefix 14
        training_params.append((0,1)) #inv date suffix position 15
        training_params.append(" ".join(str(i) for i in newz[w:w+1])) #inv date suffix 16

        if PNRno == '-':
            training_params.append('-') #17
            training_params.append('-') #18
            training_params.append('-') #19
            training_params.append('-') #20
            training_params.append('-') #21
            training_params.append('-') #22
            training_params.append('-') #23
            # print('No PNR Number')

        elif PNRno != '-':
            y = 0
            for inv in newz:
                y+=1
                if inv == PNRno:
                    ccc = newz[y-1]
                    break       

            training_params.append(newz[y-2]) #pnr no 17
            training_params.append(0) #pnr no position 18      
            testreg = find_regex(ccc)
            testtxt = ccc
            zz = re.search(testreg,testtxt)
            training_params.append(len(zz.group())) #pnr length 19
            training_params.append((-2,-1)) #pnr no prefix position 20
            training_params.append(" ".join(str(i) for i in newz[y-2:y-1])) #pnr no prefix 21
            training_params.append((0,2)) #pnr no suffix position 22
            training_params.append(" ".join(str(i) for i in newz[y:y+2])) #pnr no suffix 23


        if PassName == '-':
            training_params.append('-') #pass name 24
            training_params.append('-') #pass name position 25
            training_params.append('-') #pass name 2 26
            training_params.append('-') #pass name prefix position 27
            training_params.append('-') #pass name prefix 28
            training_params.append('-') #pass name suffix position 29
            training_params.append('-') #pass name suffix 30
            # print('No Passanger Name')
        elif PassName!='-':
            pass1 = PassName.split(' ')[0]
            pass2 = PassName.split(' ')[-1]

            vv = 0
            for cv in newz:
                if newz[vv] == pass2:
                    break
                vv+=1
                
            uu = 0
            for cv in newz:
                if newz[uu] == pass1:
                    break
                uu+=1
    
            e = 0
            for w in newz:
                if  newz[e] == newz[uu-1]:
                    aaa = newz[e+1:]
                    # print(z[e],'      ', aaa)
                    name1 = 0
                    yyy = []
                    for aa in aaa:
                        if aaa[name1] == newz[vv+1] :
                            cc = name1
                            # print('cc is',cc)
                            # print('Employee Name is :', " ".join(str(i) for i in aaa[:cc]))  
                        name1+=1
                    break
                if (e+2)<= len(newz):
                    e+=1

            training_params.append(newz[uu-1]) #passenger name 24
            training_params.append('-') #name position 25
            training_params.append(newz[vv+1]) #passenger name 2 26
            training_params.append((-1,0)) #preffix position 27
            training_params.append(" ".join(str(i) for i in newz[uu-1:uu])) #preffix 28
            training_params.append((1,2)) #suffix position 29
            training_params.append(" ".join(str(i) for i in newz[vv+1:vv+2]))#suffix 30

        if Sfrom == '-':
            training_params.append('-') #31
            training_params.append('-') #32
            training_params.append('-') #33
            training_params.append('-') #34
            training_params.append('-') #35
            training_params.append('-') #36
            # print('No Sector')
        elif Sfrom != '-':
            c = 0
            for inv in newz:
                c+=1
                if inv == Sfrom:
                    fff = newz[c-1]
                    break

            training_params.append(newz[c-2]) #sector from 31
            training_params.append(0) #sector from position 32 
            training_params.append((0,1)) #sector from suffix position 33
            training_params.append(" ".join(str(i) for i in newz[c:c+1])) #sector from suffix 34 
            training_params.append((-2,-1)) #sector from prefix position 35 
            training_params.append(" ".join(str(i) for i in newz[c-2:c-1])) #sector from prefix 36

        if Sto == '-':
            training_params.append('-') #37
            training_params.append('-') #38
            training_params.append('-') #39
            training_params.append('-') #40
            training_params.append('-') #41
            training_params.append('-') #42
            # print('No Sector')

        elif Sto != '-':
            d = 0
            for inv in newz:
                d+=1
                if inv == Sto:
                    ggg = newz[d-1]
                    break

            training_params.append(newz[d-2]) #sector to 37
            training_params.append(0) #sector to position 38
            training_params.append((-2,-1)) #sector to prefix position 39
            training_params.append(" ".join(str(i) for i in newz[d-2:d-1])) #sector to prefix 40
            training_params.append((0,2)) #sector to suffix position 41
            training_params.append(" ".join(str(i) for i in newz[d:d+2])) #sector to suffix 42

        h = 0
        j = 0
        k = 0
        for i in range(len(invc2)):
            r = 0
            for j in invc2[h]:
                if subtotal == invc2[h][r]:
                    j,k = h,r
                    break
                r+=1
            if k==0:
                h+=1
            else:
                break
        # print('sub',j,k)
        # print(invc3[j][k])
        training_params.append('-') #taxable value 43
        training_params.append('-') #non taxable value 44
        training_params.append((j,k)) #invoice amount 45

        if Cgst != '-' :
            q = 0
            x = 0
            y = 0
            # print(1)
            for i in range(len(invc2)):
                r = 0
                for j in invc2[q]:
                    if Cgst == invc2[q][r]:
                        x,y = q,r
                        break
                    r+=1
                if y==0:
                    q+=1
                else:
                    break
            # print('cgst position:',x,y)
            training_params.append(invc2[x][y-1]) #46
            training_params.append(invc2[x][y-1]) #47
            training_params.append(invc2[x][y-1]) #48
            training_params.append(invc2[x][y-1]) #49
            training_params.append('-') #50
            training_params.append('-') #51
            training_params.append(x) #52

        elif Igst != '-' :    
            q = 0
            x = 0
            y = 0
            for i in range(len(invc2)):
                r = 0
                for j in invc2[q]:
                    if Igst == invc2[q][r]:
                        x,y = q,r
                        # print('CGST position is:',x,y)
                        # print('CGST % is:',invc3[x][y-1])
                        break
                    r+=1
                if y==0:
                    q+=1
                else:
                    break
                print('\n')
            # print('Igst position:',x,y)
            training_params.append('-')
            training_params.append('-')
            training_params.append('-')
            training_params.append('-')
            training_params.append(invc2[x][y-1])
            training_params.append(invc2[x][y-1])
            training_params.append(x)
        
        z = 0
        a = 0
        b = 0
        for i in range(len(invc2)):
            r = 0
            for j in invc2[z]:
                if Total_ == invc2[z][r]:
                    a,b = z,r
                    break
                r+=1
            z+=1

        training_params.append((a,b)) #Total 53

        if HSN == '-':
            training_params.append('-')
            # print('No HSN')
        elif HSN != '-':
            q = 0
            x = 0
            y = 0
            for i in range(len(invc2)):
                r = 0
                for j in invc2[q]:
                    if HSN == invc2[q][r]:
                        x,y = q,r
                        break
                    r+=1
                if y==0:
                    q+=1
                else:
                    break

            training_params.append((x,y))


        bchar = ['(',')']

        VendorName = jsvname
        VendorGSTIN = jsgstin
        InvoiceNumber = training_params[0]
        InvoiceNoRegex = training_params[3]
        InvoiceNoLength = training_params[4]
        InvoiceNoPrefix = training_params[6]
        InvoiceNoSuffix = training_params[8]
        InvoiceDate = training_params[9]
        InvoiceDateRegex = training_params[11]
        InvoiceDateLength = training_params[12]
        InvoiceDatePrefix = training_params[14]
        InvoiceDateSuffix = training_params[16]
        PNRNo = training_params[17]
        PNRNoLength = training_params[19]
        PNRNoSuffix = training_params[23]
        PNRNoPrefix = training_params[21]
        PassengerName = training_params[24]
        PassengerNameSuffix = training_params[30]
        PassengerNamePrefix = training_params[28]
        SectorFrom = training_params[31]
        SectorFromSuffix = training_params[34]
        SectorFromPrefix = training_params[36]
        SectorTo = training_params[37]
        SectorToSuffix = training_params[42]
        SectorToPrefix = training_params[40]
        TaxableValue = training_params[43]
        NonTaxableValue = training_params[44]
        CGST = training_params[46]
        CGSTPrefix = training_params[47]
        SGST = training_params[48]
        SGSTPrefix = training_params[49]
        IGST = training_params[50]
        IGSTPrefix = training_params[51]
        Total = str(training_params[53])
        eTotal = Total.replace('(','')
        eeTotal = eTotal.replace(')','')
        # if HSNCode == '-':
        #     pass
        # elif HSNCode != '-':
        HSNCode = str(training_params[54])
        eHSN = HSNCode.replace('(','')
        eeHSN = eHSN.replace(')','')
        IsActive = True
        CreatedBy =''
        CreatedDateUtc =''
        ModifiedBy =''
        ModifiedDateUtc =''
        PassengerName1 =''
        PassengerName2 = training_params[26]
        SenderEmailID =''
        EmployeeCode =''
        EmployeeName =''
        ProviderName =''
        PhoneNumberefix =''
        PhoneNumber =''
        SubscribersName1 =''
        SubscribersName2 =''
        SubscribersNamePrefix =''
        BillNumber =''
        BillNoRegex =''
        BillNoLength =''
        BillNoPrefix =''
        BillNoSuffix =''
        BillDate =''
        BillDateRegex =''
        BillDateLength =''
        BillDatePrefix =''
        BillDateSuffix =''
        BillPeriod =''
        BillPeriodPrefix =''
        BillPeriodsuffix =''
        BillAmount =''
        T_CGST =''
        T_CGSTPrefix =''
        T_SGST =''
        T_SGSTPrefix =''
        T_IGST =''
        T_IGSTPrefix =''
        T_Total =''
        InvoiceNumberSplit = training_params[1]
        cccInvoiceNumberPosition = training_params[2]
        InvoiceNoprefixposition = training_params[5]
        InvoiceNosuffixposition = training_params[7]
        InvoiceDatePosition = training_params[10]
        InvoiceDateprefixposition = str(training_params[13])
        eIDPP = InvoiceDateprefixposition.replace('(','')
        eeIDPP = eIDPP.replace(')','')
        InvoiceDatesuffixposition = str(training_params[15])
        eIDSP = InvoiceDatesuffixposition.replace('(','')
        eeIDSP = eIDSP.replace(')','')
        PNRNumberPosition = training_params[18]
        PNRNoprefixposition = str(training_params[20])
        ePNPP = PNRNoprefixposition.replace('(','')
        eePNPP = ePNPP.replace(')','')
        PNRsuffixposition = str(training_params[22])
        ePNSP = PNRsuffixposition.replace('(','')
        eePNSP = ePNSP.replace(')','')
        PassengerNamePosition = training_params[25]
        PassengerNamepreffixposition = str(training_params[27])
        ePANPP = PassengerNamepreffixposition.replace('(','')
        eePANPP = ePANPP.replace(')','')
        PassengerNamesuffixposition = str(training_params[29])
        ePANSP = PassengerNamesuffixposition.replace('(','')
        eePANSP = ePANSP.replace(')','')
        Sectorfromsuffixposition = str(training_params[33])
        eSFSP = Sectorfromsuffixposition.replace('(','')
        eeSFSP = eSFSP.replace(')','')
        Sectorfrompreffixposition = str(training_params[35])
        eSFPP = Sectorfrompreffixposition.replace('(','')
        eeSFPP = eSFPP.replace(')','')
        Sectortopreffixposition = str(training_params[39])
        eSTPP = Sectortopreffixposition.replace('(','')
        eeSTPP = eSTPP.replace(')','')
        Sectortosuffixposition = str(training_params[41])
        eSTSP = Sectortosuffixposition.replace('(','')
        eeSTSP = eSTSP.replace(')','')
        GSTListNo = training_params[52]
        InvoiceAmount = str(training_params[45])
        eIA = InvoiceAmount.replace('(','')
        eeIA = eIA.replace(')','')
        SectortoPosition = training_params[38]
        SectorfromPosition = training_params[32]
        pan = jsgstin[2:-3]
        gstregex = '\w{2}\w{5}\d{4}\w{4}'
        UniqueName = jsuname

        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
        cursor = conn.cursor()
        conn.execute("""INSERT INTO dbo.Training1 (VendorName,VendorGSTIN,InvoiceNumber,InvoiceNoRegex,InvoiceNoLength,InvoiceNoPrefix,InvoiceNoSuffix,InvoiceDate,InvoiceDateRegex,InvoiceDateLength,InvoiceDatePrefix,InvoiceDateSuffix,PNRNo,PNRNoLength,PNRnoSuffix,PNRNoPrefix,PassengerName,PassengerNameSuffix,PassengerNamePrefix,SectorFrom,SectorFromSuffix,SectorFromPrefix,SectorTo,SectorToSuffix,SectorToPrefix,TaxableValue,NonTaxableValue,CGST,CGSTPrefix,SGST,SGSTPrefix,IGST,IGSTPrefix,Total,HSNCode,IsActive,PassengerName2,InvoiceNumberSplit,cccInvoiceNumberPosition,InvoiceNoprefixposition,InvoiceNosuffixposition,InvoiceDatePosition,InvoiceDateprefixposition,InvoiceDatesuffixposition,PNRNumberPosition,PNRNoprefixposition,PNRsuffixposition,PassengerNamePosition,PassengerNamepreffixposition,PassengerNamesuffixposition,Sectorfromsuffixposition,Sectorfrompreffixposition,Sectortopreffixposition,Sectortosuffixposition,GSTListNo,InvoiceAmount,SectortoPosition,SectorfromPosition,pan,gstregex,UniqueName) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", VendorName,VendorGSTIN,InvoiceNumber,InvoiceNoRegex,InvoiceNoLength,InvoiceNoPrefix,InvoiceNoSuffix,InvoiceDate,InvoiceDateRegex,InvoiceDateLength,InvoiceDatePrefix,InvoiceDateSuffix,PNRNo,PNRNoLength,PNRNoSuffix,PNRNoPrefix,PassengerName,PassengerNameSuffix,PassengerNamePrefix,SectorFrom,SectorFromSuffix,SectorFromPrefix,SectorTo,SectorToSuffix,SectorToPrefix,TaxableValue,NonTaxableValue,CGST,CGSTPrefix,SGST,SGSTPrefix,IGST,IGSTPrefix,eeTotal,eeHSN,IsActive,PassengerName2,InvoiceNumberSplit,cccInvoiceNumberPosition,InvoiceNoprefixposition,InvoiceNosuffixposition,InvoiceDatePosition,eeIDPP,eeIDSP,PNRNumberPosition,eePNPP,eePNSP,PassengerNamePosition,eePANPP,eePANSP,eeSFSP,eeSFPP,eeSTPP,eeSTSP,GSTListNo,eeIA,SectortoPosition,SectorfromPosition,pan,gstregex,UniqueName)
        conn.commit()
        conn.close()
        os.remove(getfile)
        os.remove(gettext)

        conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
        cursor = conn.cursor()
        cursor.execute("""SELECT ID FROM dbo.StatusMaster WHERE SystemName=? AND IsActive = ?""",'Trained',1,)
        TStatus = cursor.fetchone()
        TrainingStatusId = TStatus[0]
        conn.close()

        if IsApproved == False:
            conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
            cursor = conn.cursor()
            cursor.execute("""SELECT ID FROM dbo.StatusMaster WHERE SystemName=? AND IsActive = ?""",'PendingReview',1,)
            RStatus = cursor.fetchone()
            RequestStatusId = RStatus[0]
            link_url = spsite+sprptrain+jfname+'/'+forshare
            cursor.execute("""UPDATE dbo.RequestDetails SET PromotedField = ?, DocumentUrl = ?, RequestStatusId = ?, TrainingStatusId = ? WHERE Id = ?""",VendorName,link_url,RequestStatusId,TrainingStatusId,rowid,)
            cursor.commit()
            conn.close()
            sourcefol.move_to(link_train).execute_query()
        elif IsApproved == True:
            conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password+';TrustServerCertificate=yes')
            cursor = conn.cursor()
            cursor.execute("""SELECT ID FROM dbo.StatusMaster WHERE SystemName=? AND IsActive = ?""",'Approved',1,)
            RStatus = cursor.fetchone()
            RequestStatusId = RStatus[0]
            link_url = spsite+sprppro+jfname+'/'+forshare
            cursor.execute("""UPDATE dbo.RequestDetails SET PromotedField = ?, DocumentUrl = ?, RequestStatusId = ?, TrainingStatusId = ? WHERE Id = ?""",VendorName,link_url,RequestStatusId,TrainingStatusId,rowid,)
            cursor.commit()
            conn.close()
            sourcefol.move_to(link_pro).execute_query()
        # xcv = 0
        # for i in training_params:
        #     print(xcv, type(training_params[xcv]))
        #     xcv+=1
        # print(PNRNoPrefix)
        # conn.close()
        return training_params
        # return {'cgst':jscgst,'sgst':jssgst,'igst':jsigst,'st':jsinva,'ttl':jsinvta,'hsn':jshsn}
    
        # Cgst = jscgst
        # Sgst = jssgst
        # Igst = jsigst
        # subtotal = jsinva
        # Total_ = jsinvta
        # HSN = jshsn
    except pyodbc.Error as p:
        raise p
        # print(p,'odbc sql error')
        pass

    except IndexError as I:
        raise I
        # print(I,'Failed to insert')
        pass

    except NameError as e:
        raise e
        # print(e,'nameerror as folder is empty')
        pass

    except HTTPError as h:
        raise h
        # print(h,'httperror due to nameerror as folder is empty')
        pass

    except ClientRequestException as c:
        raise c
        # print(c,'clienterror due to httperror as folder is empty')
        pass
    
