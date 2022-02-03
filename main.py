import pandas as pd
from datetime import datetime
import requests
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt #used to render data results visually


#Build the project dictionary

months = [
{'Jan', 1},
{'Feb', 2},
{'Mar', 3},
{'Apr', 4},
{'May', 5},
{'Jun', 6},
{'Jul', 7},
{'Aug', 8},
{'Sep', 9},
{'Oct', 10},
{'Nov', 11},
{'Dec', 12}
]




# Get countiees list by JSON
url = 'https://api.first.org/data/v1/countries'
r = requests.get(url)

# Decode the JSON data into a dictionary: json_data
country_data = r.json()

#print countries dictionary
#print(type(country_data['data']))

#read the data from the everest.csv file into a Panda DataFrame
df = pd.DataFrame(pd.read_csv("everest.csv"))


df.fillna(0)


#strip control chars from col headers
df.columns = df.columns.str.rstrip('\xa0')

#get a list of the column headers and store in a list... not sure, may need it later on
col_list = (df.columns.tolist())
#print(col_list)

#Parse the 'Yr/Season' column into seperate Year & Season Columns
df['Year'] = df['Yr/Seas'].str[:4]
df['Season'] = df['Yr/Seas'].str[5:8]


#use loc to replace  the 'No' value in the Oxy Column with 'N'
df.loc[df['Oxy'] == 'No', 'Oxy'] = 'N'
df.loc[df['Dth'] == '.', 'Dth'] = 'N'

#print the DataFrame Shape - Attribute
print(df.shape)

#print the DataFrame Info - Method
print(df.info())


null_pc = df.isnull().mean()
print('Null % = ' + str(null_pc))

#get the mean time for the data set
#dfGoodTimes = df[df['Time'] != '0']

#meantime = dfGoodTimes['Time'].value_counts().argmax()
#print('MEAN TIME = ' + str(meantime))

#Add function to validate Time value in DataFrame
def timeIsValid(timein):
    timeformat = "%H:%M"

    #check to ensure argument passed in is a $
    if isinstance(timein, str) != True :
        return False

    try:
        validtime = datetime.strptime(timein, timeformat)
        #Do your logic with validtime, which is a valid format
        return True
    except ValueError:
        #Do your logic for invalid format (maybe print some message?).
        return False


#renders a Seaborn relative visual
def renderSeabornRelativeVisual(data, kind, markers, xLab, yLab, title, rotation) :
    sns.relplot(data=data, kind=kind, markers=markers)
    plt.xlabel(xLab, labelpad=14)
    plt.ylabel(yLab, labelpad=14)
    plt.title(title)
    plt.xticks(rotation=rotation)
    plt.show()
    plt.close()

#renders a Seaborn count visual
def renderSeabornCountVisual(data, xColumn, xLab, yLab, title, rotation) :

    plt.figure(figsize=(20, 13))
    sns.countplot(x= xColumn, data=data)
    plt.xlabel(xLab, labelpad=14)
    plt.ylabel(yLab, labelpad=14)
    plt.title(title)
    plt.xticks(rotation=rotation)
    plt.show()
    plt.close()



def renderMatPlotVisual(data, kind, xLab, yLab, title, ascending) :

    print(data)
    #sort data
    data.sort_values(ascending=ascending)
    #get categories
    categories = data.index.tolist()
    #enumerate categories
    x_pos = [i for i, _ in enumerate(categories)]
    data.plot(kind=kind)

    plt.title(title, y=1.02)


    #set visual look & feel
    if kind == 'bar' :
        plt.xlabel(xLab, labelpad=14)
        plt.ylabel(yLab, labelpad=14)
        plt.xticks(x_pos, categories)
    else :
        plt.labels = categories
        plt.legend(categories)

    plt.show()
    plt.close()


#return a data snapshot filtered by key & value passed in

def filter_data_by_column(key, value):
    return df[df[key] == value]

#Loop thru the DataFrame and build the following new Columns... Age_Group. SummitHour, Month
for i in range(len(df)):

    month = df.loc[i, 'Date'][3:6]
    #month_number = months[month]

    df.loc[i, 'Month'] = month
    #df.loc[i, 'MonthNumber'] = month_number
    if timeIsValid(df.loc[i, 'Time']):
        df.loc[i, 'SummitHour'] = df.loc[i, 'Time'][:2]

    if df.loc[i,'Age'] > 0:
        df.loc[i,'Age_Group']=int(df.loc[i,'Age']/10)*10

    if df.loc[i, 'Host'] == 'Nepal':
        df.loc[i, 'Route'] = 'South Col'

    else:
        df.loc[i, 'Route'] = 'North Face'




#Sort the DataFrame by Summit Shout
df.sort_values(by=['SummitHour'], ascending=True)


#group data by Year, needed tp render the number of summits per year over time
dfGroup = df.groupby(['Year']).size().reset_index(name='Summits')
#print(dfGroup)

np_yearly_summits = np.array(dfGroup['Year'], dfGroup['Summits'])

#Get a snapshot of data for people who summited without Oxygen
df_no_oxygen = filter_data_by_column('Oxy', 'N')


#Set up the default palette for the Visuals
hue_colors = { 'South Col' : "#808080", 'North Face': '#00FF00' }
sns.set_palette('Set2')
sns.set_style('whitegrid')

#### DISPLAY NUMBER OF SUMMITS PER YEAR ####
renderSeabornRelativeVisual(np_yearly_summits, "line", True, "Summits", "Year", 'Summits Timespan', 90)

#### DISPLAY NUMBER OF SUMMITS BY ROUTE ####
renderMatPlotVisual(df.Route.value_counts(), 'bar', "Route","Summits", "Summits by Route", True)

#### DISPLAY NUMBER OF SUMMITS BY SEASON ####
renderMatPlotVisual(df['Season'].value_counts(), 'bar', "Season","Summits", "Summits per Season", True)

#### DISPLAY NUMBER OF SUMMITS BY MONTH ####
renderMatPlotVisual(df['Month'].value_counts(), 'bar', "Month","Summits", "Summits per Month", True)

#### DISPLAY NUMBER OF SUMMITS BY HOUR ####
renderMatPlotVisual(df['SummitHour'].value_counts(), 'bar', "Hour","Summits", "Summits by Hour", True)

#### DISPLAY NUMBER OF SUMMITS BY AGE GROUP ####
renderMatPlotVisual(df['Age_Group'].value_counts(), 'pie', "Age Group","Summits", "Summits per Age Group", True)


sns.relplot(x='Age_Group', y='Year', hue='Route',  kind='line', palette=hue_colors, data=df)
plt.xlabel("Age", labelpad=14)
plt.ylabel("Year", labelpad=14)
plt.title("Age Groups Summits by Year", y=1.02)
plt.show()
plt.close()

#### DISPLAY WITH/WITHOUT OXYGEN ####
renderSeabornCountVisual(df, "Oxy", "Oxygen", "Summits", 'Assisted/Unassisted Summits', 90)

renderSeabornCountVisual(df_no_oxygen, "Citizenship", "Nationality", "Summits", 'Unassisted Summits by Nationality', 90)

