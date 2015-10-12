class records_money_transfer_rate(dataset_record):
  class Meta:
    managed = True
    unique_together = ('dataset','time','origin_country','dest_country','sending_amount','pay_method','from_currency','to_currency')
    verbise_name = 'Money Transfer Rate'

  dataset = models.ForeignKey('datalab.dataset')

  time = models.DateTimeField(verbose_name="Date")
  travel_agency = models.CharField(max_length=64, verbose_name="Travel Agency")
  origin_country = models.CharField(max_length=64, verbose_name="Origin Country")
  dest_country = models.CharField(max_length=64, verbose_name="Destination Country")
  sending_amount = models.FloatField(null=True,verbose_name="Sending Amount", unit='number')
  transaction_fee = models.FloatField(null=True,verbose_name="Trasaction Fee", unit='number')
  pay_method =  models.CharField(max_length=64, null=True,verbose_name="Pay Method")
  receive_method =  models.CharField(max_length=64, null=True,verbose_name="Receive Method")#Now default=bank account
  from_currency = models.CharField(max_length=64, null=True,verbose_name="From Currency")
  to_currency = models.CharField(max_length=64, null=True,verbose_name="To Currency")
  exchange_rate = models.FloatField(null=True,verbose_name="Excange Rate", unit='number')
