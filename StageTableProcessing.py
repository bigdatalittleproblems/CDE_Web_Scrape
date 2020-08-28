# -*- coding: utf-8 -*-
"""
Created on Mon May 11 16:42:45 2020

@author: christian.ramirez
"""

# Libraries
import sys
import os
from typing import List

import pandas as pd
import cowsay

count_col: List[str] = ['CumulativeEnrollment', 'ChronicAbsenteeismEligibleEnrollment', 'ChronicAbsenteeismCount',
                        'TotalSuspensions', 'UnduplicatedCount ofStudentsSuspended',
                        'Percent of Students Suspended with One Suspension',
                        'Percent of Students Suspended with Multiple Suspensions']
rate_col: List[str] = ['ChronicAbsenteeismRate',
                       'SuspensionRate',
                       'Percent of Cumulative Enrollment',
                       'Percent of Students Suspended']


def prestagetable(dataDic):
    """
    Must be a Dictionry
    :param dataDic:
    :return:
    """
    tableNames = list(dataDic.keys())
    for i in tableNames:
        try:
            dropCol = [z for z in dataDic[i].columns if z.isdigit()]
            dataDic[i].drop(columns=dropCol, inplace=True)
            print(f'Dropped:{dropCol} for table {i}')
        except:
            print('Did not Drop any Columns')
        x = list(dataDic[i].columns)
        for j in x:
            if j in count_col:
                try:
                    dataDic[i][j] = pd.to_numeric(dataDic[i][j].str.strip('%*'), errors='coerce')
                except AttributeError:
                    print('{} is already numeric'.format(j))
                    pass
                except Exception as ex:
                    print(f'***GOT THE FOLLOWING ERROR: {ex}***')
                    print('Other error for {}'.format(j))
                    pass
            elif j in rate_col:
                try:
                    dataDic[i][j] = pd.to_numeric(dataDic[i][j].str.strip('%*'), errors='coerce') / 100
                except AttributeError:
                    print('{} is already numeric'.format(j))
                    pass
                except Exception as ex:
                    print(f'***GOT THE FOLLOWING ERROR: {ex}***')
                    print('Other error for {}'.format(j))
                    pass
    return dataDic


def StageTable(dataDic):
    dataDicoutput = {}
    projectWD = os.getcwd()
    path_Output = os.path.join(projectWD, 'ReportOutput')
    # Final Report Output to import into DW
    path_FinalOutput = os.path.join(path_Output, 'FinalData')

    sy_conversion = pd.read_csv(os.path.join(projectWD, 'Resources', 'SchoolYear.txt'), sep='\t')
    stagingTableCol = ['MetricID', 'School', 'SchoolID', 'GroupType', 'Subgroup', 'SchoolYear', 'DataValue']
    metricID_CA_Discipline_CDE = ['CA_Discipline_CDE_SusIncident_Cnt',
                                  'CA_Discipline_CDE_OSSIncident_Cnt',
                                  'CA_Discipline_CDE_ISSIncident_Cnt',
                                  'CA_Discipline_CDE_SusUnique_Cnt',
                                  'CA_Discipline_CDE_OSSUnique_Cnt',
                                  'CA_Discipline_CDE_ISSUnique_Cnt',
                                  'CA_Discipline_CDE_ExpUnique_Cnt']
    metricID_CA_AttMemb_CDE = ['CA_AttMemb_CDE_ChronicAbsentees_Cnt',
                               'CA_AttMemb_CDE_CumEnrollEligChronic_Cnt']
    # CDE Codes for conversion
    PHI = 19647330124024
    LGC = 19647330124016

    ColReplace = {'School Name': 'school_name', 'Student Group': 'subgroup', 'Grade Band': 'grade_band',
                  '# Students': 'n_students', '# Chronically Absent': 'n_chronically_absent',
                  '% Chronically Absent': 'pct_chronically_absent', 'School': 'school', 'District': 'system',
                  'District Name': 'system_name', 'Ethnicity': 'CDE_Subgroup', 'Subgroup': 'CDE_Subgroup'}

    GD_Subgroups = pd.read_csv(os.path.join(projectWD, 'Resources', 'GD_Subgroups.txt'), sep='\t')
    gdSchools = pd.read_csv(os.path.join(projectWD, 'Resources', 'GreenDot_CDS_Codes_final.txt'), sep='\t')
    # SusDataEthnicity_stack[1].Ethnicity.drop_duplicates()
    # rename column to prevent future conflict

    for d in dataDic:
        try:
            dataDic[d].rename(columns=ColReplace, inplace=True)
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
        try:
            if ['CDE_Subgroup'] in list(dataDic[d].columns):
                dataDic[d].dropna(subset=['CDE_Subgroup'], inplace=True)
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
        try:
            dataDic[d].reset_index(drop=True, inplace=True)
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
        try:
            dataDic[d].SchoolCDS.replace(PHI, LGC, inplace=True)
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
        try:
            dataDic[d]['CDE_Report'] = dataDic[d]['dataID'].str.split('_', expand=True)[0]
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
        try:
            dataDic.update({d: dataDic[d].merge(GD_Subgroups, left_on='CDE_Subgroup', right_on='CDE_Subgroup')})
        except Exception as ex:
            cowsay.beavis(f'got this Error:{ex}')
    for i in dataDic:
        try:
            dataDicoutput.update({i: dataDic[i].merge(sy_conversion, how='left', on='SchoolYear_CDE').merge(
                gdSchools.filter(['CDS', 'School', 'SchoolID']), left_on='SchoolCDS', right_on='CDS')})
        except:
            cowsay.daemon('Merge Failed in StageTableProcessing.StageTable function')
    return dataDicoutput


