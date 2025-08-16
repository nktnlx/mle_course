class MlModel:
    def __init__(self, model_path: str, prediction_cost: float):
        self._model = self._load_model(model_path)
        self._prediction_cost = prediction_cost
        self._input_features = ['sex', 'age', 'is_alone', 'pclass', 'fare']

    @property
    def prediction_cost(self):
        return self._prediction_cost

    @property
    def input_features(self):
        return self._input_features

    def _load_model(self, model_path: str):
        from catboost import CatBoostClassifier

        loaded_model = CatBoostClassifier()
        loaded_model.load_model(model_path)
        return loaded_model

    def predict(self, data: list) -> float:
        result = self._model.predict_proba(data)
        probability_to_survive = result[1:][0]
        return probability_to_survive
