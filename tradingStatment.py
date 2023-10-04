import stockData
import logger

class Transaction:
    #매수
    def set_bid(self, candle, batting_money = 0):
        self.bid_candle_ = candle
        self.ask_candle_ = None
        if batting_money == 0:
            self.amount_ = 1
        else:
            bid_price = self.bid_candle_["Close"]
            amount = int(batting_money / bid_price)
            if amount <= 0:
                return 0
            self.amount_ = amount

        return self.amount_
    #매도
    def set_ask(self, candle):
        self.ask_candle_ = candle

    def calc_profit(self):
        bid_price = self.bid_candle_["Close"]
        ask_price = self.ask_candle_["Close"]
        profit = ask_price - bid_price
        return profit * self.amount_
    
    def calc_final_money(self):
        ask_price = self.ask_candle_["Close"]
        return ask_price * self.amount_
    
    def calc_profit_rate(self):
        bid_price = self.bid_candle_["Close"]
        ask_price = self.ask_candle_["Close"]
        profit_rate = (ask_price - bid_price) / bid_price
        return profit_rate

class TradingStatement:
    def __init__(self, sd, trading, balance, kelly_rate):
        self.stock_data_ = sd
        self.transctions_ = []
        self.balance_ = balance
        self.trading_ = trading
        self.kelly_rate_ = kelly_rate
        self.trading_name_ = trading.__class__.__name__

    def add_transaction(self, tran):
        self.transctions_.append(tran)

    def total_prtofit(self):
        profit = 0
        for tran in self.transctions_:
            profit += tran.calc_profit()
        return profit

    def total_trading_count(self):
        count = len(self.transctions_)
        return count

    # 승률
    def win_rating(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        win_count = 0
        for tran in self.transctions_:
            if tran.calc_profit() > 0:
                win_count = win_count + 1
        
        win_rate = win_count / trading_count
        return win_rate

    # 수익율
    def profit_rate(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        rate = 0
        for tran in self.transctions_:
            if tran.calc_profit() > 0:
                rate = rate + tran.calc_profit_rate()                
        
        rate = rate / trading_count
        return rate
    
    # 손실율
    def lose_rate(self):
        trading_count = self.total_trading_count()
        if trading_count <= 0:
            return 0
        
        rate = 0
        for tran in self.transctions_:
            if tran.calc_profit() <= 0:
                rate = rate + tran.calc_profit_rate()                
        
        rate = rate / trading_count
        return rate
    
    def set_balance(self, balance):
        self.balance_ = balance
    
    # 해당 전략으로 최적의 배팅 비율을 구한다
    def __kelly_criterion(self, p, profit, loss):
        if loss == 0:
            logger.info("켈리공식으로 손실율 0으론 계산 불가")
            return 0
        
        q = 1 - p
        b = profit / loss  # 이길 때 얻는 이익과 지면 손실 비율의 비율
        f_star = (p * b - q) / b
        return f_star
    
    def optimal_bet_ratio(self):
        win_rate = self.win_rating()
        profit_rate = self.profit_rate()
        lose_rate = self.lose_rate()
        f_star = self.__kelly_criterion(win_rate, profit_rate, lose_rate)
        return f_star

    def log(self):
        trading_count = self.total_trading_count() 
        if trading_count <= 0:
            logger.info("! [%s][%s] 의 백테스팅 거래 없음" % (self.stock_data_.name_, self.trading_name_))                       
            return
        
        win_rate = self.win_rating()
        profit_rate = self.profit_rate()
        lose_rate = self.lose_rate()

        logger.info("! [%s][%s] 의 백테스팅 리포트" % (self.stock_data_.name_, self.trading_name_))
        for tran in self.transctions_:
            bid_candle = tran.bid_candle_
            ask_candle = tran.ask_candle_
            logger.info("- 매수[{0}]:[{1}], 수량[{2}], 매수 금액[{3:,.2f}]"
                        .format(bid_candle["Date"], bid_candle["Close"], tran.amount_, bid_candle["Close"] * tran.amount_))
            logger.info("- 매도[{0}]:[{1}], 수량[{2}], 매도 금액[{3:,.2f}]" 
                        .format(ask_candle["Date"], ask_candle["Close"], tran.amount_, ask_candle["Close"] * tran.amount_))
            logger.info("=> 이익[{0:,.2f}]".format(tran.calc_profit()))

        logger.info("+ [{0}][{1}] 의 승률 {2:.2f}, 거래수 {3}, 총이익 {4:,.2f}]" 
                    .format(self.stock_data_.name_, self.trading_name_, win_rate * 100, trading_count, self.total_prtofit())) 
        logger.info("+ 승률[{0}]%, 수익율[{1:.2f}]%, 손실율[{2:.2f}]% , 최적 배팅 비율[{3:.2f}]%"
                    .format(win_rate, profit_rate, lose_rate, self.kelly_rate_))
        logger.info("! [{0}][{1}] 전략 [{2:.2f}]% 비율 배팅 시뮬시 => 총 금액[{3:,.2f}]"
                    .format(self.stock_data_.name_, self.trading_name_, self.kelly_rate_, self.balance_))
        