def stagetablemelt(df):
    # rename Value Columns to value
    filterout = ['Compton Unified',
                 'Inglewood Unified',
                 'Lennox',
                 'Los Angeles',
                 'Los Angeles County',
                 'Los Angeles County Office of Education',
                 'Los Angeles Unified',
                 'Statewide']
    dataCol = list(df.columns)
    idField = []
    dataField = ['ChronicAbsenteeismRate',
                 'ChronicAbsenteeismCount',
                 'CumulativeEnrollment',
                 'ChronicAbsenteeismEligibleEnrollment',
                 'TotalSuspensions',
                 'UnduplicatedCount ofStudentsSuspended',
                 'SuspensionRate',
                 'CumulativeEnrollment',
                 'Percent of Students Suspended with One Suspension',
                 'Percent of Students Suspended with Multiple Suspensions',
                 'Percent of Cumulative Enrollment',
                 'Percent of Students Suspended']
    for i in dataCol:
        if i not in dataField:
            idField.append(i)
    dataDic = []
    for i in dataField:
        print(i)
        dataDic.append(pd.melt(df, id_vars=idField, value_vars=i))
    dataDicOutput = pd.concat(dataDic)
    dataDicOutput.drop_duplicates(inplace=True)

    groupColumns = []
    for i in list(dataDicOutput.columns):
        if i not in ['HTML_Link', 'value','Name']:
            groupColumns.append(i)
    dataDicOutput=dataDicOutput[dataDicOutput['Name'].isin(filterout) == False]
    dataDicOutput = dataDicOutput[pd.notnull(dataDicOutput.value)]
    dataDicOutputFinal = dataDicOutput.fillna('NA').groupby(groupColumns, as_index=False).agg({'value': 'sum'})
    return dataDicOutputFinal

    # pd.merge(dataFinal['ChronAbsEth_Stack'], GD_Subgroups, how='left', on=['Ethnicity'])
    # dataFinalMerge = {}
    #
    #
    # calcTablesSus = {}
    # for i in ['SusDataEthnicity_stack', 'SusDatasubGroup_stack']:
    #     # Temp Vars are to have a single point to change
    #     tempCol = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment',
    #                'UnduplicatedCount ofStudentsSuspended']
    #     tempGroupBy = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup']
    #     calcTablesSus.update({i + '_Unique_Cnt': dataFinalMerge[i].filter(
    #         ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup',
    #          'UnduplicatedCount ofStudentsSuspended']).groupby(tempGroupBy, as_index=False).agg(
    #         {'UnduplicatedCount ofStudentsSuspended': 'sum'})})
    #     calcTablesSus.update({i + '_Incident_Cnt': dataFinalMerge[i].filter(
    #         ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'TotalSuspensions']).groupby(tempGroupBy,
    #                                                                                                         as_index=False).agg(
    #         {'TotalSuspensions': 'sum'})})
    #     calcTablesSus.update({i + '_CumulativeEnrollment_Cnt': dataFinalMerge[i].filter(
    #         ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment']).groupby(
    #         tempGroupBy, as_index=False).agg({'CumulativeEnrollment': 'sum'})})
    #
    # # Rename loop
    # for i in calcTablesSus:
    #     tempColName = {'UnduplicatedCount ofStudentsSuspended': 'DataValue', 'TotalSuspensions': 'DataValue',
    #                    'CumulativeEnrollment': 'DataValue'}
    #     calcTablesSus[i].rename(columns=tempColName, inplace=True)
    #
    # calcTablesChronAbs = {}
    # for i in ['ChronAbsEth_Stack', 'ChronAbsSubgroup_Stack']:
    #     # Temp Vars are to have a single point to change
    #     tempCol = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment',
    #                'UnduplicatedCount ofStudentsSuspended']
    #     tempGroupBy = ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup']
    #     calcTablesChronAbs.update({i + '_CumEnrollEligChronic_Cnt': dataFinalMerge[i].filter(
    #         ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup', 'ChronicAbsenteeismEligibleEnrollment']).groupby(
    #         tempGroupBy, as_index=False).agg({'ChronicAbsenteeismEligibleEnrollment': 'sum'})})
    #     calcTablesChronAbs.update({i + '_ChronicAbsentees_Cnt': dataFinalMerge[i].filter(
    #         ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup', 'ChronicAbsenteeismCount']).groupby(tempGroupBy,
    #                                                                                                      as_index=False).agg(
    #         {'ChronicAbsenteeismCount': 'sum'})})
    # # Rename loop
    # for i in calcTablesChronAbs:
    #     tempColName = {'ChronicAbsenteeismEligibleEnrollment': 'DataValue', 'ChronicAbsenteeismCount': 'DataValue',
    #                    'CumulativeEnrollment': 'DataValue'}
    #     calcTablesChronAbs[i].rename(columns=tempColName, inplace=True)
    #
    # for i in ['SusDataEthnicity_stack', 'SusDatasubGroup_stack']:
    #     calcTablesSus[i + '_Unique_Cnt']['Metric'] = 'Unique_Cnt'
    #     calcTablesSus[i + '_Incident_Cnt']['Metric'] = 'Incident_Cnt'
    #     calcTablesSus[i + '_CumulativeEnrollment_Cnt']['Metric'] = 'CumulativeEnrollment_Cnt'
    # for i in ['ChronAbsEth_Stack', 'ChronAbsSubgroup_Stack']:
    #     calcTablesChronAbs[i + '_CumEnrollEligChronic_Cnt']['Metric'] = '_CumEnrollEligChronic_Cnt'
    #     calcTablesChronAbs[i + '_ChronicAbsentees_Cnt']['Metric'] = '_ChronicAbsentees_Cnt'
    #
    # for i in calcTablesChronAbs:
    #     calcTablesChronAbs[i]['MetricSource'] = 'CA_AttMemb_CDE'
    #     calcTablesChronAbs[i]['MetricID'] = calcTablesChronAbs[i]['MetricSource'] + calcTablesChronAbs[i]['Metric']
    #
    # for i in calcTablesSus:
    #     calcTablesSus[i]['MetricSource'] = 'CA_Discipline_CDE_'
    #     calcTablesSus[i]['MetricID'] = calcTablesSus[i]['MetricSource'] + calcTablesSus[i]['susRep'] + calcTablesSus[i][
    #         'Metric']
    #
    # # Stack final Data
    # ChronAbsStack = pd.concat(calcTablesChronAbs)
    # SusStack = pd.concat(calcTablesSus)
    #
    # sy_conversion
    # ChronAbsStackTemp = ChronAbsStack.merge(sy_conversion, how='left', on='SchoolYear_CDE')
    # SusStackTemp = SusStack.merge(sy_conversion, how='left', on='SchoolYear_CDE')
    #
    # # join School name to data
    # ChronAbsStackFinal = SusStackTemp.merge(gdSchools.filter(['CDS', 'School', 'SchoolID']), left_on='SchoolCDS',
    #                                         right_on='CDS')
    # SusStackFinal = SusStackTemp.merge(gdSchools.filter(['CDS', 'School', 'SchoolID']), left_on='SchoolCDS',
    #                                    right_on='CDS')
    #
    # # join SchoolYear
    #
    # ChronAbsStackFinal = ChronAbsStackFinal.filter(stagingTableCol)
    # SusStackFinal = SusStackFinal.filter(stagingTableCol)
    #
    # if os.path.exists(path_FinalOutput):
    #     print(f'path {path_Output} exists')
    # else:
    #     print(f'Creating Path: {path_FinalOutput}')
    #     os.mkdir(path_FinalOutput)
    #
    # susOutputPath = os.path.join(path_FinalOutput, 'CDE_Suspensions{}.csv'.format(''))
    # AbsenteeismOutputPath = os.path.join(path_FinalOutput, 'CDE_Absenteeism{}.csv'.format(''))
    #
    # SusStackFinal.to_csv(susOutputPath, index=False)
    # cowsay.cow(f'CDE_Suspensions has been stacked and placed in this path: \n {susOutputPath}')
    # ChronAbsStackFinal.to_csv(AbsenteeismOutputPath, index=False)
    # cowsay.cow(f'CDE_Absenteeism has been stacked and placed in this path: \n {AbsenteeismOutputPath}')


