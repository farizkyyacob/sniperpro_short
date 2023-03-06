import ccxt
import config
import time
from threading import *
import configparser

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': config.api_key(),
    'secret': config.api_secret(),
    'options': {
        'defaultType': 'future', },
})

#Read config.ini file
config_obj = configparser.ConfigParser()
config_obj.read("configfile.ini")
dcastart = config_obj["dcastart"]

dcastart_num = dcastart["timestampcheck"]


# getting lot
x = exchange.fetch_balance(params={'type': 'future'})
totalmarginbalance = x["total"]["USDT"]
print(totalmarginbalance)

print('Getting your current position mode (One-way or Hedge Mode):')
response = exchange.fapiPrivate_get_positionside_dual()
if response['dualSidePosition']:
    print('You are in Hedge Mode')
else:
    print('You are in One-way Mode')

# lotm =
symbol = 'CRVUSDT'

type = 'market'  # or 'market', other types aren't unified yet
sidelong = 'buy'
sideshort = 'sell'
amountdef = 6  # your amount
paramslong = {
    'positionSide': 'LONG'  # and 'SHORT'
}
paramsshort = {
    'positionSide': 'SHORT'  # and 'SHORT'
}

price = 'null'
"""
#openposition
response = exchange.fapiPrivateV2_get_positionrisk(params={'symbol': symbol})
if(len(response)=0):
    buy_market_order = exchange.create_order(symbol, type, sidelong, amount, price,paramslong)
    #INCLUDE 'price' IF NEEDED
    sell_market_order = exchange.create_order(symbol, type, sideshort, amount, price,paramsshort)

"""

target_tp = 1  # persen dari size
target_tp = target_tp / 100
amount_dca = amountdef
dca = int(dcastart_num)
dca_list = [2,2,2,4,4,8,16,32,64,128]
leverage = 20
selisih = 1  # persen

a = 0

def open_pos():
    # openposition
    buy_market_order = exchange.create_order(symbol, type, sideshort, amountdef, price, paramsshort)


def thread_trade(side, amount):
    global symbol, type, sidelong, amountdef, price, paramslong, sideshort, paramsshort
    # close the order
    paramsclose = {'closePosition': "True", "positionSide": "SHORT"}
    if (side == "buy"):
        print("Close Position")
        # close current pos
        buy_market_order = exchange.create_order(symbol, type, side, amount, price, paramsshort)
        time.sleep(5)
        # open new pos
        #print("Open Position")
        buy_market_order = exchange.create_order(symbol, type, sideshort, amountdef, price, paramsshort)
    # add order
    if (side == "sell"):
        print("Add Position")
        buy_market_order = exchange.create_order(symbol, type, side, amount, price, paramsshort)

print("DCA START : ",dca)
time.sleep(5)
pos = False
tp_price = 0
j = 0
while a < 5:

    response = exchange.fapiPrivateV2_get_positionrisk(params={'symbol': symbol})
    if (len(response) > 0):
        # positionSide Check if LONG position exist
        i = 0
        for data in response:
            if (data["positionSide"] == "SHORT" and abs(float(data["positionAmt"])) > 0):
                j = i
                pos = True
            # print(data)
            i = i + 1
        # print(response[j])
    if (pos == False):
        open_pos()

    if(pos):
        current_size = abs(float(response[j]['positionAmt']) * float(response[j]['entryPrice']))
        current_pnl = float(response[j]['unRealizedProfit'])
        entry_price = float(response[j]['entryPrice'])
        mark_price = float(response[j]['markPrice'])
        amount_token = abs(float(response[j]['positionAmt']))

        # print(response[0])
        # print(response[1])
        print("\n\n#################Position#######################")
        print("Pair %s Last Price %s" % (symbol, mark_price))
        print("Size Token : ", amount_token)
        print("Size USDT : ", current_size)
        print("PnL : ", current_pnl)

        # check condition
        target_tp_amount = current_size * target_tp
        print("Target TP", target_tp_amount)
        if(amount_token > 0):
            tp_price = entry_price - (target_tp_amount / amount_token)
        print("TP Price", tp_price)
        print("Next Averaging : ", (entry_price + (entry_price * (selisih / 100))))
        print("DCA Step : ", dca)
        if (current_pnl > target_tp_amount):
            # close long trade ("sell","LONG",long_amount)
            threadtrade = Thread(target=thread_trade, args=("buy", amount_token))
            threadtrade.start()
        if (mark_price > (entry_price + (entry_price * (selisih / 100)))):
            selisih = selisih + 1
            amount_dca = dca_list[dca] * amountdef
            dca = dca + 1
            threadtrade = Thread(target=thread_trade, args=("sell", amount_dca))
            threadtrade.start()
            # open new trade dca ("buy","LONG",long_amount)
            # update long_target_pnl


    time.sleep(0.5)