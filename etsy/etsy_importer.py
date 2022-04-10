import csv
import enum
import re
from os import path
from beancount.core import amount, data
from beancount.ingest import importer
from beancount.core.amount import Amount
from beancount.core.number import ZERO, D
from beancount.utils.date_utils import parse_date_liberally

class Col(enum.Enum):
  DATE = 0     # 'Date'
  TYPE = 1     # 'Type'
  TITLE = 2    # 'Title'
  INFO = 3     # 'Info'
  CURRENCY = 4 # 'Currency'
  AMOUNT = 5   # 'Amount'
  FEES = 6     # 'Fees & Taxes'
  NET = 7      # 'Net'
  STATUS = 8   # 'Status'

class TransactionType(enum.Enum):
  FEE = 'Fee'
  SHIPPING = 'Shipping'
  DEPOSIT = 'Deposit'
  PAYMENT = 'Payment'
  REFUND = 'Refund'
  SALE = 'Sale'
  TAX = 'Tax'

class Importer(importer.ImporterProtocol):
  def __init__(
    self, 
    account,
    currency,
    regexps=None,
    deposit_payee='Owner',
    deposit_account='Assets:Bank:Checking',
    payment_account='Assets:Bank:Checking',
    file_output_account='etsy',
    debug: bool = False,
    filename: str = None):
    """Constructor.

    Args:
      account: An account string, the account to post this to.
      currency: A currency string, the currency of this account.
      regexps: A list of regular expression strings used by identifier mixin
      debug: Whether or not to print debug information
      **kwds: Extra keyword arguments to provide to the base mixins.
    """
    self.currency = currency
    self.debug = debug
    self.account = account
    self.deposit_payee = deposit_payee
    self.deposit_account = deposit_account
    self.payment_account = payment_account
    self.file_output_account = file_output_account
    if debug:
      print('account: {} currency {} regexps {}'.format(account, currency, regexps))
    if filename is not None:
      self.filename = re.compile(filename)

  def name(self):
    return 'etsy'

  def identify(self, file):
    if self.filename:
      return self.filename.search(file.name) is not None
    return False

  def file_account(self, _):
    return self.file_output_account

  def file_date(self, file):
    if file is None:
      return None
    _, last_date = self.get_date_range(file)
    return last_date

  def file_name(self, file):
    base = path.basename(file.name)
    return '{}.beancount'.format(base)

  def extract(self, file):
    entries = []
    reader = iter(csv.reader(open(file.name)))
    # skip header
    next(reader)

    first_row = last_row = None
    for ix, row in enumerate(reader):
      if not row or row[0].startswith('#'):
        continue

      if self.debug:
        print(row)

      if first_row is None:
        first_row = row
      last_row = row

      date = parse_date_liberally(row[Col.DATE.value])
      narration = row[Col.TITLE.value]
      tag = row[Col.INFO.value]
      if tag:
        tags = {tag.replace('#', '')}
      else:
        tags = data.EMPTY_SET
      tx_type = row[Col.TYPE.value]
      if tx_type == TransactionType.DEPOSIT.value:
        payee = self.deposit_payee
      else:
        payee = 'Etsy'

      debit, credit = self.get_row_amounts(row)
      if debit is None and credit is None:
        continue

      meta = data.new_metadata(file.name, ix)

      meta['; original'] = ','.join(row)
      txn = data.Transaction(meta, date, '*', payee, narration, 
        tags, data.EMPTY_SET, [])
      
      if self.debug:
        print('p1: {}, {}, {} [{}]'.format(self.account, debit, credit, tx_type))
      p1 = data.Posting(self.account, debit, None, None, None, None)
      # make other side
      txAccount = 'Expenses:Etsy:{}'.format(tx_type)

      if tx_type == TransactionType.DEPOSIT.value:
        txAccount = self.deposit_account

      elif tx_type == TransactionType.SALE.value:
        txAccount = 'Income:Etsy:Sale'
      
      elif tx_type == TransactionType.FEE.value:
        txAccount = 'Expenses:Etsy:Fees'

      elif tx_type == TransactionType.PAYMENT.value:
        if row[Col.TITLE.value] == 'Card Payment':
          txAccount = self.payment_account
        else:
          txAccount = 'Expenses:Etsy:Fees'
      
      if self.debug:
        print('p2 {}, {}, {}'.format(txAccount, debit, credit))
      p2 = data.Posting(txAccount, credit, None, None, None, None)
      if credit:
        txn.postings.append(p2)
        txn.postings.append(p1)
      else:
        txn.postings.append(p1)
        txn.postings.append(p2)

      entries.append(txn)

    # Figure out if the file is in ascending or descending order.
    first_date = parse_date_liberally(first_row[Col.DATE.value])
    last_date = parse_date_liberally(last_row[Col.DATE.value])
    is_ascending = first_date < last_date

    # Reverse the list if the file is in descending order
    if not is_ascending:
        entries = list(reversed(entries))

    return entries

  def get_account(self, file=None):
    return self.account

  def get_date_range(self, file):
    reader = iter(csv.reader(open(file.name)))
    # skip header
    next(reader)

    first_row = last_row = None
    for row in reader:
      if not row or row[0].startswith('#'):
        continue

      if self.debug:
        print(row)

      if first_row is None:
        first_row = row
      last_row = row

    first_date = parse_date_liberally(first_row[Col.DATE.value])
    last_date = parse_date_liberally(last_row[Col.DATE.value])
    if first_date < last_date:
      return first_date, last_date

    return last_date, first_date

  def get_row_amounts(self, row):
    tx_type = row[Col.TYPE.value]
    if tx_type == TransactionType.DEPOSIT.value:
      raw = row[Col.TITLE.value].split(' ')[0]
    else:
      raw_amount = row[Col.AMOUNT.value]
      raw_fees = row[Col.FEES.value]
      if (raw_fees != '--'):
        raw = raw_fees
      else:
        raw = raw_amount

    if raw:
      raw = raw.replace('$', '')

    value = D(raw)
    debit = credit = None
    debit = value;
    
    return (Amount(debit, self.currency) if debit else None,
            Amount(credit, self.currency) if credit else None)

  def __repr__(self):
    return "Importer for Etsy"

