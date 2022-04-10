Beancount Importer for Etsy Stores
==================================

By DevBruce, for his wonderful wife.

This is a simple importer for the CSV output Etsy gives store owners.  It is not
a very *good* output they give us, but it is enough to convert into Beancount
format.

Basic Config
------------

See `test_config.py` for an example of configuration.  Basically, just put it on your
path, and import like shown in that file.

Example Usage
-------------

`bean-identify test_config.py data/small.csv`

```
**** C:\Users\DevBruce\work\beancount_etsy_importer\data\small.csv
Importer:    etsy
Account:     etsy
```

`bean-extract test_config.py data/small.csv`

```
[...]
2022-01-28 * "Etsy" "Partial refund to buyer for Order #2233445566"
  ; original: "January 28, 2022,Refund,Partial refund to buyer for Order #2233445566,,USD,-$1.91,--,-$1.91"
  Assets:Etsy           -1.91 USD
  Expenses:Etsy:Refund

2022-01-28 * "Etsy" "Credit for processing fee" #Order 2233445566
  ; original: "January 28, 2022,Fee,Credit for processing fee,Order #2233445566,USD,--,$0.06,$0.06"
  Assets:Etsy         0.06 USD
  Expenses:Etsy:Fees

2022-01-28 * "Etsy" "USPS shipping label" #Label 3344556677
  ; original: "January 28, 2022,Shipping,USPS shipping label,Label #3344556677,USD,--,-$14.25,-$14.25"
  Assets:Etsy             -14.25 USD
  Expenses:Etsy:Shipping

2022-01-31 * "Owner Payout" "$15.34 sent to your bank account"
  ; original: "January 31, 2022,Deposit,$15.34 sent to your bank account,,USD,--,--,--"
  Assets:Etsy                                  15.34 USD
  Assets:Bank:OurCreditUnion:BusinessChecking

2022-01-31 * "Etsy" "Listing fee" #Listing 1122334455
  ; original: "January 31, 2022,Fee,Listing fee,Listing #1122334455,USD,--,-$0.20,-$0.20"
  Assets:Etsy         -0.20 USD
  Expenses:Etsy:Fees

2022-03-01 * "Etsy" "Card Payment" #Visa ending in xxxx
  ; original: "March 1, 2022,Payment,Card Payment,Visa ending in xxxx,USD,--,$13.40,$13.40"
  Assets:Etsy                  13.40 USD
  Liabilities:CreditCard:Visa
```

`bean-file test_config.py data/small.csv`

```
Importer:    etsy
Account:     etsy
Date:        2022-03-01 (from contents)
Destination: C:\Users\DevBruce\work\beancount_etsy_importer\etsy\2022-03-01.small.csv.beancount
```

License
-------

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.

Copyright 2022, DevBruce