class TradeSettings:

    def __init__(self, ob, pair):
        self.pair = pair
        
        # Basic settings (required)
        self.n_ma = ob.get('n_ma', 12)
        self.n_std = ob.get('n_std', 2.0)
        self.maxspread = ob.get('maxspread', 0.0004)
        self.mingain = ob.get('mingain', 0.0006)
        self.riskreward = ob.get('riskreward', 1.5)

        # ATR settings (with defaults)
        self.atr_multiplier = ob.get('atr_multiplier', 2.0)
        self.atr_period = ob.get('atr_period', 14)
        # self.atr_threshold = ob.get('atr_threshold', 0.001)
        
        # RSI settings (with defaults)
        self.rsi_period = ob.get('rsi_period', 14)
        self.rsi_overbought = ob.get('rsi_overbought', 70)
        self.rsi_oversold = ob.get('rsi_oversold', 30)
        

        


    def __repr__(self):
        return str(vars(self))

    @classmethod
    def settings_to_str(cls, settings):
        ret_str = "Trade Settings:\n"
        for _, v in settings.items():
            ret_str += f"{v}\n"

        return ret_str