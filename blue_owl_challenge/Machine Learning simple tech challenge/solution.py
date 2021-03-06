# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %autosave 0

# ideas:
# 1. data processing - one hot encoding, normalization
# 2. quick EDA
# 3. set up cv5
# 4. get a baseline performance by using the data as it is with a few models (lr, svm, random forest, lda)
# 5. feature engineering and re-train
# 6. use XGboost

# # Data import and cleaning

train_path = "data/train.csv"
test_path = "data/test.csv"

import numpy as np
import pandas as pd

# # simple EDA

import matplotlib.pyplot as plt

train_df = pd.read_csv(train_path)

test_df = pd.read_csv(test_path)

train_df.head()

train_df.describe()

train_df.info()

train_df['outcome'].value_counts()

train_df.hist(figsize=(12,8))
plt.show()

# **Observations**
# - age is evenly dsitributed
# - cost of ad has flat right end
# - launch location is binary/categorical, balanced
# - income is normally distributed
# - no. of driver, 1 or 2, balanced
# - vehicles own: 1-3
# - outcome: mostly negative, imbalance: stratified split
# - prior tenure: unsure about the meaning
#
# **What can be done**
# - Create new features to reflect the income level/financial stability (no. vehicles/driver)
#

# # Data preprocessing

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# +
cat_features = ['device_type', 'gender', 'in_initial_launch_location']

def data_preprocessing(data, use_scale=False, scale=None, onehot=True):
    data['gender'].fillna(data['gender'].mode().iloc[0], inplace=True)
    
    if onehot: 
        one_hot = OneHotEncoder(sparse=False)
        one_hot.fit(data['in_initial_launch_location'].values.reshape(-1,1))
        location_onehot = one_hot.fit_transform(data['in_initial_launch_location'].values.reshape(-1,1))
        data = data.join(pd.DataFrame(location_onehot, columns=['location_onehot1','location_onehot2'])).drop('in_initial_launch_location',axis=1)

        one_hot = OneHotEncoder(sparse=False)
        device_onehot = one_hot.fit_transform(data['device_type'].values.reshape(-1,1))
        data = data.join(pd.DataFrame(device_onehot, columns=['device_onehot1','device_onehot2','device_onehot3','device_onehot4','device_onehot5'])).drop('device_type',axis=1)

        one_hot = OneHotEncoder(sparse=False, handle_unknown='ignore')
        gender_onehot = one_hot.fit_transform(data['gender'].values.reshape(-1,1))
        data = data.join(pd.DataFrame(gender_onehot, columns=['gender_onehot1','gender_onehot2'])).drop('gender',axis=1)
        
    else:
        ord_encoder = OrdinalEncoder()
        ords = pd.DataFrame(ord_encoder.fit_transform(train_df[cat_features]), columns = cat_features)
        data[cat_features] = ords
        
    if use_scale and scale!=None:
        data = pd.DataFrame(scale.fit_transform(data.iloc[:,0:6]), columns = data.iloc[:,0:6].columns).join(data.iloc[:,6:])

    return data


# -

train = data_preprocessing(train_df, use_scale=True, scale=MinMaxScaler(), onehot=True)
train.head()

train.hist(figsize=(12,8))
plt.show()

# # Model comparison

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import cross_val_score

X = train.drop('outcome', axis=1)
y = train['outcome']

# +
#X.drop(["device_onehot1","device_onehot2","device_onehot3","device_onehot4",'device_onehot5'], axis=1, inplace=True)
# -

model_dict = {'lr': LogisticRegression(max_iter=200),
              'svm': SVC(), 
              'cart': DecisionTreeClassifier(), 
              'rf': RandomForestClassifier(),
              'ldr': LinearDiscriminantAnalysis()
             }

# +
cv_scores = []
for i, model in enumerate(model_dict):
    cv_score = cross_val_score(model_dict[model],X, y, scoring='roc_auc', cv=5)
    cv_scores.append(cv_score)
    
cv_scores = pd.DataFrame(cv_scores, index=list(model_dict.keys()))
cv_scores.mean()
# -

