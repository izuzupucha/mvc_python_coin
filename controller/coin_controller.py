import streamlit as st
from config import constants as cons
from model.get_data_model import GetDataModel
from model.analyze_model.analyze_ema_model import AnalyzeEMAModel
from model.analyze_model.analyze_macd_model import AnalyzeMACDModel
from model.analyze_model.analyze_ic_model import AnalyzeICModel
from model.analyze_model.analyze_psar_model import AnalyzePSARModel
from model.analyze_model.analyze_adx_model import AnalyzeADXModel
from model.analyze_model.analyze_bb_model import AnalyzeBBModel
from model.analyze_model.analyze_rsi_model import AnalyzeRSIModel
from model.analyze_model.analyze_obv_model import AnalyzeOBVModel
from model.analyze_model.analyze_kdj_model import AnalyzeKDJModel
from model.calcullate_model.calculate_entry_model import CalculateEntryModel

class CoinController:
    def __init__(self):
        # Khởi tạo các model cần dùng
        data_model = GetDataModel()
        self.ema_model = AnalyzeEMAModel(data_model)
        self.macd_model = AnalyzeMACDModel(data_model)
        self.ic_model = AnalyzeICModel(data_model)
        self.psar_model = AnalyzePSARModel(data_model)
        self.adx_model = AnalyzeADXModel(data_model)
        self.bb_model = AnalyzeBBModel(data_model)
        self.rsi_model = AnalyzeRSIModel(data_model)
        self.obv_model = AnalyzeOBVModel(data_model)
        self.kdj_model = AnalyzeKDJModel(data_model)
        self.calculate_entry_model = CalculateEntryModel(data_model)

    def handle_strategy(self, menu_id, coin_pair=None, interval=None, period=None):        
        # ===== CHỈ BÁO XU HƯỚNG =====
        if menu_id == cons.EMA:
            result = self.ema_model.analyze_ema(coin_pair, interval)
            
        elif menu_id == cons.MACD:
            result = self.macd_model.analyze_macd(coin_pair, interval)
            
        elif menu_id == cons.IC:
            result = self.ic_model.analyze_ic(coin_pair, interval)
            
        elif menu_id == cons.PSAR:
            result = self.psar_model.analyze_psar(coin_pair, interval)
            
        elif menu_id == cons.ADX:
            result = self.adx_model.analyze_adx(coin_pair, interval)

        # ===== CHỈ BÁO XÁC NHẬN =====
        elif menu_id == cons.RSI:
            result = self.rsi_model.analyze_rsi(coin_pair, interval)
            
        elif menu_id == cons.BB:
            result = self.bb_model.analyze_bb(coin_pair, interval)
            
        elif menu_id == cons.OBV:
            result = self.obv_model.analyze_obv(coin_pair, interval)
            
        elif menu_id == cons.KDJ:
            result = self.kdj_model.analyze_kdj(coin_pair, interval)

        # ===== COMBO XÁC NHẬN XU HƯỚNG =====
        #elif menu_id == cons.EMA_MACD_RSI:
        #    result = self.model.analyze_ema_macd_rsi(coin_pair, interval)
            
        #elif menu_id == cons.EMA_20_50_MACD:
        #    result = self.model.analyze_ema_20_50_macd(coin_pair, interval)

        # ===== COMBO ĐẢO CHIỀU =====
        #elif menu_id == cons.RSI_MACD:
        #    result = self.model.analyze_rsi_macd(coin_pair, interval)
            
        #elif menu_id == cons.MACD_SAR_ADX:
        #    result = self.model.analyze_macd_sar_adx(coin_pair, interval)

        # ===== COMBO SCALPING =====
        #elif menu_id == cons.EMA_SAR:
        #    result = self.model.analyze_ema_sar(coin_pair, interval)
            
        #elif menu_id == cons.RSI_Stoch_VWAP:
        #    result = self.model.analyze_rsi_stoch_vwap(coin_pair, interval)
        else:
            result = "Chiến lược chưa hỗ trợ."       
        return result