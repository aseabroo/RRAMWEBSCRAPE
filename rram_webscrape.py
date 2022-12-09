# Augustus Seabrooke
# Webscraping RRAM
# SOURCE: https://www.geeksforgeeks.org/how-to-scrape-all-pdf-files-in-a-website/

# for get request of the PDF files or URL
from tkinter import font
import PyPDF2
import requests
# for tree traversal scraping in webpage
from bs4 import BeautifulSoup
# for input and output operations
import io
# for dynamic webscraping
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
# for getting information about the pdfs
from PyPDF2 import PdfFileReader, PdfFileWriter
# for pandas DataFrame  and data manipulation
import pandas as pd
import tabula
import matplotlib.pyplot as plt

# website to scrape 
url = "https://investors.csx.com/metrics/default.aspx#volume-trends"
# initiating webdriver
driver = webdriver.Chrome('/Users/augustusseabrooke/Downloads/chromedriver')
driver.get(url)
#ensure page is loaded
time.sleep(5)
# renders JS code and stores all of info in static html code
html = driver.page_source 
# parse hTML content
soup = BeautifulSoup(html, "html.parser")
list_of_pdf = dict()
count_pdf = 0
driver.close()


def initial_scrape():
    # finds all of the pdf links available on the page
    module_items = soup.find_all(class_="module_link module-downloads_title-link")
    for module_item in module_items:
        # text for [year] Week [#] AAR
        pdf_title = module_item.find('span').text
        # link for [year] Week [#] AAR
        pdf_path = module_item.get('href')
        # TEST CODE : this is only just to check if I can update the table
        if '32' in pdf_title:
            print('32')
            continue
        list_of_pdf[pdf_title] = pdf_path
    return list_of_pdf

 # This function scrapes the webpage based on the year. However, this does not deal with the drop down menu for archive downloads.
def year_scrape(year):
    # finds all of the pdf links available on the page
    module_items = soup.find_all(class_="module_link module-downloads_title-link")
    for module_item in module_items:
        pdf_title = module_item.find('span').text # searches for the Weekly title of the pdf
        pdf_path = module_item.get('href') # gets the links of each pdf
        if pdf_title.startswith(year): # if the title matches the passed  year variable
            list_of_pdf[pdf_title] = pdf_path # add the file path to the list of pdf
    return(list_of_pdf)


# This function works by taking the top most pdf download link on the website, which usually is 
# the most recent pdf link and checks to see if the list of pdfs have been updated with the 
# newest or most recent pdf file. BEWARE: This will not work properly if the developers of the website 
# change how they position their most updated link. 
def update_scrape(pdf_list):
    # update the list of pdf when first element is not in list of pdf
    newest_module = soup.find(class_="module_link module-downloads_title-link") # grabs the first relevant pdf file on the page
    newest_pdf_title = newest_module.find('span').text # sets the variable to the string title of the most recent pdf file
    newest_pdf_link = newest_module.get('href') # gets the link to the most recent pdf file
    if newest_pdf_title not in pdf_list: # if the most recent title is not in the list, add it ot the list
        print('does not exist')
        pdf_list[newest_pdf_title] = newest_pdf_link
        print('updated')
    else:
        print('does exist')

# TEST CODE FOR ONE PDF FILE
# def scrape_1():
#     pdf_dict = dict()
#     newest_module = soup.find(class_="module_link module-downloads_title-link")
#     newest_pdf_title = newest_module.find('span').text
#     newest_pdf_link = newest_module.get('href')
#    # print(newest_pdf_title)
#    # print(newest_pdf_link)
#     pdf_dict[newest_pdf_title] = newest_pdf_link
#     return pdf_dict[newest_pdf_title]

# This function takes in a pdf path and pdf title. The pdf path is used with tabula.read_pdf function
# to extract data from the pdf. This function extract pdf data from one pdf at a time. This function returns
# a list of dataframe objects. Essentially, we are returning a list of one dataframe each time. 
# Thus, I ended up concating the list of dataframe in to one single dataframe.
# This function can be abstracted. 
def extract(pdf_path, pdf_title):
    # print(pdf_path)
    df = tabula.read_pdf(pdf_path, multiple_tables= True, area = (134.53, 14.74, 498.77, 305.62, ), pages = 1 )
    pdf_title = pdf_title.replace('AAR', '')
    print(len(df[0].columns))
    if len(df[0].columns) == 3:
        df[0].drop('2', inplace=True, axis = 1)
    df[0].columns = [ 'Product Type', pdf_title]
    df = pd.concat(df)
    
  #  print(df)
    return df

def to_int(s):
    return int(s.replace(',','').replace(' ',''))


