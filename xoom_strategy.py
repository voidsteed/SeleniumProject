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

#---------------------------------Xoom-------------------------------------------------------

class XO_Strategy(Parsing_Strategy):
  def __init__(self, origin_country, destination_country, amount, pay_method, receive_method):
    super(XO_Strategy, self).__init__()
    self._url = 'https://www.xoom.com/send/getstarted'
    self._origin = origin_country
    self._d_country = destination_country
    self._amount = amount
    self._pay_method = pay_method
    self._receive_method = receive_method
    self._map = lib_config_data.get_country_iso_codes()
    self._d_country_drop = "div.countryItem#" + self._d_country


  def s_action(self):
    """
    Selenium action. Using selenium to automate the actions on target website
    """
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    driver.get(self._url)
    # First dropdown list to choose country
    time.sleep(5)
    dropdown_country = driver.find_element_by_class_name("countryPulldown")
    country_div = driver.find_element_by_css_selector(self._d_country_drop)
    # dropdown click and select country
    dropdown_country.click()
    time.sleep(10)
    country_div.click()
    time.sleep(5)
    # Click continue button
    driver.find_element_by_css_selector("button.ui-action-tag.action-primary").click()
    time.sleep(5)
    # Sending amount
    amount = driver.find_element_by_id('sendAmount')
    amount.click()
    amount.clear()
    amount.click()
    amount.send_keys(self._amount)
    time.sleep(5)
    driver.find_element_by_css_selector("button.ui-action-tag.action-primary").click()
      
    # Receiving option, possible to raise NoSuchElementException
    try:
      time.sleep(5)
      pick_up = driver.find_element_by_id("pickup")
      deposit = driver.find_element_by_id("deposit")
      if self._receive_method.upper() == "PICK UP":
        pick_up.click()
      elif self._receive_method.upper() == "DEPOSIT":
        deposit.click()
      driver.find_element_by_css_selector("button.ui-action-tag.action-primary").click()
    except NoSuchElementException:
      driver.find_element_by_css_selector("button.ui-action-tag.action-primary").click()
      
    # Pay method radio button, possible to raise NoSuchElementException
    try:
      time.sleep(5)
      back_account = driver.find_element_by_css_selector("#checking.custom-radio.custom-radio-large")
      debit = driver.find_element_by_css_selector("#debit.custom-radio.custom-radio-large")
      if self._pay_method.upper() == "BANK ACCOUNT":
        back_account.click()
      elif self._pay_method.upper() == "DEBIT / CREDIT CARD":
        debit.click()
    except NoSuchElementException:
      self._page_source = None
      driver.quit()
      return self._page_source

    self._page_source = driver.page_source
    driver.quit()
    return self._page_source


  def parse(self):
    data_object = {}
    date = time.strftime("%x")
    if self._page_source == None:
      data_object['Date'] = date
      data_object['Travel Agency'] = "XOOM"
      data_object['From Currency'] = None
      data_object['To Currency'] = None
      data_object['Pay Method'] = self._pay_method
      data_object['Receive Method'] = self._receive_method
      data_object['Sending Amount'] = self._amount
      data_object['Fee'] = None
      data_object['Exchange Rate'] = None
      data_object['Origin Country'] = self._origin
      data_object['Destination Country'] = self._d_country
      self._data = data_object
      return self._data
    else:
      soup = BeautifulSoup(self._page_source)
      try:# Handle the error countries cannot send their own currency. Example: CO
        from_currency = soup.find('dl',id='rec-fx').find_all('small')[0].text.strip()
        to_currency = soup.find('dl',id='rec-fx').find_all('small')[1].text.strip()
        exchange_rate = soup.find('dl',id='rec-fx').find('dd',class_='data-value nobr').text.split('=')[1].replace(to_currency,'').replace(',','').strip()
      except AttributeError:
        from_currency = "USD"
        to_currency = "USD"
        exchange_rate = float(1)

      pay_method = soup.find('dl',id='rec-payment').find('dd').text.strip()
      sending_amount = soup.find('span',id='sendamtreceipt').text.replace(',','').strip()
      service_fee = soup.find('dl',id='rec-fee').find('dd').find('span',id='fee').text.replace(',','').strip()
      
      # Store infos into dict
      data_object['Date'] = date
      data_object['Travel Agency'] = "XOOM"
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
