from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions  
from playsound import playsound
import os

from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import os
import time
import pandas as pd

def setupCowinDriver():
    global driver
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


def startCowinDriver():
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
    #columns per row 7
    uls = soup.find_all("ul", {"class": "slot-available-wrap"})
    row_count = 0

    #Ignore Centers
    ignore_centers = []

    #ignore_centers.append("APOLLO HOSPITAL 1 Paid")
    

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
                    if vaccine_centers[row_count].strip() not in ignore_centers:
                        print("Playing Alarm!!!!")
                        playsound("alarm_trim.wav")
                        os.system("python test_chromecast.py")
                    else:
                        print(vaccine_centers[row_count].strip(), " ignored")

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



setupCowinDriver()

while(1):
    startCowinDriver()
    time.sleep(1)