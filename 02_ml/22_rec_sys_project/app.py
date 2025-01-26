import os
import random
from typing import List

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from fastapi import FastAPI
from schema import PostGet
from datetime import datetime


engine = create_engine(
    "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
    "postgres.lab.karpov.courses:6432/startml"
)

# getting path to a model
def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":
        model_path = '/workdir/user_input/model'
    else:
        model_path = path
    return model_path


# loading the model
def load_models():
    model_path = get_model_path("/Users/nikitin_a/PycharmProjects/l22_rec_sys/catboost_model.cbm")
    from catboost import CatBoostClassifier
    loaded_model = CatBoostClassifier()
    loaded_model.load_model(model_path)
    return loaded_model


# loading data from PostgresSQL db in batches
def batch_load_sql(query: str) -> pd.DataFrame:
    chunksize = 200000
    engine = create_engine(
        "postgresql://robot-startml-ro:pheiph0hahj1Vaif@"
        "postgres.lab.karpov.courses:6432/startml"
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    cnt = 0
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=chunksize):
        chunks.append(chunk_dataframe)
        cnt += chunksize
        #print(f'lines loaded: {cnt}')
    conn.close()
    return pd.concat(chunks, ignore_index=True)


# loading users data
def load_users() -> pd.DataFrame:
    query = 'SELECT * FROM "user_data"'
    loaded_users_df = batch_load_sql(query)
    return loaded_users_df


# loading users likes data
def load_liked() -> pd.DataFrame:
    query = "SELECT user_id, post_id FROM feed_data WHERE action = 'like'"
    loaded_likes_df = batch_load_sql(query)
    return loaded_likes_df


# loading the model
model = load_models()

# loading dataframe with features, likes and posts
users_df = load_users()

# loading posts dataframe
posts_df = pd.read_sql('SELECT * FROM "post_text_df"', con=engine)

# loading posts features (tf-idf --> PCA)
posts_df_pca = pd.read_sql('SELECT * FROM "post_text"', con=engine)

# loading likes data
likes_df = load_liked()

# initialize a FastAPI application instance
app = FastAPI()


@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(
        id: int,
        time: datetime,
        limit: int = 10) -> List[PostGet]:

    # filtering user data based on id input from endpoint parameters
    user_df = users_df[users_df['user_id'] == id]

    # users features engineering step
    bins = [0, 18, 30, 45, 60, np.inf]
    labels = [18, 30, 45, 60, 99]
    user_df['age_category'] = pd.cut(user_df['age'], bins=bins, labels=labels, right=False)
    user_df.drop(['age'], axis=1, inplace=True)
    user_df.reset_index(drop=True, inplace=True)

    # timestamp features engineering step
    user_features_df = pd.DataFrame([{'timestamp': time}])
    user_features_df['month'] = user_features_df['timestamp'].dt.month
    user_features_df['day'] = user_features_df['timestamp'].dt.day
    user_features_df['day_of_week'] = user_features_df['timestamp'].dt.dayofweek
    user_features_df['hour_of_day'] = user_features_df['timestamp'].dt.hour

    # merging features to make predictions
    user_features_df = pd.concat([user_features_df, user_df], axis=1)
    user_features_df = user_features_df.merge(posts_df_pca, how='cross')
    user_features_df.drop(['timestamp'], axis=1, inplace=True)

    # defining a dictionary to map columns to their optimized data types
    dtype_mapping = {
        'month': 'int8',  # month ranges from 1 to 12
        'day': 'int8',  # day ranges from 1 to 31
        'day_of_week': 'int8',  # day_of_week ranges from 0 to 6
        'hour_of_day': 'int8',  # hour_of_day ranges from 0 to 23
        'gender': 'object',  # gender is binary or small range
        'country': 'object',  # country is categorical
        'city': 'object',  # city is categorical
        'exp_group': 'object',  # exp_group is likely a small range
        'os': 'object',  # os is categorical
        'source': 'object',  # source is categorical
        'age_category': 'int8',  # age_category is likely a small range
        'topic': 'object',  # topic is categorical
        'PCA_1': 'float16',  # float16 is sufficient for PCA components
        'PCA_2': 'float16',  # float16 is sufficient for PCA components
        'PCA_3': 'float16',  # float16 is sufficient for PCA components
        'PCA_4': 'float16',  # float16 is sufficient for PCA components
        'PCA_5': 'float16'  # float16 is sufficient for PCA components
    }

    # converting columns to optimized data types
    user_features_df = user_features_df.astype(dtype_mapping)

    # making predictions
    y_pred_proba = model.predict_proba(user_features_df.drop(['user_id', 'post_id'], axis=1))
    y_pred_proba_positive = y_pred_proba[:, 1]

    # adding a column with likes probabilities
    user_df = user_features_df
    user_df['probability'] = y_pred_proba_positive

    # taking into account posts that the user has already liked
    user_likes = likes_df[likes_df['user_id'] == id].post_id.to_list()
    filtered_df = user_df[~user_df['post_id'].isin(user_likes)]
    filtered_df = filtered_df.sort_values('probability', ascending=False) \
        .drop_duplicates(subset='post_id', keep='first')

    # filtering only top-n posts according to input endpoint `limit` parameter
    top_posts_ids = filtered_df.head(limit).post_id.to_list()

    # in case there is no predictions for the user, we will show him overall top-n posts
    if len(top_posts_ids) < limit:
        random_items = limit - len(top_posts_ids)
        most_likes_posts = [1141, 1634, 1707, 1883, 1685, 1857, 1479, 1508, 1572, 1760,
                            1916, 1686, 1361, 3404, 1829, 1776, 1819, 1461, 1460, 1902]
        most_likes_filt = [i for i in most_likes_posts if i not in user_likes]
        top_posts_ids.extend(random.sample(most_likes_filt[:limit], k=random_items))

    # querying posts data based on the top_posts like probabilities
    top_posts_df = posts_df.query('post_id in @top_posts_ids')
    top_posts_df['user_id'] = id

    # returning results
    result = [
        PostGet(
            id=row['post_id'],
            text=row.get('text', ''),
            topic=row.get('topic', '')
        )
        for _, row in top_posts_df.iterrows()
    ]

    return result
