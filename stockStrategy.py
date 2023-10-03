import matplotlib.pyplot as plt
import stockData
import talib.abstract as ta
from talib import MA_Type
from tradingStatment import Transaction, TradingStatement

class StockStrategy:
    def __init__(self, stock_data, char_dir):
        self.stock_data_ = stock_data
        self.char_dir_ = char_dir

    # 전략 만들기
    def make_indicators(self, idx):
        sd = self.stock_data_
        lenth = len(sd.chart_data_)
        if idx > 0:
            if lenth < idx:
                return None
            df = sd.chart_data_[:idx]  
        else:
            df = sd.chart_data_
        return df

    # 매수 가격인가?
    def bid_price(self, candle):
        pass

    # 매도 가격인가?
    def ask_price(self, candle):
        pass
    
    def back_test(self, balance = 0, kelly_rate = 0):
        df = self.stock_data_.chart_data_
        trading_statement = TradingStatement(sd=self.stock_data_, trading=self, balance=balance, kelly_rate=kelly_rate)
        transaction = Transaction()
        
        state = stockData.TradingState.BUY
        lenth = len(df)
        # data 는 1년 후 (working 220일) 지표가 정상적으로 로딩 된다
        for idx in range(220, lenth, 1):
            df = self.make_indicators(idx)
            if df is None:
                break
            candle = df.iloc[-1]
            
            if state == stockData.TradingState.BUY:
                if self.bid_price(candle):
                    bat_money = balance * min([kelly_rate, 1.0])
                    amount = transaction.set_bid(candle, bat_money)
                    if amount >= 1:
                        state = stockData.TradingState.SELL
                        if balance > 0:
                            balance = balance - (amount * candle["Close"])
                        
            elif state == stockData.TradingState.SELL:
                if self.ask_price(candle):
                    state = stockData.TradingState.BUY
                    transaction.set_ask(candle)
                    trading_statement.add_transaction(transaction)
                    if balance > 0:
                        balance = balance + transaction.calc_final_money()

                    trading_statement.set_balance(balance)

                    transaction = Transaction()
                    
        return trading_statement
        

    # 차트 출력해서 맞는지 검증
    def print_chart(self):
        pass

