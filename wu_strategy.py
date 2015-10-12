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

#import django

PROJECT_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__ )), '..', '..','..')
addPaths = [['utilities'], ['thinknum.com']]
for addPath in addPaths:
  path = os.path.join(*([PROJECT_ROOT] + addPath))
  if not path in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'thinknum.settings'

from bs4 import BeautifulSoup
import lib_config_data
from money_transfer_interface import Parsing_Strategy

#---------------------------------Western Union------------------------------------------------------
class WU_Strategy(Parsing_Strategy):
  """
  Strategy class
  Input: origin country, destination country, sending amount, pay method, receive method
  """
  def __init__(self, origin_country, destination_country, amount, pay_method, receive_method):
    super(WU_Strategy, self).__init__()
    self._url = 'https://www.westernunion.com/us/en/send-money/start.html'
    self._origin = origin_country
    self._d_country = destination_country
    self._amount = amount
    self._pay_method = pay_method
    self._receive_method = receive_method
    self._map = lib_config_data.get_country_iso_codes()
    self._d_country_drop = self._d_country

  # @@ need a map to get country code using lib_config_data
  def is_exist(self,driver,id_):
    """
    Check if the element is exist by id
    """
    try:
      driver.find_element_by_id(id_)
    except NoSuchElementException, e:
      return False
    return True

  def s_action(self):
    """
    Selenium action. Using selenium to automate the actions on target website
    """
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    #driver = webdriver.Firefox()

    driver.get(self._url)
    time.sleep(5)
    # Get the first dropdown list
    dropdown = Select(driver.find_element_by_id("wu-country-list"));
    dropdown.select_by_value(self._d_country_drop)
    time.sleep(10)
    # Send amount to textfield
    amount = driver.find_element_by_id('input-amount-fea')
    amount.click()
    amount.clear()
    amount.send_keys(self._amount)
    # Sending zipcode
    zipcode = driver.find_element_by_id('input-zip-fea')
    # o_country is US
    zipcode.send_keys('10036')
    time.sleep(10)
    # Pick Bank deposit by default
    pick_up = 'receiver_000'
    deposit = 'receiver_500'
    # Both exist
    if self.is_exist(driver,pick_up) and self.is_exist(driver,deposit):
      if self._receive_method.upper() == "PICK UP":
        driver.find_element_by_id(pick_up).click()
      elif self._receive_method.upper() == "DEPOSIT":
        driver.find_element_by_id(deposit).click()
    # Pick up cash exist
    elif self.is_exist(driver,pick_up) and (not self.is_exist(driver,deposit)):
      driver.find_element_by_id(pick_up).click()
    # Deposit exist
    elif not self.is_exist(driver,pick_up) and self.is_exist(driver,deposit):
      driver.find_element_by_id(deposit).click()
    else:# both buttons are not existed, just set page source to empty and return
      self._page_source = None
      driver.quit()
      return self._page_source
    try:
      time.sleep(5)#PhantomJS is too fast
      back_account = driver.find_element_by_css_selector("#opt1payingMethod.pay.ACH")
      credit = driver.find_element_by_css_selector("#opt1payingMethod.pay.CreditCard")
    # If didn't find the button, program will try to find if the other one is there, and click on it
      if self._pay_method.upper() == "BANK ACCOUNT":
        back_account.click()
      elif self._pay_method.upper() == "DEBIT / CREDIT CARD":
        credit.click()
    # If there is no pay method, just return url
    except NoSuchElementException:
      # Pass None to page source
      self._page_source = None
      driver.quit()
      return self._page_source

    self._page_source = driver.page_source
    driver.quit()
    return self._page_source

  def parse(self):
    data_object = {}
    date = time.strftime("%x")
    #check empty case: Israel
    if self._page_source == None:
      data_object['Date'] = date
      data_object['Travel Agency'] = "Western Union"
      data_object['From Currency'] = None
      data_object['To Currency'] = None
      data_object['Pay Method'] = self._pay_method
      data_object['Receive Method'] = self._receive_method
      data_object['Sending Amount'] = float(self._amount)
      data_object['Fee'] = None
      data_object['Exchange Rate'] = None
      data_object['Origin Country'] = self._origin
      data_object['Destination Country'] = self._d_country
      self._data = data_object
      return self._data
    else:
      # Read page source by beautiful soup
      soup = BeautifulSoup(self._page_source)

      from_currency = soup.find('span',id='currency-transfer').text.strip()
      to_currency = soup.find('span',id='currency-receiver').text.strip()
      pay_method = soup.find('p',id='payingWithDesc').text.strip().upper()
      sending_amount = soup.find('span',id='transferAmount').text.strip()
      service_fee = soup.find('span',id='serviceFee').text.strip()
      exchange_rate = soup.find('span',id='exchangeRateCurrency').text.strip()
      #@@ add receive method into dict
      data_object['Date'] = date
      data_object['Travel Agency'] = "Western Union"
      data_object['From Currency'] = from_currency
      data_object['To Currency'] = to_currency
      data_object['Pay Method'] = pay_method.upper()
      data_object['Receive Method'] = self._receive_method
      data_object['Sending Amount'] = float(sending_amount)
      data_object['Fee'] = float(service_fee)
      data_object['Exchange Rate'] = float(exchange_rate)
      data_object['Origin Country'] = self._origin
      data_object['Destination Country'] = self._d_country
      self._data = data_object
      return self._data
