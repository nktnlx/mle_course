import os
import joblib
import numpy as np


class MlModel:
    def __init__(self, model_path: str):
        self._model = self._load_model(model_path)
        self._scaler = self._load_scaler(model_path)
        self._input_features = ['HadAngina', 'ChestScan', 'GeneralHealth',
                                'AgeCategory', 'DifficultyWalking', 'RemovedTeeth',
                                'HadDiabetes', 'SleepHours', 'IsMale',
                                'WeightInKilograms', 'SmokerStatus', 'HeightInMeters',
                                'AlcoholDrinkers', 'LastCheckupTime', 'PhysicalHealthDays']

    @property
    def input_features(self):
        return self._input_features

    def _load_model(self, model_path: str):
        from catboost import CatBoostClassifier
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(model_path)
        return loaded_model

    def _load_scaler(self, model_path: str):
        scaler_dir = os.path.dirname(model_path)
        scaler_path = os.path.join(scaler_dir, 'scaler.pkl')
        return joblib.load(scaler_path)

    def transform_data(self, data: list) -> list:
        user_data = data.copy()

        # Calculate BMI
        bmi = round(user_data[9] / user_data[11] ** 2, 2)
        user_data.append(bmi)

        # One-hot encode age
        all_age_categories = [
            'Age_25_to_29', 'Age_30_to_34', 'Age_35_to_39',
            'Age_40_to_44', 'Age_45_to_49', 'Age_50_to_54',
            'Age_55_to_59', 'Age_60_to_64', 'Age_65_to_69',
            'Age_70_to_74', 'Age_75_to_79', 'Age_80_or_older'
        ]
        encoded_age_data = {cat: 0 for cat in all_age_categories}
        if user_data[3] != 'Age_18_to_24':
            encoded_age_data[user_data[3]] = 1
        age_data_lst = list(encoded_age_data.values())

        # One-hot encode smoking status
        all_smoking_categories = [
            'Never smoked', 'Smokes_every_day', 'Smokes_some_days'
        ]
        encoded_smoking_data = {cat: 0 for cat in all_smoking_categories}
        if user_data[10] != 'Former smoker':
            encoded_smoking_data[user_data[10]] = 1
        smoking_data_lst = list(encoded_smoking_data.values())

        # One-hot encode checkup status
        all_checkup_categories = [
            'Past_2_years', 'Past_5_years', 'Past_year'
        ]
        encoded_checkup_data = {cat: 0 for cat in all_checkup_categories}
        if user_data[13] != '5_or_more_years_ago':
            encoded_checkup_data[user_data[13]] = 1
        checkup_data_lst = list(encoded_checkup_data.values())

        # Extend with OHE data
        user_data.extend(age_data_lst)
        user_data.extend(smoking_data_lst)
        user_data.extend(checkup_data_lst)

        # Remove original categorical columns
        del user_data[3]
        del user_data[9]
        del user_data[11]

        # Scale features
        input_array = np.array(user_data).reshape(1, -1)
        user_data_scaled = self._scaler.transform(input_array)

        return user_data_scaled

    def predict(self, data: list) -> float:
        X = self.transform_data(data)
        result = self._model.predict_proba(X)
        cardiovascular_probability = float(result[0, 1])
        return cardiovascular_probability
