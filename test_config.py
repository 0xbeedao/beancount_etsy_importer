import sys
from os import path
sys.path.insert(0, path.join(path.dirname(__file__)))

from etsy.etsy_importer import Importer as EtsyImporter

class MyStoreImporter(EtsyImporter):
  '''
  Importer for Etsy CSV files, wrapped this way for easy testing.
  '''
  def __init__(self):
    super().__init__(
      'Assets:Etsy',
      'USD',
      [],
      filename=".*etsy.*.csv",
      debug=False,
      deposit_payee='Owner Payout',
      deposit_account='Assets:Bank:OurCreditUnion:BusinessChecking',
      payment_account="Liabilities:CreditCard:Visa",
    )

etsy_importer =  MyStoreImporter();

CONFIG = [etsy_importer]
