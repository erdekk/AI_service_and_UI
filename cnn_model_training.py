import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

# 데이터 로딩
df = pd.read_csv('dataset_preprocessed.csv')  # 경로를 알맞게 수정하세요
df = df.dropna()

X_raw = df['password'].astype(str).values
y_raw = df['score'].astype(float).values / 100.0  # 0~1로 정규화

# 문자 단위 Tokenizer
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts(X_raw)
X_seq = tokenizer.texts_to_sequences(X_raw)

# 패딩
maxlen = 20  # 최대 길이 설정
X_pad = pad_sequences(X_seq, maxlen=maxlen, padding='post')

# 훈련/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X_pad, y_raw, test_size=0.2, random_state=42)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense

vocab_size = len(tokenizer.word_index) + 1  # 문자 집합 크기

model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=64, input_length=maxlen),
    Conv1D(128, 3, activation='relu'),
    GlobalMaxPooling1D(),
    Dense(64, activation='relu'),
    Dense(1, activation='sigmoid')  # 출력: 0~1 사이 (회귀)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])  # MSE로 학습

model.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test))
loss, mae = model.evaluate(X_test, y_test)
print(f'Test MAE: {mae * 100:.2f}%')  # 정규화 해제
test_pw = ["password123", "4#G8kLs9!", "abc"]
test_seq = tokenizer.texts_to_sequences(test_pw)
test_pad = pad_sequences(test_seq, maxlen=maxlen)
pred = model.predict(test_pad)
print((pred * 100).round(2))  # 0~100 점수로 환산
model.save("password_strength_regression_cnn.h5")

import pickle
with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)
