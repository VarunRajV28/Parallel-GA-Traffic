import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

print("Loading traffic data...")
# 1. Load the dataset you just created
df = pd.read_csv('traffic_data.csv')

# We want the LSTM to look at the queues and the accident status to predict the North Queue
features = df[['North_Queue', 'East_Queue', 'Accident_Active']].values

# 2. Scale the Data (Neural Networks love numbers between 0 and 1)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(features)

# 3. Create "Time Sequences" (The core concept of an LSTM)
# We will teach the AI: "Look at the past 10 seconds of traffic to predict the 11th second."
time_steps = 10
X, y = [], []

for i in range(len(scaled_data) - time_steps):
    X.append(scaled_data[i:(i + time_steps)]) # The past 10 seconds
    y.append(scaled_data[i + time_steps, 0])  # The target: North_Queue at the 11th second

X, y = np.array(X), np.array(y)

print(f"Training data shape: {X.shape} (Samples, Time Steps, Features)")

# 4. Build the LSTM Neural Network
print("Building the LSTM model...")
model = Sequential()
# The LSTM layer with 50 'neurons'
model.add(LSTM(units=50, return_sequences=False, input_shape=(X.shape[1], X.shape[2])))
# The output layer (Predicting exactly 1 number: the future queue length)
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# 5. Train the Brain!
print("Training starting... (This might take a minute)")
# Epochs = how many times it reads the dataset. Batch_size = how many rows it memorizes at once.
model.fit(X, y, epochs=20, batch_size=32, verbose=1)

# 6. Save the trained model to your folder
model.save('supervisor_lstm.keras')
print("Training complete. Model saved as 'supervisor_lstm.keras'")