import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# 모델 및 토크나이저 불러오기
model = load_model('password_strength_regression_cnn.h5')
with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

MAX_LEN = 20

# 전처리 함수
def preprocess_password(password):
    sequence = tokenizer.texts_to_sequences([password])
    padded = pad_sequences(sequence, maxlen=MAX_LEN, padding='post', truncating='post')
    return padded


# 예측 함수
def predict_strength(event=None):
    password = entry.get().strip()

    if not password:
        messagebox.showwarning("입력 오류", "비밀번호를 입력해주세요.")
        return

    if len(password) < 6:
        messagebox.showinfo("입력 안내", "비밀번호는 최소 6자 이상이어야 합니다.")
        return

    processed = preprocess_password(password)
    prediction = model.predict(processed, verbose=0)[0][0]
    percentage = round(prediction * 100, 2)

    # 강도 평가
    if percentage < 40:
        color = "red"
        level = "약함"
        img_key = "weak"
    elif percentage < 70:
        color = "orange"
        level = "보통"
        img_key = "medium"
    else:
        color = "green"
        level = "강함"
        img_key = "strong"

    result_label.config(text=f"🔒 예측 강도: {percentage}% ({level})", fg=color)
    progress_bar['value'] = percentage
    progress_bar.configure(style=f"{level}.Horizontal.TProgressbar")

    # 이미지 업데이트
    image_label.config(image=images[img_key])
    image_label.image = images[img_key]  # 참조 유지


# 입력 초기화 함수
def clear_input():
    entry.delete(0, tk.END)
    result_label.config(text="")
    progress_bar['value'] = 0
    image_label.config(image="")


# 비밀번호 보이기 토글
def toggle_password():
    if show_var.get():
        entry.config(show="")
    else:
        entry.config(show="*")


# 스타일 설정
def setup_styles():
    style = ttk.Style()
    style.theme_use("default")

    style.configure("약함.Horizontal.TProgressbar", troughcolor='white', background='red')
    style.configure("보통.Horizontal.TProgressbar", troughcolor='white', background='orange')
    style.configure("강함.Horizontal.TProgressbar", troughcolor='white', background='green')


# 메인 UI
root = tk.Tk()
root.title("AI 비밀번호 강도 예측기")
root.geometry("480x500")
root.configure(bg="#f0f8ff")
# 이미지 미리 로드
image_paths = {
    "weak": "/UI_pictures/weak.png",
    "medium": "/UI_pictures/medium.png",
    "strong": "/UI_pictures/strong.png"
}
images = {
    key: ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
    for key, path in image_paths.items()
}

setup_styles()

title = tk.Label(root, text="🔐 비밀번호 강도 예측기", font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#003366")
title.pack(pady=15)

guide = tk.Label(root, text="비밀번호를 입력하고 강도를 확인하세요 (6자 이상)", font=("Helvetica", 11), bg="#f0f8ff", fg="#333")
guide.pack()

entry = tk.Entry(root, font=("Helvetica", 14), width=30, show="*")
entry.pack(pady=10)
entry.bind('<Return>', predict_strength)

show_var = tk.BooleanVar()
show_check = tk.Checkbutton(root, text="비밀번호 보기", variable=show_var, command=toggle_password, bg="#f0f8ff")
show_check.pack()

btn_frame = tk.Frame(root, bg="#f0f8ff")
btn_frame.pack(pady=5)

predict_btn = tk.Button(btn_frame, text="예측하기", command=predict_strength, font=("Helvetica", 12), bg="#007acc",
                        fg="white", width=12)
predict_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(btn_frame, text="초기화", command=clear_input, font=("Helvetica", 12), bg="#cccccc", width=10)
clear_btn.grid(row=0, column=1, padx=5)

result_label = tk.Label(root, text="", font=("Helvetica", 14, "bold"), bg="#f0f8ff")
result_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=5)

# 이미지 라벨
image_label = tk.Label(root, bg="#f0f8ff")
image_label.pack(pady=10)

root.mainloop()
