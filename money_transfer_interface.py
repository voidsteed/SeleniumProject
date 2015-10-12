class Parsing_Strategy(object):
  """
  A base class to create strategy to get money transfer fee data from different website
  """
  def __init__(self):
    self._page_source = None
    self._data = None


  def s_action(self):
    """
    Selenium action. Using selenium to automate the actions on target website
    """
    raise NotImplementedError('Exception raised, ImageFinder is supposed to be an interface / abstract class!')


  def parse(self):
    """
    Using Beautiful Soup to parse page source
    """
    raise NotImplementedError('Exception raised, ImageFinder is supposed to be an interface / abstract class!')