cv_score = cross_val_score(LogisticRegression(max_iter=200), X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(SVC(),X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(DecisionTreeClassifier(), X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(RandomForestClassifier(n_estimators=500, random_state=42),X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(LinearDiscriminantAnalysis(), X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

# **observation**: 
# - lr is sensitive to feature scaling, rf is not so much
# - minmax scaling is better
# - onehot encoding gives better results

# # Feature engineering

train_more_features = data_preprocessing(train_df, use_scale=False, scale=MinMaxScaler())
train_more_features['cost/driver'] = train_more_features['cost_of_ad']/train_more_features['n_drivers']
train_more_features['cost/vehicle'] = train_more_features['cost_of_ad']/train_more_features['n_vehicles']
train_more_features['income/driver'] = train_more_features['income']/train_more_features['n_drivers']
train_more_features['income/vehicle'] = train_more_features['income']/train_more_features['n_vehicles']
train_more_features['vehicle/driver'] = train_more_features['n_vehicles']/train_more_features['n_drivers']
train_more_features.head()

num_features = [0,1,2,3,4,5,-5,-4,-3,-2,-1]
scale = MinMaxScaler()
train_more_features.iloc[:, num_features] = pd.DataFrame(scale.fit_transform(train_more_features.iloc[:,num_features]), columns = train_more_features.iloc[:,num_features].columns)
train_more_features.head()

X = train_more_features.drop('outcome', axis=1)
y = train_more_features['outcome']

cv_score = cross_val_score(LogisticRegression(),X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(RandomForestClassifier(n_estimators=500, random_state=42),X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

cv_score = cross_val_score(LinearDiscriminantAnalysis(),X, y, scoring='roc_auc', cv=5)
print(f"scores:{cv_score}, \n mean:{cv_score.mean()}")

# **observation**: 
# - several engieered features are effective to lr

# # Train test split training

# +
from sklearn.model_selection import StratifiedShuffleSplit

split = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
for train_index, test_index in split.split(X, y):
    strat_train_set = train.loc[train_index]
    strat_test_set = train.loc[test_index]
# -

X_train = strat_train_set.drop('outcome', axis=1)
y_train = strat_train_set['outcome']
X_test = strat_test_set.drop('outcome', axis=1)
y_test = strat_test_set['outcome']

from sklearn import metrics


def train_model(model, x_train, y_train, x_test, y_test):
    model.fit(x_train, y_train)
    
    y_pred = model.predict(x_test)
    y_scores = model.predict_proba(x_test)

    return model, metrics.roc_auc_score(y_test, y_scores[:,1])


_, auc = train_model(LogisticRegression(), X_train, y_train, X_test, y_test)
print(auc)

_, auc = train_model(SVC(probability=True), X_train, y_train, X_test, y_test)
print(auc)

_, auc = train_model(DecisionTreeClassifier(), X_train, y_train, X_test, y_test)
print(auc)

rf, auc = train_model(RandomForestClassifier(n_estimators=500, random_state=42), X_train, y_train, X_test, y_test)
print(auc)

pd.DataFrame(rf.feature_importances_, index = train.drop('outcome', axis=1).columns).sort_values(by=[0], ascending=False)

_, auc = train_model(LinearDiscriminantAnalysis(), X_train, y_train, X_test, y_test)
print(auc)


def zero_classifier(X):
    return np.zeros(len(X))


zero_classifier(X_test)

metrics.roc_auc_score(y_test, zero_classifier(X_test))

from sklearn.model_selection import cross_val_predict

# +
from sklearn.metrics import roc_curve

model_dict = {'lr': LogisticRegression(),
              'svm': SVC(probability=True), 
              'cart': DecisionTreeClassifier(), 
              'rf': RandomForestClassifier(),
              'ldr': LinearDiscriminantAnalysis(),
             }

fprs = []
tprs = []

for i, model in enumerate(model_dict):
    y_scores = cross_val_predict(model_dict[model], X_train, y_train, cv=3, method="predict_proba")[:, 1]
    fpr, tpr, thresholds = roc_curve(y_train, y_scores)
    fprs.append(fpr)
    tprs.append(tpr)


# +
def plot_roc_curve(fpr, tpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')

for i, model in enumerate(model_dict):
    plot_roc_curve(fprs[i], tprs[i], model)
    
plt.legend()
plt.show()

# -

# # Grid search

from sklearn.model_selection import GridSearchCV

RandomForestClassifier()

param_grid = [{'n_estimators': [50, 100, 200], 'max_features': np.arange(3,16,3)},
              
             ]
rf = RandomForestClassifier()
grid_search = GridSearchCV(rf, param_grid, cv=5,
                           scoring='roc_auc', verbose=2, n_jobs=8)
grid_search.fit(X, y)


grid_search.best_params_

grid_search.best_estimator_

cvres = grid_search.cv_results_

for mean_score, params in zip(cvres['mean_test_score'], cvres['params']):
    print(mean_score, params)

# # XGboost

from xgboost import XGBClassifier

# +
#early stopping strategy
my_model = XGBClassifier(n_estimators=100, learning_rate=0.3)

my_model.fit(X_train, y_train,
             early_stopping_rounds=5,
            eval_set=[(X_test, y_test)])

y_scores = my_model.predict_proba(X_test)
metrics.roc_auc_score(y_test, y_scores[:,1])
# -

# **Early stopping observation**
# - Stop at about 15 iterations with learning rate = 0.3

# +
#use original train data
X = train.drop('outcome', axis=1)
y = train['outcome']

split = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)

for train_index, test_index in split.split(X, y):
    strat_train_set = train.loc[train_index]
    strat_test_set = train.loc[test_index]
    
X_train = strat_train_set.drop('outcome', axis=1)
y_train = strat_train_set['outcome']
X_test = strat_test_set.drop('outcome', axis=1)
y_test = strat_test_set['outcome']

# +
cv_score = cross_val_score(XGBClassifier(n_estimators=15, learning_rate=0.3, random_state=42), X, y, scoring='roc_auc', cv=5)
print(f"cv scores (auc):{cv_score}, \n mean:{cv_score.mean()}")

xg, auc = train_model(XGBClassifier(n_estimators=15, learning_rate=0.3), X_train, y_train, X_test, y_test)
print(f"\nsingle split auc: {auc}")
# -

pd.DataFrame(xg.feature_importances_, index = X.columns).sort_values(by=[0], ascending=False)

# +
#use train data with more features
X = train_more_features.drop('outcome', axis=1)
y = train_more_features['outcome']

split = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)

for train_index, test_index in split.split(X, y):
    strat_train_set = train_more_features.loc[train_index]
    strat_test_set = train_more_features.loc[test_index]
    
X_train = strat_train_set.drop('outcome', axis=1)
y_train = strat_train_set['outcome']
X_test = strat_test_set.drop('outcome', axis=1)
y_test = strat_test_set['outcome']

# +
cv_score = cross_val_score(XGBClassifier(n_estimators=15, learning_rate=0.3, random_state=42), X, y, scoring='roc_auc', cv=5)
print(f"cv scores (auc):{cv_score}, \n mean:{cv_score.mean()}")

xg, auc = train_model(XGBClassifier(n_estimators=15, learning_rate=0.3), X_train, y_train, X_test, y_test)
print(f"single split auc: {auc}")
# -

pd.DataFrame(xg.feature_importances_, index = X.columns).sort_values(by=[0], ascending=False)

# +
from sklearn.metrics import roc_curve

model_dict = {'lr': LogisticRegression(),
              'svm': SVC(probability=True), 
              'cart': DecisionTreeClassifier(), 
              'rf': RandomForestClassifier(),
              'ldr': LinearDiscriminantAnalysis(),
              'xgb': XGBClassifier(n_estimators=15, learning_rate=0.3)
             }

fprs = []
tprs = []

for i, model in enumerate(model_dict):
    y_scores = cross_val_predict(model_dict[model], X_train, y_train, cv=3, method="predict_proba")[:, 1]
    fpr, tpr, thresholds = roc_curve(y_train, y_scores)
    fprs.append(fpr)
    tprs.append(tpr)

# +
for i, model in enumerate(model_dict):
    plot_roc_curve(fprs[i], tprs[i], model)
    
plt.legend()
plt.show()

# -


