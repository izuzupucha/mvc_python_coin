from model.get_data_model import GetDataModel

class BaseAnalyzeModel:
    def __init__(self, data_model: GetDataModel):
        self.data_model = data_model