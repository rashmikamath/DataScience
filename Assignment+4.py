
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[11]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[12]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[13]:

import pandas as pd
import numpy as np
import re

university_towns = open('university_towns.txt', 'r').readlines()


# In[14]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
xls
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    state = ""
    lst = []
    dict1 = {}
    for line in university_towns:
        if '[ed' in line:
            state = line.split("[edit]")[0].strip(' ')
        else:
            if '(' in line:
                region = line.split("(")[0].strip(' ')
            else:
                region = line.strip()
            lst.append((state,region))

    list_of_university = pd.DataFrame(lst,columns=['State','RegionName'])
    return list_of_university


# In[15]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdplevel = pd.read_excel("gdplev.xls", skiprows=7)
    gdplevel = gdplevel[['Unnamed: 4','Unnamed: 5','Unnamed: 6']]
    gdplevel['Year'] = gdplevel['Unnamed: 4'].apply(lambda x: x[:4]).astype('int64')
    gdplevel = gdplevel[gdplevel['Year']>=2000]
    gdplevel['diff_gdp'] = gdplevel['Unnamed: 5']-gdplevel['Unnamed: 5'].shift(1)
    gdplevel['change'] = np.where(gdplevel['diff_gdp']>=0, '1', '0')
    pattern = ''.join(gdplevel['change'].tolist())
    matches = re.finditer("00+11", pattern)
    match = next(matches)
    start, end = match.span()
    return gdplevel['Unnamed: 4'].iloc[start-1,]


# In[16]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdplevel = pd.read_excel("gdplev.xls", skiprows=7)
    gdplevel = gdplevel[['Unnamed: 4','Unnamed: 5','Unnamed: 6']]
    gdplevel['Year'] = gdplevel['Unnamed: 4'].apply(lambda x: x[:4]).astype('int64')
    gdplevel = gdplevel[gdplevel['Year']>=2000]
    gdplevel['diff_gdp'] = gdplevel['Unnamed: 5']-gdplevel['Unnamed: 5'].shift(1)
    gdplevel['change'] = np.where(gdplevel['diff_gdp']>=0, '1', '0')
    pattern = ''.join(gdplevel['change'].tolist())
    matches = re.finditer("00+11", pattern)
    match = next(matches)
    start, end = match.span()
    return gdplevel['Unnamed: 4'].iloc[end-1,]


# In[17]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdplevel = pd.read_excel("gdplev.xls", skiprows=7)
    gdplevel = gdplevel[['Unnamed: 4','Unnamed: 5','Unnamed: 6']]
    gdplevel['Year'] = gdplevel['Unnamed: 4'].apply(lambda x: x[:4]).astype('int64')
    gdplevel = gdplevel[gdplevel['Year']>=2000]
    gdplevel['diff_gdp'] = gdplevel['Unnamed: 5']-gdplevel['Unnamed: 5'].shift(1)
    gdplevel['change'] = np.where(gdplevel['diff_gdp']>=0, '1', '0')
    pattern = ''.join(gdplevel['change'].tolist())
    matches = re.finditer("00+11", pattern)
    match = next(matches)
    start, end = match.span()
    gdplevel = gdplevel.iloc[start-1:end-1]
    recession_bottom = gdplevel['Unnamed: 5'].min()
    recession_bottom_df = gdplevel[gdplevel['Unnamed: 5']==recession_bottom]
    re_bottom = recession_bottom_df['Unnamed: 4'].to_string(index=False)
    return re_bottom


# In[18]:

housing_data = pd.read_csv("City_Zhvi_AllHomes.csv")


# In[19]:

def get_mapping(x):
    year, quarter = x.split('q')
    if quarter == '1':
        return (year+'-'+'01', year+'-'+'02', year+'-'+'03')
    if quarter == '2':
        return (year+'-'+'04', year+'-'+'05', year+'-'+'06')
    if quarter == '3':
        if year !='2016':
            return (year+'-'+'07', year+'-'+'08', year+'-'+'09')
        else:
            return (year+'-'+'07', year+'-'+'08')
    if quarter == '4' and year != '2016':
        return (year+'-'+'10', year+'-'+'11', year+'-'+'12')

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returnindex=["State","RegionName"]s it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    import itertools
    housing_data = pd.read_csv("City_Zhvi_AllHomes.csv")
    li = [(j+'q1',j+'q2',j+'q3',j+'q4') for j in ["20%02d" % (i,) for i in range(16)]]
    quater_list = list(itertools.chain.from_iterable(li))

    quater_list.append('2016q1')
    quater_list.append('2016q2')
    quater_list.append('2016q3')

    
    for i in quater_list:
        mapping = get_mapping(i)
        if len(mapping)==3:
            mean_val = housing_data[[mapping[0],mapping[1],mapping[2]]].mean(axis=1)
        else:
            mean_val = housing_data[[mapping[0],mapping[1]]].mean(axis=1)
        housing_data[i] = mean_val

    housing_data['StateX'] = housing_data['State'].apply(lambda x: states.get(x))
    housing_data = housing_data.set_index(["StateX","RegionName"])
    housing_data = housing_data[quater_list]

    housing_data_new = pd.DataFrame(housing_data)
    return housing_data_new


# In[20]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    import itertools
    housing_data = pd.read_csv("City_Zhvi_AllHomes.csv")
    li = [(j+'q1',j+'q2',j+'q3',j+'q4') for j in ["20%02d" % (i,) for i in range(16)]]
    quater_list = list(itertools.chain.from_iterable(li))

    quater_list.append('2016q1')
    quater_list.append('2016q2')
    quater_list.append('2016q3')


    for i in quater_list:
        mapping = get_mapping(i)
        if len(mapping)==3:
            mean_val = housing_data[[mapping[0],mapping[1],mapping[2]]].mean(axis=1)
        else:
            mean_val = housing_data[[mapping[0],mapping[1]]].mean(axis=1)
        housing_data[i] = mean_val

    housing_data['State'] = housing_data['State'].apply(lambda x: states.get(x))
    ux = get_list_of_university_towns()
    ux['IsUniversity']= True
    main_df = pd.merge(housing_data, ux, how='left', on=["State","RegionName"])
    main_df['IsUniversity'] = main_df['IsUniversity'].fillna(False)
    recess_start = get_recession_start()
    recess_bottom = get_recession_bottom()
    recess_start_ix = main_df.columns.get_loc(recess_start)
    recess_bottom_ix = main_df.columns.get_loc(recess_bottom)
    main_df['PriceRatio'] = main_df.iloc[:,recess_start_ix-1]/main_df.iloc[:,recess_bottom_ix]


    university_df = main_df[main_df['IsUniversity']==True]
    university_df = university_df['PriceRatio'].dropna()
    university_df_mean = university_df.mean()


    non_university_df = main_df[main_df['IsUniversity']==False]
    non_university_df = non_university_df['PriceRatio'].dropna()
    non_university_df_mean = non_university_df.mean()

    p_val = ttest_ind(non_university_df, university_df).pvalue

    different = False
    if p_val<0.01:
        different = True

    better = 'non-university town'
    if university_df_mean < non_university_df_mean:
        better = 'university town'
    
    return (different, p_val, better)

