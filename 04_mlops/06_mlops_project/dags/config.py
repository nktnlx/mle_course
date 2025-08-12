config = {
    'random_state': 42,
    'data': {
        'test_size': 0.2,
    },
    'rf_params': {
        'n_estimators': [100, 200, 500],
        'criterion': ['squared_error'],
        'max_depth': [None, 10],
        'min_samples_split': [2, 5],
        'max_features': [1, 'sqrt'],
        'random_state': [42],
    },
    'lr_params': {
    'fit_intercept': [True, False],
    'positive': [True, False]
    }
}
