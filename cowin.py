from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions  
from playsound import playsound

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import os
import time
import pandas as pd



def table_to_2d(table_tag):
    rowspans = []  # track pending rowspans
    rows = table_tag.find_all('tr')

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1. 
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere. 
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom. 
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans 
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1
            value = cell.get_text()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table

def startCowinDriver():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()

    #Kite Website
    driver.get('https://www.cowin.gov.in/home')

    #Find Status Checkbox //Search by Pin/District
    select_status = driver.find_element_by_class_name("custom-checkbox")
    select_status.click()

    #Select State
    select_state = driver.find_element_by_id("mat-select-0")
    select_state.click()

    time.sleep(1)

    #Karnataka
    select_options = driver.find_elements_by_xpath('//span[@class="mat-option-text"]')
    for option in select_options:
        try:
            if option.text == "Karnataka":
                option.click()
        except exceptions.StaleElementReferenceException as e:
                print(e)
                pass

    time.sleep(1)

    #Select district
    select_district = driver.find_element_by_id("mat-select-2")
    select_district.click()

    time.sleep(1)

    #BBMP
    select_options = driver.find_elements_by_xpath('//span[@class="mat-option-text"]')
    for option in select_options:
        try:
            if option.text == "BBMP":
                option.click()
        except exceptions.StaleElementReferenceException as e:
                print(e)
                pass
            
    time.sleep(1)

    #Age 18-44  flexRadioDefault1
    #All Age flexRadioDefault2
    #45+ flexRadioDefault3
    age_select = driver.find_element_by_id("flexRadioDefault1")
    age_select.click()

    time.sleep(1)

    driver.find_element_by_xpath('//button[normalize-space()="Search"]').click()

    time.sleep(2)

    cowin_html = driver.page_source
    soup = BeautifulSoup(cowin_html, "html.parser")

    #dates
    dates = []
    dates.append("Center")
    date_uls = soup.find_all("ul", {"class": "availability-date-ul"})
    for date_ul in date_uls:
        datesoup = BeautifulSoup(str(date_ul), 'html.parser')
        date_lis = datesoup.find_all('li')
        for idx in range(7):
            dates.append(str(date_lis[idx].text))
    
    df_vaccine = pd.DataFrame(columns=dates)

    #vaccine centers
    vaccine_centers = []
    h5s = soup.find_all("h5", {"class": "center-name-title"})
    for h5 in h5s:
        vaccine_centers.append(h5.text)
        #print(h5.text)

    #vaccine_availability_table = soup.find("div", {"class": "slot-available-wrap"})
    #column per row 7
    cpr = 7
    uls = soup.find_all("ul", {"class": "slot-available-wrap"})
    row_count = 0
    for ul in uls:
        newsoup = BeautifulSoup(str(ul), 'html.parser')
        lis = newsoup.find_all('li')
        
        row_list_data = []
        for li in lis:
            #print(li.text)
            newsoup2 = BeautifulSoup(str(li), 'html.parser')
            booking_status = newsoup2.find('a')

            if booking_status.text != " NA ":
                #print(booking_status.text, end =" ")
                if booking_status.text.strip() != "Booked":
                    #os.system('python play_alarm.py -d 4 alarm_trim.wav')
                    playsound("alarm_trim.wav")

                vaccine_name = newsoup2.find("div", {"class": "vaccine-cnt"})
                #print(vaccine_name.text, end =" ")

                vaccine_age = newsoup2.find("span", {"class": "age-limit"})
                #print(vaccine_age.text, end =" ")
            
                row_list_data.append(booking_status.text + "_" + vaccine_name.text + "_" + vaccine_age.text)
            else:
                row_list_data.append("NA");
        new_row = {'Center': vaccine_centers[row_count] , dates[1]:row_list_data[0],dates[2]:row_list_data[1],dates[3]:row_list_data[2],dates[4]:row_list_data[3],dates[5]:row_list_data[4],dates[6]:row_list_data[5],dates[7]:row_list_data[6]}

        df_vaccine = df_vaccine.append(new_row,ignore_index=True)
        row_count = row_count + 1

    print(df_vaccine)
    #time.sleep(100)



while(1):
    startCowinDriver()
    time.sleep(60)