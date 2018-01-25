#!/usr/bin/env python3

import requests
import logging
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from enum import Enum

from TwitterSentiment import *

logger = logging.getLogger(__name__)


class SentimentSources(Enum):
    TWITTER = 1
    REDDIT = 2


# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or b'').decode()
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode().rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


class TradingBot:
    def __init__(self, product):
        """
        Each instance of this class trades a single product. Create multiple instances to trade more products
        simultaneously.
        """
        self.api_url = 'https://api.gdax.com/'
        self.product = product
        # ./coinbase_keys is not in the repo. Get it out-of-band.
        with open('./coinbase_keys') as coinbase_keys:
            self.auth = CoinbaseExchangeAuth(coinbase_keys.readline().rstrip(), coinbase_keys.readline().rstrip(),
                                             coinbase_keys.readline().rstrip())
        # Print accounts
        r = requests.get(self.api_url + 'accounts', auth=self.auth)
        logger.debug(r.json())

        # Print products
        r = requests.get(self.api_url + 'products', auth=self.auth)
        logger.debug(r.json())

        # Print info about trading `product` on Coinbase. This includes the minimum order size.
        for product_info in r.json():
            if product_info['id'] == self.product:
                logger.debug(product_info)

    def place_order(self, order):
        """
        Place an order.

        Sample order that buys 1 Bitcoin for $2:
        order = {
            'size': 1.0,
            'price': 2.0,
            'side': 'buy',
            'product_id': 'BTC-USD',
        }
        """
        logger.debug(order)
        r = requests.post(self.api_url + 'orders', json=order, auth=self.auth)
        print(r.json())

    def update_balance(self, btc, usd):
        """
        TODO: Move this to a seperate object that can be shared by multiple TradingBots
        """
        self.last_balance_btc = btc
        self.last_balance_usd = usd

    def update_quote(self, quote):
        """
        TODO: We really should keep track of VWAP with a small window size instead, especially for illiquid products.
        However, that has more parameters to tune so it's easier to just use the top-of-book quotes.
        """
        self.last_bid = quote.bid
        self.last_ask = quote.ask

    def signal_sentiment(self, sentiment: float, confidence: float, source):
        """
        Update our best estimate of the general public's sentiment regarding the coin we are trading.

        :param sentiment: float between 0 (negative outlook) and 1 (positive outlook)
        :param confidence: float between 0 (random guess) and 1 (the hivemind has made up its mind)
        :param source: Reddit, Twitter, etc
        """
        self.sentiment = sentiment

    def signal_web_mention(self, product, url, page_rank: float, trading_volume: float):
        """
        Signal that an altcoin was mentioned on an important web page such as an exchange's blog. This often results in
        a price spike.
        :param url:
        :param product: The coin that was mentioned on a web page
        :param page_rank:
        :param trading_volume: If the page belongs to an exchange: USD traded on that exchange. Else: 0.
        :return:
        """
        pass

    def get_new_orders(self):
        """
        :return: A list of orders to be placed immediately
        """
        orders = []
        if self.last_balance_usd > 2:
            match_bid = {
                'size': 0.0001,  # About $2
                'price': self.last_bid,
                'side': 'buy',
                'product_id': self.product,
            }
            orders.append(match_bid)
        if self.last_balance_btc > 0.0001:
            match_ask = {
                'size': 0.0001,  # About $2
                'price': self.last_ask,
                'side': 'sell',
                'product_id': self.product,
            }
            orders.append(match_ask)
        return orders

    def tick(self):
        for order in self.get_new_orders():
            self.place_order(order)


def main():
    logging.basicConfig(level=logging.DEBUG)
    bot = TradingBot(product='BTC-USD')
    bot.update_balance(10, 10)
    start_twitter_sentiment(bot)

    class SampleQuote:
        def __init__(self):
            self.bid = 100
            self.ask = 200

    bot.update_quote(SampleQuote())

    for i in range(3):  # Run for 3 seconds
        bot.tick()
        time.sleep(1)


if __name__ == "__main__":
    main()