def StageTableDepricate():
    projectWD = os.getcwd()
    path_Output = os.path.join(projectWD, 'ReportOutput')
    # Final Report Output to import into DW
    path_FinalOutput = os.path.join(path_Output, 'FinalData')

    sy_conversion = pd.read_csv(os.path.join(projectWD, 'Resources', 'SchoolYear.txt'), sep='\t')

    stagingTableCol = ['MetricID', 'School', 'SchoolID', 'GroupType', 'Subgroup', 'SchoolYear', 'DataValue']
    metricID_CA_Discipline_CDE = ['CA_Discipline_CDE_SusIncident_Cnt',
                                  'CA_Discipline_CDE_OSSIncident_Cnt',
                                  'CA_Discipline_CDE_ISSIncident_Cnt',
                                  'CA_Discipline_CDE_SusUnique_Cnt',
                                  'CA_Discipline_CDE_OSSUnique_Cnt',
                                  'CA_Discipline_CDE_ISSUnique_Cnt',
                                  'CA_Discipline_CDE_ExpUnique_Cnt']
    metricID_CA_AttMemb_CDE = ['CA_AttMemb_CDE_ChronicAbsentees_Cnt',
                               'CA_AttMemb_CDE_CumEnrollEligChronic_Cnt']
    # CDE Codes for conversion
    PHI = 19647330124024
    LGC = 19647330124016

    GD_Subgroups = pd.read_csv(os.path.join(projectWD, 'Resources', 'GD_Subgroups.txt'), sep='\t')
    fileList = os.listdir(path_Output)

    # School Names
    gdSchools = pd.read_csv(os.path.join(projectWD, 'Resources', 'GreenDot_CDS_Codes_final.txt'), sep='\t')

    dataFinal = {}
    for i in fileList:
        if '.csv' in i:
            dataFinal.update({i.replace('.csv', ''): pd.read_csv(os.path.join(path_Output, i))})
        else:
            pass

    GD_Subgroups = pd.read_csv(os.path.join(projectWD, 'Resources', 'GD_Subgroups.txt'), sep='\t')
    # SusDataEthnicity_stack[1].Ethnicity.drop_duplicates()
    chronAbsColumnReplace = {'School Name': 'school_name', 'Student Group': 'subgroup', 'Grade Band': 'grade_band',
                             '# Students': 'n_students', '# Chronically Absent': 'n_chronically_absent',
                             '% Chronically Absent': 'pct_chronically_absent', 'School': 'school', 'District': 'system',
                             'District Name': 'system_name'}

    # rename column to prevent future conflict
    ColReplace = {'Ethnicity': 'CDE_Subgroup', 'Subgroup': 'CDE_Subgroup'}
    dataFinal['ChronAbsEth_Stack'].rename(columns=ColReplace, inplace=True)
    dataFinal['ChronAbsSubgroup_Stack'].rename(columns=ColReplace, inplace=True)
    dataFinal['SusDataEthnicity_stack'].rename(columns=ColReplace, inplace=True)
    dataFinal['SusDatasubGroup_stack'].rename(columns=ColReplace, inplace=True)

    # drop empty rows
    dataFinal['ChronAbsEth_Stack'].dropna(subset=['CDE_Subgroup'], inplace=True)
    dataFinal['ChronAbsSubgroup_Stack'].dropna(subset=['CDE_Subgroup'], inplace=True)
    dataFinal['SusDataEthnicity_stack'].dropna(subset=['CDE_Subgroup'], inplace=True)
    dataFinal['SusDatasubGroup_stack'].dropna(subset=['CDE_Subgroup'], inplace=True)

    dataFinal['ChronAbsEth_Stack'].reset_index(drop=True, inplace=True)
    dataFinal['ChronAbsSubgroup_Stack'].reset_index(drop=True, inplace=True)
    dataFinal['SusDataEthnicity_stack'].reset_index(drop=True, inplace=True)
    dataFinal['SusDatasubGroup_stack'].reset_index(drop=True, inplace=True)

    # convert Animo Phillis Wheatley to Legacy
    dataFinal['ChronAbsEth_Stack'].SchoolCDS.replace(PHI, LGC, inplace=True)
    dataFinal['ChronAbsSubgroup_Stack'].SchoolCDS.replace(PHI, LGC, inplace=True)
    dataFinal['SusDataEthnicity_stack'].SchoolCDS.replace(PHI, LGC, inplace=True)
    dataFinal['SusDatasubGroup_stack'].SchoolCDS.replace(PHI, LGC, inplace=True)

    # pd.merge(dataFinal['ChronAbsEth_Stack'], GD_Subgroups, how='left', on=['Ethnicity'])
    dataFinalMerge = {}
    for i in ['ChronAbsEth_Stack', 'ChronAbsSubgroup_Stack', 'SusDataEthnicity_stack', 'SusDatasubGroup_stack']:
        dataFinalMerge.update({i: dataFinal[i].merge(GD_Subgroups, left_on='CDE_Subgroup', right_on='CDE_Subgroup')})

    calcTablesSus = {}
    for i in ['SusDataEthnicity_stack', 'SusDatasubGroup_stack']:
        # Temp Vars are to have a single point to change
        tempCol = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment',
                   'UnduplicatedCount ofStudentsSuspended']
        tempGroupBy = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup']
        calcTablesSus.update({i + '_Unique_Cnt': dataFinalMerge[i].filter(
            ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup',
             'UnduplicatedCount ofStudentsSuspended']).groupby(tempGroupBy, as_index=False).agg(
            {'UnduplicatedCount ofStudentsSuspended': 'sum'})})
        calcTablesSus.update({i + '_Incident_Cnt': dataFinalMerge[i].filter(
            ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'TotalSuspensions']).groupby(tempGroupBy,
                                                                                                            as_index=False).agg(
            {'TotalSuspensions': 'sum'})})
        calcTablesSus.update({i + '_CumulativeEnrollment_Cnt': dataFinalMerge[i].filter(
            ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment']).groupby(
            tempGroupBy, as_index=False).agg({'CumulativeEnrollment': 'sum'})})

    # Rename loop
    for i in calcTablesSus:
        tempColName = {'UnduplicatedCount ofStudentsSuspended': 'DataValue', 'TotalSuspensions': 'DataValue',
                       'CumulativeEnrollment': 'DataValue'}
        calcTablesSus[i].rename(columns=tempColName, inplace=True)

    calcTablesChronAbs = {}
    for i in ['ChronAbsEth_Stack', 'ChronAbsSubgroup_Stack']:
        # Temp Vars are to have a single point to change
        tempCol = ['SchoolCDS', 'SchoolYear_CDE', 'susRep', 'GroupType', 'Subgroup', 'CumulativeEnrollment',
                   'UnduplicatedCount ofStudentsSuspended']
        tempGroupBy = ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup']
        calcTablesChronAbs.update({i + '_CumEnrollEligChronic_Cnt': dataFinalMerge[i].filter(
            ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup', 'ChronicAbsenteeismEligibleEnrollment']).groupby(
            tempGroupBy, as_index=False).agg({'ChronicAbsenteeismEligibleEnrollment': 'sum'})})
        calcTablesChronAbs.update({i + '_ChronicAbsentees_Cnt': dataFinalMerge[i].filter(
            ['SchoolCDS', 'SchoolYear_CDE', 'GroupType', 'Subgroup', 'ChronicAbsenteeismCount']).groupby(tempGroupBy,
                                                                                                         as_index=False).agg(
            {'ChronicAbsenteeismCount': 'sum'})})
    # Rename loop
    for i in calcTablesChronAbs:
        tempColName = {'ChronicAbsenteeismEligibleEnrollment': 'DataValue', 'ChronicAbsenteeismCount': 'DataValue',
                       'CumulativeEnrollment': 'DataValue'}
        calcTablesChronAbs[i].rename(columns=tempColName, inplace=True)

    for i in ['SusDataEthnicity_stack', 'SusDatasubGroup_stack']:
        calcTablesSus[i + '_Unique_Cnt']['Metric'] = 'Unique_Cnt'
        calcTablesSus[i + '_Incident_Cnt']['Metric'] = 'Incident_Cnt'
        calcTablesSus[i + '_CumulativeEnrollment_Cnt']['Metric'] = 'CumulativeEnrollment_Cnt'
    for i in ['ChronAbsEth_Stack', 'ChronAbsSubgroup_Stack']:
        calcTablesChronAbs[i + '_CumEnrollEligChronic_Cnt']['Metric'] = '_CumEnrollEligChronic_Cnt'
        calcTablesChronAbs[i + '_ChronicAbsentees_Cnt']['Metric'] = '_ChronicAbsentees_Cnt'

    for i in calcTablesChronAbs:
        calcTablesChronAbs[i]['MetricSource'] = 'CA_AttMemb_CDE'
        calcTablesChronAbs[i]['MetricID'] = calcTablesChronAbs[i]['MetricSource'] + calcTablesChronAbs[i]['Metric']

    for i in calcTablesSus:
        calcTablesSus[i]['MetricSource'] = 'CA_Discipline_CDE_'
        calcTablesSus[i]['MetricID'] = calcTablesSus[i]['MetricSource'] + calcTablesSus[i]['susRep'] + calcTablesSus[i][
            'Metric']

    # Stack final Data
    ChronAbsStack = pd.concat(calcTablesChronAbs)
    SusStack = pd.concat(calcTablesSus)
    ChronAbsStackTemp = ChronAbsStack.merge(sy_conversion, how='left', on='SchoolYear_CDE')
    SusStackTemp = SusStack.merge(sy_conversion, how='left', on='SchoolYear_CDE')

    # join School name to data
    ChronAbsStackFinal = SusStackTemp.merge(gdSchools.filter(['CDS', 'School', 'SchoolID']), left_on='SchoolCDS',
                                            right_on='CDS')
    SusStackFinal = SusStackTemp.merge(gdSchools.filter(['CDS', 'School', 'SchoolID']), left_on='SchoolCDS',
                                       right_on='CDS')

    # join SchoolYear

    ChronAbsStackFinal = ChronAbsStackFinal.filter(stagingTableCol)
    SusStackFinal = SusStackFinal.filter(stagingTableCol)

    if os.path.exists(path_FinalOutput):
        print(f'path {path_Output} exists')
    else:
        print(f'Creating Path: {path_FinalOutput}')
        os.mkdir(path_FinalOutput)

    susOutputPath = os.path.join(path_FinalOutput, 'CDE_Suspensions{}.csv'.format(''))
    AbsenteeismOutputPath = os.path.join(path_FinalOutput, 'CDE_Absenteeism{}.csv'.format(''))

    SusStackFinal.to_csv(susOutputPath, index=False)
    cowsay.cow(f'CDE_Suspensions has been stacked and placed in this path: \n {susOutputPath}')
    ChronAbsStackFinal.to_csv(AbsenteeismOutputPath, index=False)
    cowsay.cow(f'CDE_Absenteeism has been stacked and placed in this path: \n {AbsenteeismOutputPath}')


if __name__ == "__main__":
    StageTable()