def percentize(df):
      # to do: make % of total volume and display  
  #  print(df)
    df = df.copy(deep = True)
   # print('copy:', df)
    df = df.applymap(to_int)
    print('percentize apply map type:' , df.dtypes)
  #  print('applymap', df)
    num_cols = df.shape[1]
    for week in range(0,num_cols):
   #     print('week', week, 'col', num_cols)
    # looks at every row in a given column (week)
        df.iloc[:,week] = (df.iloc[:,week] / df.iloc[:,week].sum()) * 100
    df = df.round(2)
    print('round', df.dtypes)
    return df.round(2)
# This function first extracts each of the pdf files, cleans the files up, and then aggregates the files in to
# one single, beautiful, clean dataframe.
def aggregate_data(pdf_link_list):
    count = 0
    i = 0
    appended_data = []
    for pdf in pdf_link_list: # for every pdf file in this list of pdf links
        pdf_path = pdf_link_list[pdf] # set thhe link to pdf_path
        carload_dataframe = extract(pdf_path, pdf) # call extract function, and set it ot the carload_dataframe
        appended_data.append(carload_dataframe) # add to list of dataframe
    appended_data = pd.concat(appended_data, axis = 1) # create one single dataframe
    clean_data = appended_data.T.drop_duplicates().T # drop duplicate columns
   # clean_data.to_excel(r'/Users/augustusseabrooke/Downloads/test.xlsx', index = True)
    clean_data = clean_data.set_index('Product Type') # set the Product Type as index column
   # to do: make % of total volume and display  clean_data.astype(float)
    #clean_data.add(1)
    for x in ['Trailers','Containers', 'Total Intermodal', 'Total Traffic', 'Total Carloads']:
      clean_data.drop(x, inplace = True)
   # clean_data = clean_data.astype('int')
    clean_data = percentize(clean_data)
    print(clean_data.dtypes)
    clean_data = line_plot(clean_data)
    return clean_data


# test code to scrape only 4 files
def baby_scrape():
    # finds all of the pdf links available on the page
    module_items = soup.find_all(class_="module_link module-downloads_title-link")
    for module_item in module_items:
        # text for [year] Week [#] AAR
        pdf_title = module_item.find('span').text
        # link for [year] Week [#] AAR
        pdf_path = module_item.get('href')
        # TEST CODE : this is only just to check if I can update the table
        if '32' in pdf_title or '30' in pdf_title:
         #   print('32')
            list_of_pdf[pdf_title] = pdf_path
        else:
            continue   
        count_pdf + 1
    return list_of_pdf


def bar_plot(df):
    df = df.T
    df.plot(kind='bar',
        figsize = (9, 9),
        stacked = True, 
        title = 'Carload % Volume by Product Type',
        xlabel = 'Week Date', 
        ylabel= 'Volume %', 
        y = list(df.columns),
        rot = 60)
    plt.legend(bbox_to_anchor = (1.0,0.5), 
        loc = 'center left', 
        borderaxespad = 1, 
        ncol = 1,
        fontsize=6)
    plt.subplots_adjust(right=.6, bottom = .2)
    plt.show()

def line_plot(df):
    df = df.T
    df.plot(kind='line',
        subplots = True,
        layout = (4, 5),
        figsize = (10,10),
        title = 'Carload % Volume by Product Type',
        xlabel = 'Week Date', 
        ylabel= 'Volume %', 
        y = list(df.columns),
        rot = 60)
    plt.legend( 
        loc = 'upper center', 
        borderaxespad = 1, 
        ncol = 1,
        fontsize=6)

  #  plt.subplots_adjust(right=.6, bottom = .2)
   
    plt.show()
    
# def plot_data(df):
#     df = df.T
#     df.index.name = 'Week'
#     print('index', df.index.name)
#     fig, a = plt.subplots(10,2, figsize =(12,8), tight_layout=True)
#     ax = df.plot(ax = a, kind = 'line', subplots= True, title = 'Carload Percentage by Total Volume', layout = (10, 2), sharex=True, 
#             sharey=True, y = list(df.columns), rot = 60, )
#     for a in ax:
#         a.legend(loc='upper left', prop = {'size': 6})
#    # legend = plt.legend( bbox_to_anchor=(0.85,1.025), loc='upper right', borderaxespad=0, ncol= 2)
#   #  plt.title('Carload Data by Percentage of Volume', color = 'black')
#    # plt.savefig('figure', bbox_extra_artist=legend, bbox_inches = 'tight')

#     plt.show()



    #print('columns', df.columns)
   # print(df)

    # .plot(kind = 'line', use_index= True, y = )
  #  print(df)
  #  print(plt.xlabel(df.columns))
   # plt.show()

link = "https://s2.q4cdn.com/859568992/files/doc_downloads/volume_trends/2022/2022-Week-32-AAR.pdf"
# dfs= tabula.read_pdf(link, multiple_tables= True, area = (134.53, 14.74, 498.77, 305.62, ), pages = 1 )
# print(dfs)

pdfList= baby_scrape()
# year_scrape('2022')
# pdflist = initial_scrape()


clean = aggregate_data(pdfList)

#convert_to_percentage(clean)

# update_scrape(pdfs)

