from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

import pandas as pd

class GetData():
    def __init__(self):
        pass

    def get_states(self):
        """_summary_
            method used to create and return a dictionary of all the states and their corresponding cities
        Returns:
            Dictionary: a dictionary of all the states and their cities used by the website
        """

        dataframe = pd.read_csv('./data/petrol_prices.csv')
        states_list = dataframe['state'].unique()
        dictionary_dict = {}
        temp_dict = {}

        for state in states_list:
            temp_dict[state] = dataframe[dataframe['state'] == state]['city'].to_list()
            dictionary_dict.update(temp_dict)
        return dictionary_dict

    def get_city_and_id(self):
        """_summary_
            creates a csv file for all the cities with their corresponding IDs used by the website.
            the csv needs to be cleaned later, manually. the IDs for quite a lot of city will be duplicate.
            cleaned csv can be found in ./data/
        """

        dictionary_dict = self.get_states()
        driver = webdriver.Edge('./drivers/edge/win64/msedgedriver.exe')
        driver.get('https://www.mypetrolprice.com/')

        fuel_select = Select(driver.find_element(by = By.ID, value = 'DropDownListFuels'))
        fuel_select.select_by_visible_text('Petrol')

        city_id_df = pd.DataFrame()
        for state in dictionary_dict.keys():
            state_select = Select(driver.find_element(by = By.ID, value = 'DropDownListStates'))
            state_select.select_by_visible_text(state)

            for city in dictionary_dict[state]:
                city_textbox = driver.find_element(by = By.ID, value = 'TextBoxSearchCities')
                city_textbox.send_keys(city)
                temp_data = {
                    'state': state, 
                    'id': WebDriverWait(driver, 2000)
                                .until(ec.visibility_of_element_located((By.CLASS_NAME, 'searchDiv')))
                                .get_attribute('id'), 
                    'city': city
                    }
                city_id_df = pd.concat([city_id_df, pd.DataFrame([temp_data])], ignore_index = True)
                
                WebDriverWait(driver, 2000).until(ec.visibility_of_element_located((By.CLASS_NAME, 'searchDiv'))).click()
                city_textbox.clear()
        city_id_df.to_csv('./data/city_ids_test.csv')

    def get_current_prices(self, fuel_type):
        """_summary_
            gets current prices for every city for a specific fuel type and saves it as a csv file.
            few city names to be completed in the csv afterwards are:
                Sant Kabir Nagar (UP),
                Jyotiba Phule Nagar (UP),
                Tarn Taran Sahib (Punjab),
                and Shahid Bhagat Singh Nagar (Punjab).
        Args:
            fuel_type (string): type of fuel to get the data for
        """

        driver = webdriver.Edge('./drivers/edge/win64/msedgedriver.exe')
        driver.get(f'https://www.mypetrolprice.com/{fuel_type}-price-in-india.aspx')

        data_frame = pd.DataFrame()
        select = Select(driver.find_element(by = By.ID, value = 'StateDropDownList'))
        options = select.options

        for i in range (1, len(options) - 1):
            select.select_by_index(i)

            select = Select(WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.ID, 'StateDropDownList'))))
            options = select.options

            outer_class = driver.find_elements(by = By.CLASS_NAME, value = 'SF')
            for sf_class in outer_class:
                city = sf_class.find_elements(by = By.TAG_NAME, value = 'a')[1].text
                price = sf_class.find_element(by = By.CLASS_NAME, value = 'txtC').find_element(by = By.TAG_NAME, value = 'b').text.replace('₹ ', '')
                state = options[i].text

                data = {'country': 'India', 'state': state, 'city': city, 'price': price}
                data_frame = pd.concat([data_frame, pd.DataFrame([data])], ignore_index = True)
        
        driver.close()
        data_frame.to_csv(f'./data/{fuel_type}_prices.csv')

    def get_whole_year_prices_for_city(self, city_id, city_name):
        driver = webdriver.Edge('./drivers/edge/win64/msedgedriver.exe')
        driver.get(f'https://www.mypetrolprice.com/{city_id}/Petrol-price-in-{city_name}')

        year_select = Select(driver.find_element(by = By.CLASS_NAME, value = 'hgt32'))
        year_select.select_by_value('365')

        gv_history = driver.find_elements(by = By.CLASS_NAME, value = 'GVHistory')

        another_dataframe_because_why_not = pd.DataFrame()

        for td in gv_history:
            price = td.find_element(by = By.CLASS_NAME, value = 'GVPrice').text.replace('₹ ', '')
            day = td.find_element(by = By.CLASS_NAME, value = 'HDday').text
            month = td.find_element(by = By.CLASS_NAME, value = 'HDmonth').text
            year = td.find_element(by = By.CLASS_NAME, value = 'HDyear').text
            
            temp_dict = {
                "date": datetime.strptime(f'{day} {month} {year}', '%d %b %Y').date(),
                "price": price
            }

            another_dataframe_because_why_not = pd.concat([another_dataframe_because_why_not, pd.DataFrame([temp_dict])], ignore_index = True)

        return another_dataframe_because_why_not

    def get_whole_year_prices(self):
        state_and_cities = pd.read_csv('./data/city_ids_cleaned.csv')
        for _state in state_and_cities['state'].unique():
            for _, _id, _city in state_and_cities[state_and_cities['state'] == _state][['id', 'city']].itertuples():
                print(f'{_state}, {_city}, {_id}')

                data_frame = self.get_whole_year_prices_for_city(_id, _city)

                _outdir = Path(f'./data/last_years/{_state}')
                _outdir.mkdir(parents=True, exist_ok=True)

                data_frame.to_csv(f'{_outdir}/{_city}.csv')