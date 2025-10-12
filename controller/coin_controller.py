from model.coin_model import CoinModel
import streamlit as st
from config import constants as cons
class CoinController:
    def __init__(self):
        self.model = CoinModel()

    def handle_strategy(self, menu_id, coin_pair=None, interval=None, period=None):        
        # ===== CHỈ BÁO XU HƯỚNG =====
        if menu_id == cons.EMA:
            result = self.model.analyze_ema(coin_pair, interval)
            
        elif menu_id == cons.MACD:
            result = self.model.analyze_macd(coin_pair, interval)
            
        elif menu_id == cons.IC:
            result = self.model.analyze_ic(coin_pair, interval)
            
        elif menu_id == cons.PSAR:
            result = self.model.analyze_psar(coin_pair, interval)
            
        elif menu_id == cons.ADX:
            result = self.model.analyze_adx(coin_pair, interval)

        # ===== CHỈ BÁO XÁC NHẬN =====
        elif menu_id == cons.RSI:
            result = self.model.analyze_rsi(coin_pair, interval)
            
        elif menu_id == cons.BB:
            result = self.model.analyze_bb(coin_pair, interval)
            
        elif menu_id == cons.OBV:
            result = self.model.analyze_obv(coin_pair, interval)
            
        elif menu_id == cons.KDJ:
            result = self.model.analyze_kdj(coin_pair, interval)

        # ===== COMBO XÁC NHẬN XU HƯỚNG =====
        elif menu_id == cons.EMA_MACD_RSI:
            result = self.model.analyze_ema_macd_rsi(coin_pair, interval)
            
        elif menu_id == cons.EMA_20_50_MACD:
            result = self.model.analyze_ema_20_50_macd(coin_pair, interval)

        # ===== COMBO ĐẢO CHIỀU =====
        elif menu_id == cons.RSI_MACD:
            result = self.model.analyze_rsi_macd(coin_pair, interval)
            
        elif menu_id == cons.MACD_SAR_ADX:
            result = self.model.analyze_macd_sar_adx(coin_pair, interval)

        # ===== COMBO SCALPING =====
        elif menu_id == cons.EMA_SAR:
            result = self.model.analyze_ema_sar(coin_pair, interval)
            
        elif menu_id == cons.RSI_Stoch_VWAP:
            result = self.model.analyze_rsi_stoch_vwap(coin_pair, interval)
        else:
            result = "Chiến lược chưa hỗ trợ."
        st.success(result)