# Project description   

- `22_rec_sys_project.ipynb` - EDA, features engineering, model fitting and API coding drafts
- `22_rec_sys_fitting_on_kaggle.ipynb` - fitting a `CatBoostClassifier` model using Kaggle Notebook
- `requirements.txt` - lists all the Python packages and their specific versions needed to run the project
- `schema.py` - endpoint validation `pydantic` schema
- `catboost_model.cbm` - the fitted `CatBoostClassifier` model that is used to give recommendations --> [click to download..](https://disk.yandex.ru/d/q7DuSlPDM4CLeg)
- `app.py` - recommendation system `FastAPI` service that gets `user_id` and makes predictions which `post_id` the user will like with a higher probability  

