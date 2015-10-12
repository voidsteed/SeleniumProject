from wu_strategy import WU_Strategy
from mgi_strategy import MG_Strategy
from xoom_strategy import XO_Strategy
from selenium import webdriver

class Money_Transfer_Fee_Query():

  def __init__(self,company,origin,destination,amount,pay_method,receive_method):
    """
    Input:
    company: "wu", "mgi", "xoom"
    payment_method: "Debit / Credit Card" or "Bank Account"
    """
    #@@ Origin is only USA
    self._strategy  = self.dispatch_strategy(company,origin,destination,amount,pay_method,receive_method)
    self._com = company
    self._amount = [50,200,1000]


  def dispatch_strategy(self,company,origin,destination,amount,pay_method,receive_method):
    if company == 'wu':
      instance = WU_Strategy(origin,destination,amount,pay_method,receive_method)
      return instance
    elif company == 'mgi':
      instance = MG_Strategy(origin,destination,amount,pay_method,receive_method)
      return instance
    elif company == 'xoom':
      instance = XO_Strategy(origin,destination,amount,pay_method,receive_method)
      return instance
    return None


  def s_action(self):
    self._strategy.s_action()
    return None

  def get_amount_list(self):
    """
    List of sending amount
    @@ Furture work, will add limit of amount and raise an exception
    """
    return self._amount


  def get_country_list(self):
    """
    Get country list from one strategy
    Input: driver: from selenium webdriver
    Return: List: countries
    """
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
    # When you query with company ticker name, this will choose which method for generating the country list
    if (self._com == 'wu'):
      url = 'https://www.westernunion.com/us/en/send-money/start.html'
      driver.get(url)
      lst = []
      send_box = driver.find_element_by_id("wu-country-list")
      options_country = [x for x in send_box.find_elements_by_tag_name("option")]
      for element in options_country:
        val = element.get_attribute("value")
        # Handle most of the cases
        if val == "-1":
          continue
        elif "US Military Base" in element.text:
          continue
        elif val == "AN":#skip Curacao
          continue
        elif val == "C2":#skip CYPRUS
          continue
        elif val == "CZ":#skip Czech
          continue
        elif val == "TP":#skip East Timor
          continue
        elif val == "ET":#skip Ethiopia
          continue

        """check Niger's condition country code: NE
            RO: romania not right
        """
        lst.append(val)
      driver.quit()
      return lst

    elif self._com == 'mgi':
      url = 'https://www.moneygram.com/wps/portal/moneygramonline/home/sendmoney?CC=US&LC=en-US'
      driver.get(url)
      send_box = driver.find_element_by_css_selector("select.styled.country-1.countryDD.webtrends_dCountry_online")
      options_country_u = [x for x in send_box.find_elements_by_tag_name("option")]
      lst = []
      for element in options_country_u:
        val = element.get_attribute("value")
        if val == "IRQ": # special case
          continue
        lst.append(val)
      driver.quit()
      return lst[1:]

    elif self._com == 'xoom':
      url = 'https://www.xoom.com/send/getstarted'
      driver.get(url)
      lst = []
      send_box = driver.find_element_by_id("country-sel")
      options_country = [x for x in send_box.find_elements_by_class_name("countryItem")]
      for element in options_country:
        if element.get_attribute("id") == "":
          continue
        elif element.get_attribute("id") == "BO":#skip BO, special case: 2 currency need to add try catch later
          continue
        lst.append(element.get_attribute("id"))
      driver.quit()
      return lst[1:]# Get rid of first useless item
    return None
  

  # Data we want
  def parse(self):
    self.s_action()
    return self._strategy.parse()

