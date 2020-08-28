# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 09:48:58 2020

@author: christian.ramirez
Script requires that CDE_webscrape_Class project is in the same DIR
"""
import os

import pandas as pd

projectWD = os.getcwd()
print(f'Project WD is {projectWD}')
os.chdir(projectWD)
from CDE_webscrape_Class import CDE_WebScrapeSelenium, ReportNames
from TableStack import tableStack, unstagedReportsDic, loadCsvData, overallStack
from StageTableProcessing import prestagetable, StageTable, stagetablemelt
import cowsay

# projectWD='C:/Users/christian.ramirez/OneDrive - Green Dot Public Schools/Desktop/BitBucket_Repo/Phase2_Repo/phase2'
projectWD = os.getcwd()
path_Output = os.path.join(projectWD, 'ReportOutput')
if os.path.exists(path_Output):
    print(f'path {path_Output} exists')
else:
    print(f'Creating Path: {path_Output}')
    os.mkdir(path_Output)
# from CDE_webscrape_Class import ReportNames.SchoolYear_CDE as sy
raceMapping_raw = pd.read_csv(os.path.join(projectWD, 'Resources', 'RaceMapping.txt'), sep='\t')
raceMappingCA = raceMapping_raw[raceMapping_raw.Region == 'CA']
raceMappingCA.reset_index(drop=True, inplace=True)

# importing Report variables from the class
reports = ReportNames()
SchoolYear_CDE = reports.SchoolYear_CDE
susReport = reports.availableReports['suspensionReports']
dataReportTypes = reports.dataTypeOptions
# compSchools=pd.read_csv(os.path.join(projectWD,'Resources','CompSchoolAltSchoolID.txt'),sep='\t')
CDE_School_List = pd.read_csv(os.path.join(projectWD, 'Resources', 'CDE_SchoolScrapeList.txt'), sep='\t')
##Tests
# CDE_School_List=CDE_School_List[19:20]
# SchoolYear_CDE=SchoolYear_CDE[0:2]
#############################################
# locally defined method to Scrape data.
# CDSList must be a list,
# SchoolYear_CDE can be a string or a  list. there is a test to convert it back into a list.
# susReport must be a list
# repType must be a text string

ReportSubgroupsFilters = reports.availableSubgroups


def dirCreate(dir):
    try:
        if os.path.isdir(dir):
            print(f'Dir Exists: {dir}')
            pass
        else:
            os.mkdir(dir)
    except:
        cowsay.ghostbusters(f'{dir} is not an acceptable directory')


def suspensionDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE, susReport=susReport,
                       repType=dataReportTypes[0]):
    suspension = CDE_WebScrapeSelenium()
    suspension.setup_method_docker()
    if type(SchoolYear_CDE) != list:
        SchoolYear_CDE = [SchoolYear_CDE]
    Stack = {}
    try:
        for sy in SchoolYear_CDE:
            for cds in CDSList:
                for rep in susReport:
                    for subGroup in ReportSubgroupsFilters:
                        if repType == 'programSubgroup':
                            temp = suspension.scrapeSuspension(SchoolYear_CDE=sy, SchoolCDS=cds, susRep=rep,
                                                               dataTypeOptions=repType, reportFilter=subGroup)
                            if temp != None:
                                cowsay.daemon(f'Creating Error Log record for {temp}')
                                with open('Fail_log.txt', 'a') as fl:
                                    fl.write(f'{temp} \n')
                            # break subgroup loop to only run once
                            break
                        else:
                            temp = suspension.scrapeSuspension(SchoolYear_CDE=sy, SchoolCDS=cds, susRep=rep,
                                                               dataTypeOptions=repType, reportFilter=subGroup)
                            if temp != None:
                                cowsay.daemon(f'Creating Error Log record for {temp}')
                                with open('Fail_log.txt', 'a') as fl:
                                    fl.write(f'{temp} \n')
        suspension.teardown_method()
        return Stack
    except Exception as ex:
        cowsay.tux('Error!!!!')
        print(f'***GOT THE FOLLOWING ERROR: {ex}***')
        print('Error in suspensionDataLoop function')


def chronAbsDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE, repType=dataReportTypes[0]):
    chronAbs = CDE_WebScrapeSelenium()
    chronAbs.setup_method_docker()
    if type(SchoolYear_CDE) != list:
        SchoolYear_CDE = [SchoolYear_CDE]
    Stack = {}
    try:
        for sy in SchoolYear_CDE:
            for cds in CDSList:
                for subGroup in ReportSubgroupsFilters:
                    if repType == 'programSubgroup':
                        temp = chronAbs.scrapeChronAbs(SchoolYear_CDE=sy, SchoolCDS=cds, dataTypeOptions=repType,
                                                       reportFilter='All Students')
                        if temp != None:
                            cowsay.daemon(f'Creating Error Log record for {temp}')
                            with open('Fail_log.txt', 'a') as fl:
                                fl.write(f'{temp} \n')
                        # break subgroup loop to only run once
                        break
                    else:
                        temp = chronAbs.scrapeChronAbs(SchoolYear_CDE=sy, SchoolCDS=cds, dataTypeOptions=repType,
                                                       reportFilter=subGroup)
                        if temp != None:
                            cowsay.daemon(f'Creating Error Log record for {temp}')
                            with open('Fail_log.txt', 'a') as fl:
                                fl.write(f'{temp} \n')
        chronAbs.teardown_method()
    except Exception as ex:
        cowsay.tux("Error!!!")
        print(f'***GOT THE FOLLOWING ERROR When running chronAbsDataLoop: {ex}***')
        print('Error in chronAbsDataLoop function Returnin None ')


# locally defined method to stack data. It takes in a data dictionary that is the output of the suspensionDataLoop method
def StackTables(DataDictionary):
    FinalDataTables = []
    for j in range(0, len(DataDictionary[list(DataDictionary.keys())[0]])):
        stackDoc = []
        for d in DataDictionary:
            DataDictionary[d][j]['DataID'] = d
            stackDoc.append(DataDictionary[d][j])
        FinalDataTables.append(pd.concat(stackDoc))
    for i in range(0, len(FinalDataTables)):
        FinalDataTables[i].reset_index(drop=True, inplace=True)
    return FinalDataTables


def startSusProcess():
    # Start of Suspension Scrape process
    print('Starting first Suspension Scrape')
    # suspension = CDE_WebScrapeSelenium()
    # suspension.setup_method_docker()
    suspensionDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE[0:3],
                       susReport=susReport[0:2], repType=dataReportTypes[0])
    print('Starting Second Suspension Scrape')
    suspensionDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE[0:3],
                       susReport=susReport[0:2], repType=dataReportTypes[1])
    print('Starting Suspension teardown_method()')
    # suspension.teardown_method()
    # return CompSusDataEthnicity, CompSusDatasubGroup


def startChronAbsProcess():
    print('Starting Chron Abs')
    # chronAbs = CDE_WebScrapeSelenium()
    # chronAbs.setup_method_docker()
    print('Starting Chron Abs by Ethnicity')
    chronAbsDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE[0:3],
                     repType=dataReportTypes[0])
    print('Starting Chron Abs by SubGroup')
    chronAbsDataLoop(CDSList=CDE_School_List['CDS'], SchoolYear_CDE=SchoolYear_CDE[0:3],
                     repType=dataReportTypes[1])
    # return ChronAbsEth, ChronAbsSubgroup
    # chronAbs.teardown_method()


if __name__ == '__main__':
    # Compatability for Windows
    # if sys.platform=='linux':
    #     suspension.setup_method_docker()
    # else:
    #     while True:
    #         response=input("Do you want to use Docker? input y/n (Default is N)")
    #         response=str(response)
    #         if response.lower() == 'y':
    #             suspension.setup_method_docker()
    #             break
    #         else:
    #             suspension.setup_method()
    #             break

    # Start of ChronAbs Scrape process

    startSusProcess()
    startChronAbsProcess()

    # this takes all of the files in the ./ReportOutput Dir and stacks them based on Folder names. The value returns a Dic with the name of the table and the path to the file as the Key value pair.
    unstagedReports = tableStack()
    # this takes the data dic that was generated above, and reads the files into the Dic.
    ReportsDic = unstagedReportsDic(unstagedReports)

    # preData = loadCsvData()
    finalData = prestagetable(ReportsDic)
    stagedData = StageTable(finalData)
    OutputFinalDir = os.path.join(projectWD, 'ReportOutputFinal')
    dirCreate(OutputFinalDir)
    tempStack=overallStack(stagedData)
    tempStackMelt=stagetablemelt(tempStack)
    tempStack.to_csv(os.path.join(OutputFinalDir, 'FinalStaged.csv'),index=False)
    tempStackMelt.to_csv(os.path.join(OutputFinalDir, 'FinalStagedMelt.csv'), index=False)
    for i in stagedData:
        filename = os.path.join(OutputFinalDir, f'{i}_Staged.csv')
        stagedData[i].to_csv(filename,index=False)