class TradeSettings:

    def __init__(self, ob, pair):
        self.pair = pair
        self.n_ma = ob['n_ma']
        self.n_std = ob['n_std']

        self.maxspread = ob['maxspread']
        self.mingain = ob['mingain']

        self.riskreward = ob['riskreward']

        self.atr_multiplier = ob['atr_multiplier']
        self.atr_period = ob['atr_period']
        # self.atr_threshold = ob['atr_threshold']
        
        self.rsi_period = ob['rsi_period']
        self.rsi_overbought = ob['rsi_overbought']
        self.rsi_oversold = ob['rsi_oversold']
        

        


    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str