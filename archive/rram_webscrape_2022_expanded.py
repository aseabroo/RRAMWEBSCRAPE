# Augustus Seabrooke
# Webscraping RRAM
# Task : To scrape a given look and extract PDF data. Then, display the data in to a graph form. 
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


# This function will scrape all of the available PDF files on the link. I put a test code in to mimic a potential "update"  scenario. 
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
# Thus, I ended up concating the list of dataframe in to one single dataframe. I also think this function can be coded as that the runtime is faster.
# I am not sure if there is a way to extract PDF files faster than one by one. 
# This function can be abstracted. 
def extract(pdf_path, pdf_title):
    # print(pdf_path)
    df = tabula.read_pdf(pdf_path, multiple_tables= True, area = (134.53, 14.74, 498.77, 305.62, ), pages = 1 )
    pdf_title = pdf_title.replace('AAR', '')
    if len(df[0].columns) == 3:
        df[0].drop('2', inplace=True, axis = 1)
    df[0].columns = [ 'Product Type', pdf_title]
    df = pd.concat(df)
    return df

# This function returns an integer with commas and spaces removed. 
def to_int(s):
    return int(s.replace(',','').replace(' ',''))

# This function makes a copy of the dataframe, interates through every relevant row per week to change the value in to a percentage.
# This functon then rounds up the percentage to decimal points. 
def percentize(df):
    df = df.copy(deep = True)
    num_cols = df.shape[1]
    for week in range(0,num_cols):
        # The math ((value / total value) * 100) = new value in that row at that week formula to change the values.
        df.iloc[:,week] = (df.iloc[:,week] / df.iloc[:,week].sum()) * 100 
    df = df.round(2)
    print('round', df.dtypes)
    return df.round(2)

# This function first extracts each of the pdf files, cleans the files up, and then aggregates the files in to
# one single, beautiful, clean dataframe. Then, the function will save and display the graphs in a line plot, line subplots, and a bar chat using the 
# value data and the percentized data. 
def aggregate_data(pdf_link_list):
    appended_data = []
    for pdf in pdf_link_list: # for every pdf file in this list of pdf links
        pdf_path = pdf_link_list[pdf] # set the link to pdf_path
        carload_dataframe = extract(pdf_path, pdf) # call extract function, and set it ot the carload_dataframe
        appended_data.append(carload_dataframe) # add to list of dataframe
    appended_data = pd.concat(appended_data, axis = 1) # create one single dataframe
    clean_data = appended_data.T.drop_duplicates().T # drop duplicate columns
    clean_data = clean_data.set_index('Product Type') # set the Product Type as index column
    # This is to drop the extra rows that extract method accidentally took in. 
    for x in ['Trailers','Containers', 'Total Intermodal', 'Total Traffic', 'Total Carloads']:
      clean_data.drop(x, inplace = True)
    t_data = clean_data.applymap(to_int).T # changes the string values in the dataframe to integars and transposes the data.
    clean_data = t_data.iloc[::-1] # reverses the rows so that the time series goes from left to right with the date increasing as we go right. 
    print(clean_data) # prints data table in terminal for viewing.
    percent_data = percentize(clean_data) # call percentize method.
    print(percent_data) # prints percentize data in terminal for viewing.
    # The following transforms the data in to line plot, subplots, and barplots depending on the data type.
    line_plot(percent_data, 'Volume %', 'Carload Volume % by Product Type', 'percentage')
    separated_line_plots(percent_data, 'Carload Volume % by Product Type', 'percentage')
    bar_plot(percent_data, 'Volume %', 'Carload Volume % by Product Type', 'percentage')
    line_plot(clean_data, 'Volume', 'Carload Volume by Product Type', '')
    separated_line_plots(clean_data,'Carload Volume by Product Type', '')

# This function is a test code to scrape only 4 files
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

# This function creates a stacked bar plot to visualize the percentages of carload. Nice to use to observe at a quick glance.
# However, there is some wonkiness to it. 
def bar_plot(df,y_label, graph_title, unit):
    ax = df.plot(kind='bar',
        figsize = (9, 9),
        stacked = True, 
        title = graph_title,
        xlabel = 'Week',
        ylabel= y_label, 
        y = df.columns,
        rot = 60)
    plt.legend(bbox_to_anchor = (1.0,0.5), 
        loc = 'center left', 
        borderaxespad = 1, 
        ncol = 1,
        fontsize=6)
    plt.tick_params(axis='both', which = 'major', labelsize = 5)
    plt.subplots_adjust(right=.6, bottom = .2)
    plt.savefig('bar_plot_' + unit  + '.png')
    plt.show()

# This function builds a single line plot graph with multiple variables. 
# The graph tends to look confusing with multiple variables.
def line_plot(df, y_label, graph_title, unit): 
    ax = df.plot(
        kind = 'line',
        figsize= (11,5),
        title = graph_title,
        xlabel = 'Week',
        ylabel = y_label,
        y = list(df.columns),
        legend = True,
        )
    plt.legend(bbox_to_anchor = (1.0,0.5), 
        loc = 'center left', 
        borderaxespad = 5, 
        ncol = 1,
        fontsize=7)
    plt.tick_params(axis='both', which = 'major', labelsize = 5)
    plt.xticks(rotation = 60)
    ax.set_xticks(ticks = range(len(df.index)), labels = df.index)
    plt.subplots_adjust(right=.69, bottom = .2)
    plt.savefig('line_plot_' + unit + '.png')
    plt.show()

# This function displays data by product type in separated graphs for easier comparison. 
def separated_line_plots(df, graph_title, unit):
    axes = df.plot(
        use_index = True,
        xticks = range(len(df.index)),
        subplots = True,
        kind = 'line',
        figsize= (12,8),
        layout = (10,2),
        title = graph_title,
        sharex = True,
        sharey = False,
        y = list(df.columns),
        legend = True,
    )
    axes = axes.flat # flattens array (numpy) to handle legend method
    #extract figure object to use figure level methods
    fig = axes[0].get_figure()
    #iterate thru each axes to use axes level methods
    for ax in axes:
        ax.legend(bbox_to_anchor = (0.5,1.6),
            loc='upper center', 
            fontsize = 7,
            frameon = False)
        ax.tick_params(axis='both', 
            which = 'major', 
            labelsize = 5,)
        ax.tick_params(axis='x',
            which = 'major',
            rotation = 60)
    plt.minorticks_off()
    plt.subplots_adjust(wspace = .2, hspace = .80)
    fig.text(0.05, 0.5, 'Volume ', ha = 'center', va = 'center', rotation = 90)
    fig.text(0.5,0.04, 'Week', ha='center', va='center')
    plt.savefig('separated_line_plot_'+ unit + '.png')
    plt.show()
   


#pdfList= baby_scrape()
pdfList = year_scrape('2022')
# pdflist = initial_scrape()

clean = aggregate_data(pdfList)

#convert_to_percentage(clean)
# pdfs = initial_scrape
# update_scrape(pdfs)

