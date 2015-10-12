from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains as ac
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import os, sys
import time
import io
import re

from bs4 import BeautifulSoup
import lib_config_data
from money_transfer_interface import Parsing_Strategy

#import django

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__ )), '..', '..','..')
addPaths = [['utilities'], ['thinknum.com']]
for addPath in addPaths:
  path = os.path.join(*([PROJECT_ROOT] + addPath))
  if not path in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'thinknum.settings'

#---------------------------------MoneyGram-------------------------------------------------------

class MG_Strategy(Parsing_Strategy):
  def __init__(self,origin,d_country,amount,pay_method,receive_method):
    super(MG_Strategy, self).__init__()
    self._url = 'https://www.moneygram.com/wps/portal/moneygramonline/home/sendmoney?CC=US&LC=en-US'
    self._origin = origin
    self._d_country = d_country
    self._amount = amount
    self._pay_method = pay_method
    self._receive_method = receive_method
    self._map =lib_config_data.get_country_iso_codes()
    self._d_country_drop = self._d_country
    # Pick up and deposit HTML structure are not the same
    self._pick_up_flag = False#pick up flag for parse()


  def deal_with_receive_drop(self,options):
    """
    Picking item strategy:
    1) Match the receive method (Pick up or Deposit)
    2) Match Pick up: If the item text contains: "any Agent" and the currency is "USD", pick first, return it;
                      else if the item text contains: "any Agent", return it;
                      Otherwise, no pick, return None.
    3) Match Deposit: If item text contains: "MOST BANKS", pick first and return it;
                      else if item text contains: "OTHERBANKS", pick it and return it;
                      else if pick the first occurrance of item
                      otherwise, return None

    Input:  options: list of options for second drop down. 
    Return: String: element value for select_by_value
            Possible to return None
    """
    # ele_flag is to set the first occurrance
    value = None
    receive_method = ""
    # Pick up only select The country currency or USD
    # Otherwise return Null Value
    if self._receive_method.upper() == "PICK UP":
      receive_method = "WILL_CALL"
      self._pick_up_flag = True
      ele_flag = True
      for element in options:
        ele = element.get_attribute("value")
        s = ele.split(":")
        ele_receive_method = s[0]
        ele_currency = s[1]
        if ("any Agent" in element.text.strip()) and (ele_currency == "USD") and (ele_receive_method == receive_method):
          return ele
        elif ("any Agent" in element.text.strip()) and (ele_receive_method == receive_method):
          return ele

    # Deposit find "Most bank" or otherbanks 
    # or first occurrance of country currency 
    # or first occurrance of USD
    elif self._receive_method.upper() == "DEPOSIT":
      receive_method = "BANK_DEPOSIT"
      ele_flag = True
      for element in options:
        ele = element.get_attribute("value")
        s = ele.split(":")
        ele_receive_method = s[0]
        ele_currency = s[1]
        if "MOST BANKS" in element.text.strip():
          return ele
        elif "OTHERBANKS" in element.text.strip():
          return ele
        elif (ele_currency == "USD") and (ele_receive_method == receive_method) and ele_flag:
          ele_flag = False
          value = ele#You cannot return here because you need to keep looking "MOST BANKS" or "OTHERBANKS" first
    return value


  def s_action(self):
    # Could add switch for debugging later
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    driver.get(self._url)
    #-------------First dropdown menu-----------------------
    dropdown_send = Select(driver.find_element_by_css_selector("select.styled.country-1.countryDD.webtrends_dCountry_online"))
    dropdown_send.select_by_value(self._d_country_drop)
    time.sleep(2)#PhantomJS is too fast, it has to sleep

    #-------------Second dropdown menu-----------------------
    select_box = driver.find_element_by_css_selector("select.styled.rOp")
    dropdown_receive = Select(select_box)
    time.sleep(5)#PhantomJS is too fast, it has to sleep
    receive_method = ""
    options = [x for x in select_box.find_elements_by_tag_name("option")][1:]
    #default value pick 1st not matter what
    value = options[0].get_attribute("value")
    new_value = self.deal_with_receive_drop(options)
    if new_value != None:
      value = new_value
    if ("WILL_CALL" in value):
      self._pick_up_flag = True

    try:
      dropdown_receive.select_by_value(value)
      time.sleep(5)#PhantomJS is too fast, it has to sleep
      
      amount = driver.find_element_by_id('viewns_7_G3GH6GA308N2F0IO5DVH5F30I6_:_id0:amount')
      amount.click()
      amount.clear()
      amount.click()
      time.sleep(5)#PhantomJS is too fast, it has to sleep
      amount.send_keys(str(self._amount))
      time.sleep(5)#PhantomJS is too fast, it has to sleep
      
      # Click start button
      driver.find_element_by_id("viewns_7_G3GH6GA308N2F0IO5DVH5F30I6_:_id0:estimateBtn").click()
      time.sleep(10)#PhantomJS is too fast, it has to sleep
    except NoSuchElementException:
        self._page_source = None
        driver.quit()
        return self._page_source
    self._page_source = driver.page_source
    driver.quit()
    return self._page_source


  def parse(self):
    data_object1 = {}
    data_object2 = {}
    date = time.strftime("%x")
    if self._page_source == None:
      data_object['Date'] = date
      data_object['From Currency'] = None
      data_object['To Currency'] = None
      data_object['Pay Method'] = None
      data_object['Receive Method'] = self._receive_method
      data_object['Sending Amount'] = float(self._amount)
      data_object['Fee'] = None
      data_object['Exchange Rate'] = None
      data_object['Origin Country'] = self._origin
      data_object['Destination Country'] = self._d_country
      self._data = data_object
      return self._data
      
    else:
      soup = BeautifulSoup(self._page_source)

      date = time.strftime("%x")
      # Only US now
      from_currency = "USD"
      to_currency = soup.find('div',class_='exchangeHeader').find('strong').find('span',class_='exRate').text.strip().split(" ")  
      to_currency = to_currency[(len(to_currency)-1)]
      # The result will be 2 rows for different pay methods
      row1 = None
      row2 = None
      receive_method = ""
      try:
        if (self._pick_up_flag):
          row1 = soup.find('div',class_='detail sameBox clearfix')
          row2 = soup.find('div',class_='detail econBox clearfix')
          service_fee1 = row1.find('div',class_='alt fee').find('div',class_='feeAmount').text
          service_fee2 = row2.find('div',class_='alt fee').find('div',class_='feeAmount').text
          receive_method = "PICK UP"
        else:
          row1 = soup.find('div',class_='detail bdBox clearfix')
          row2 = soup.find('div',class_='detail bdBoxES clearfix')
          service_fee1 = row1.find('div',class_='alt fee').find('div',class_='feeAmount').getText()
          receive_method = "DEPOSIT"
          service_fee2 = row2.find('div',class_='alt fee').find('div',class_='feeAmount').getText()
        title = soup.find('div',class_='clearfix line')
        exchange_rate = soup.find('div',class_='exchangeHeader').find('strong').find('span',class_='exRate').text.strip().split(" ")[0]
        pay_method1 = row1.find('div',class_='alt pm creditCard').text.strip().upper()
        pay_method2 = row2.find('div',class_='alt pm').text.strip().upper()
      except ValueError: # Exception no service in the country
        service_fee1 = None
        service_fee2 = None
        exchange_rate = None
        pay_method1 = None
        pay_method2 = None

      data_object1['Date'] = date
      data_object1['Travel Agency'] = "MoneyGram"
      data_object1['From Currency'] = from_currency
      data_object1['To Currency'] = to_currency
      data_object1['Pay Method'] = pay_method1
      data_object1['Receive Method'] = receive_method
      data_object1['Sending Amount'] = float(self._amount)
      data_object1['Fee'] = float(service_fee1)
      data_object1['Exchange Rate'] = float(exchange_rate)
      # @@ Country names are 3 letter ones, later change to 2
      data_object1['Origin Country'] = self._origin
      data_object1['Destination Country'] = self.look_up_iso_2(self._d_country)
      
      data_object2['Date'] = date
      data_object2['Travel Agency'] = "MoneyGram"
      data_object2['From Currency'] = from_currency
      data_object2['To Currency'] = to_currency
      data_object2['Pay Method'] = pay_method2
      data_object2['Receive Method'] = receive_method
      data_object2['Sending Amount'] = float(self._amount)
      data_object2['Fee'] = float(service_fee2)
      data_object2['Exchange Rate'] = float(exchange_rate)
      data_object2['Origin Country'] = self._origin
      data_object2['Destination Country'] = self.look_up_iso_2(self._d_country)

      if self._pay_method.upper() == pay_method1:
          self._data = data_object1
      elif self._pay_method.upper() == pay_method2:
          self._data = data_object2
      return self._data


  def look_up_iso_2(self, country_name_3):
    """
    Turn 3-letter country code into 2-letter code
    Input: 3-letter code
    Return: 2-letter code
    """
    country_name_2 = ""
    for row in self._map:
      if row['iso_3'] == country_name_3:
        country_name_2 = row['iso_2']
        return country_name_2
