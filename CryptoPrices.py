
# coding: utf-8

# In[29]:

# Cryptonator scraper that retreives prices of BTC, ETH, LTC, and BCH
# BY AJAY NADHAVAJHALA

import requests

def get_price(coin, base_currency):
    """Returns current price of given coin in the respective currency"""

    try:
        url = "https://api.cryptonator.com/api/ticker/{}-{}".format(
            coin, base_currency)
        request = requests.get(url)
        if request.status_code == 200:
            data = request.json()
    except requests.exceptions.RequestException:
        return "Coin not found"

    if not data['success']:
        raise Exception("Coin not found")
    else:
        return data['ticker']['price']
    
print("bitcoin price: ", get_price("btc", "usd") )
print("ethereum price: ", get_price("eth", "usd") )
print("litecoin price: ", get_price("ltc", "usd") )
print("bitcoin cash price: ", get_price("bch", "usd") )

''' OUTPUT

bitcoin price:  13758.90418896
ethereum price:  712.54817098
litecoin price:  262.97575689
bitcoin cash price:  2680.75930212

'''


# In[ ]:



