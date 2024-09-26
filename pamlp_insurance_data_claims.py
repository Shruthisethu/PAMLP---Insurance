# -*- coding: utf-8 -*-
"""PAMLP - Insurance Data Claims.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lHt0deuSyi88H64Su7-IZ_vC17xDlo3M
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Loading the dataset
data = pd.read_csv("Insurance claims data.csv")

#Viewing the data
data.head()

#Summarising the data
data.info()

#Checking for null values
data.isnull().sum()

#Handling missing values - Numerical data
data['width'] = data['width'].fillna(data['width'].median())

#Handling missing values - Categorical data
data['is_power_steering'] = data['is_power_steering'].fillna(data['is_power_steering'].mode()[0])
data['rear_brakes_type'] = data['rear_brakes_type'].fillna(data['rear_brakes_type'].mode()[0])
data['is_speed_alert'] = data['is_speed_alert'].fillna(data['is_speed_alert'].mode()[0])

#Re-checking for null values
data.isna().sum()

# Starting exploratory Data Analysis

#Visualising target variable
sns.set_style("whitegrid")

#Plot the distribution of the target variable 'claim_status'
plt.figure(figsize=(8, 5))
sns.countplot(x='claim_status', data=data)
plt.title('Distribution of Claim Status')
plt.xlabel('Claim Status')
plt.ylabel('Count')
plt.show()

#Selecting numerical columns for analysis
numerical_columns = ['subscription_length', 'vehicle_age', 'customer_age']

#Plotting distributions of numerical features
plt.figure(figsize=(15, 5))
for i, column in enumerate(numerical_columns, 1):
    plt.subplot(1, 3, i)
    sns.histplot(data[column], bins=30, kde=True)
    plt.title(f'Distribution of {column}')

plt.tight_layout()
plt.show()

#Selecting some relevant categorical columns for analysis
categorical_columns = ['region_code', 'segment', 'fuel_type']

#Plotting distributions of categorical features
plt.figure(figsize=(15, 10))
for i, column in enumerate(categorical_columns, 1):
    plt.subplot(3, 1, i)
    sns.countplot(y=column, data=data, order = data[column].value_counts().index)
    plt.title(f'Distribution of {column}')
    plt.xlabel('Count')
    plt.ylabel(column)

plt.tight_layout()
plt.show()

from sklearn.utils import resample

#Separate majority and minority classes
majority = data[data.claim_status == 0]
minority = data[data.claim_status == 1]

#Handling imbalanced data
#Oversample the minority class
minority_oversampled = resample(minority,
                                replace=True,
                                n_samples=len(majority),
                                random_state=42)

#Combine majority class with oversampled minority class
oversampled_data = pd.concat([majority, minority_oversampled])

#Check the distribution of undersampled and oversampled datasets
oversampled_distribution = oversampled_data.claim_status.value_counts()

oversampled_distribution

#Plotting the distribution of 'customer_age', 'vehicle_age', and 'subscription_length' with respect to 'claim_status'
plt.figure(figsize=(15, 5))

# 'customer_age' distribution
plt.subplot(1, 3, 1)
sns.histplot(data=oversampled_data, x='customer_age', hue='claim_status', element='step', bins=30)
plt.title('Customer Age Distribution')

# 'vehicle_age' distribution
plt.subplot(1, 3, 2)
sns.histplot(data=oversampled_data, x='vehicle_age', hue='claim_status', element='step', bins=30)
plt.title('Vehicle Age Distribution')

# 'subscription_length' distribution
plt.subplot(1, 3, 3)
sns.histplot(data=oversampled_data, x='subscription_length', hue='claim_status', element='step', bins=30)
plt.title('Subscription Length Distribution')

plt.tight_layout()
plt.show()

#Data Pre-processing
from sklearn.preprocessing import LabelEncoder

#Encode categorical variables
le = LabelEncoder()
encoded_data = data.apply(lambda col: le.fit_transform(col) if col.dtype == 'object' else col)

#Separate features and target variable
X = encoded_data.drop('claim_status', axis=1)
y = encoded_data['claim_status']

from sklearn.ensemble import RandomForestClassifier

#Create a random forest classifier model
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X, y)

#Get feature importance
feature_importance = rf_model.feature_importances_

#Create a dataframe for visualization of feature importance
features_df = pd.DataFrame({'Feature': X.columns, 'Importance': feature_importance})
features_df = features_df.sort_values(by='Importance', ascending=False)

# displaying the top 10 important features in asc order
print(features_df.head(10))

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier

#Drop 'Policy_id' column from the data
oversampled_data = oversampled_data.drop('policy_id', axis=1)

#Prepare the oversampled data
X_oversampled = oversampled_data.drop('claim_status', axis=1)
y_oversampled = oversampled_data['claim_status']

#Encoding categorical columns
X_oversampled_encoded = X_oversampled.apply(lambda col: LabelEncoder().fit_transform(col) if col.dtype == 'object' else col)

#Splitting the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_oversampled_encoded, y_oversampled, test_size=0.3, random_state=42)

# #Create and train the Random Forest model
# rf_model_oversampled = RandomForestClassifier(random_state=42)
# rf_model_oversampled.fit(X_train, y_train)

#Model - Decision Tree
from sklearn.tree import DecisionTreeClassifier
# Initializing Decision Tree Classifier
rf_model_oversampled = DecisionTreeClassifier()
# Training the Decision Tree Classifier on the training data
rf_model_oversampled.fit(X_train, y_train)

#Predictions
y_pred = rf_model_oversampled.predict(X_test)

#Classification report
print(classification_report(y_test, y_pred))

#Encoding original imbalanced data
original_encoded = data.drop('policy_id', axis=1).copy()
encoders = {col: LabelEncoder().fit(X_oversampled[col]) for col in X_oversampled.select_dtypes(include=['object']).columns}

for col in original_encoded.select_dtypes(include=['object']).columns:
    if col in encoders:
        original_encoded[col] = encoders[col].transform(original_encoded[col])

#Checking predictions for original imbalanced data
original_encoded_predictions = rf_model_oversampled.predict(original_encoded.drop('claim_status', axis=1))

#Comparing results
comparison_df = pd.DataFrame({
    'Actual': original_encoded['claim_status'],
    'Predicted': original_encoded_predictions
})

print(comparison_df.head(10))

#Visualization
correctly_classified = (comparison_df['Actual'] == comparison_df['Predicted']).sum()
incorrectly_classified = (comparison_df['Actual'] != comparison_df['Predicted']).sum()

classification_counts = [correctly_classified, incorrectly_classified]
labels = ['Correctly Classified', 'Misclassified']

#Create a pie chart
plt.figure(figsize=(8, 8))
plt.pie(classification_counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#FF5733'])
plt.title('Classification Accuracy')
plt.show()