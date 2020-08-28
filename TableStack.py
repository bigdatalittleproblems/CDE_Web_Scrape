import sys
import os
import time
import pandas as pd
import cowsay
projectWD=os.getcwd()
import json
ReportDir=os.path.join(projectWD,'ReportOutput')
#make Directory if it does not exist.
try:
    os.mkdir(ReportDir)
except:
    pass
ReportList=os.listdir(ReportDir)

def StackTables(DataDictionary):
    stackDoc=[]
    for d in DataDictionary:
        DataDictionary[d]['DataID']=d
        stackDoc.append(DataDictionary[d])
    FinalStack=pd.concat(stackDoc,axis=0)
    return FinalStack

def tableStack():
    fileStackDic={}
    stack={}
    for i in ReportList:    
        j=os.path.join(ReportDir,i)
        if os.path.isdir(j):
            CDE_SuspensionReports=os.listdir(j)
            stack={}
            for k in CDE_SuspensionReports:
                k=str(k)
                l=os.path.join(j,k)
                temp1=pd.read_csv(l)
                stack.update({k:temp1})
            tempStack=StackTables(stack)
            fileStackName=f'{j}_Stack.csv'
            fileStackDic.update({i:fileStackName})
            tempStack.to_csv(fileStackName,index=False)
            cowsay.daemon(fileStackName)
    print(fileStackDic)
    return fileStackDic

def unstagedReportsDic(unstagedReports):
    unstagedReportsDic={}
    for i in unstagedReports:
        temp=pd.read_csv(unstagedReports[i])
        unstagedReportsDic.update({i:temp})
    return unstagedReportsDic

def loadCsvData(dir=ReportDir):
    x=os.listdir(dir)
    print(f'Step 0{x}')
    output={}
    for i in x:
        y=os.path.join(dir,i)
        if os.path.isdir(y):
            #skip Directory
            continue
        else:
            temp=pd.read_csv(y)
            print(temp)
            j=i.replace('.csv','')
            output.update({j:temp})
    return output


def overallStack(dataDic):
    for i in dataDic:
        dataDic[i]['TableID']=i
    dataOutput = pd.concat(dataDic,axis=0)
    return dataOutput


if __name__=='__main__':
    cowsay.daemon('Coolio')
    test=loadCsvData()
    for i in test:
        test[i].info()

    # x=tableStack()
    # y=unstagedReportsDic(x)
    # for i in y:
    #     cowsay.cow(i)
    #     print(y[i])
