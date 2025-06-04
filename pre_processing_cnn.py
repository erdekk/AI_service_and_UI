import random
import string
from zxcvbn import zxcvbn
import Levenshtein
import csv

def luds_score(pwd):
    length = len(pwd)
    has_upper = any(c.isupper() for c in pwd)
    has_lower = any(c.islower() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    has_symbol = any(c in string.punctuation for c in pwd)

    score = 0
    score += min(length * 4, 40)   # 길이 최대 40점
    score += 10 if has_upper else 0
    score += 10 if has_lower else 0
    score += 20 if has_digit else 0
    score += 20 if has_symbol else 0

    return min(score, 100)

def levenshtein_penalty(pwd, common_passwords, threshold=3):
    distances = [Levenshtein.distance(pwd, p) for p in common_passwords]
    min_dist = min(distances) if distances else 100
    penalty = max(0, (threshold - min_dist) * 20)  # 거리 0 → -60점, 거리 3 이상 → 0점
    return -penalty

def zxcvbn_score(pwd):
    result = zxcvbn(pwd)
    return result['score'] * 20  # 0~4 점수를 0~80 점으로 변환

def total_strength_score(pwd, common_passwords):
    s1 = luds_score(pwd)
    s2 = zxcvbn_score(pwd)
    s3 = levenshtein_penalty(pwd, common_passwords)
    final_score = s1 * 0.3 + s2 * 0.5 + (100 + s3) * 0.2
    return round(min(max(final_score, 0), 100), 2)

def generate_labels(password_list, common_passwords):
    labeled_data = []
    for pwd in password_list:
        score = total_strength_score(pwd, common_passwords)
        labeled_data.append((pwd, score))
    return labeled_data

input_file = 'data_set.txt'

# 결과 저장할 CSV 경로
output_file = 'dataset_preprocessed.csv'

# 최대 비밀번호 길이 설정
MAX_LEN = 20

def load_passwords(filename, max_len=MAX_LEN):
    passwords = set()
    with open(filename, 'r', encoding='latin-1', errors='ignore') as f:
        for line in f:
            pwd = line.strip()
            if 0 < len(pwd) <= max_len and all(c in string.printable for c in pwd):
                passwords.add(pwd)
    return list(passwords)

# 전처리 및 라벨링
def preprocess_passwords(passwords, common_passwords):
    processed = []
    for pwd in passwords:
        score = total_strength_score(pwd, common_passwords)
        processed.append((pwd, score))
    return processed
def load_top_passwords(filename, limit=100000, max_len=20):
    passwords = []
    with open(filename, 'r', encoding='latin-1', errors='ignore') as f:
        for line in f:
            pwd = line.strip()
            if 0 < len(pwd) <= max_len and all(c in string.printable for c in pwd):
                passwords.append(pwd)
                if len(passwords) >= limit:
                    break
    return passwords
def main():
    # 1. 비밀번호 로드
    print("Loading passwords...")
    passwords = load_passwords(input_file)
    random.shuffle(passwords)
    print(f"Loaded {len(passwords)} unique passwords.")

    print("Generating strength scores...")
    dataset = preprocess_passwords(passwords, passwords)

    # 4. CSV 저장
    print(f"Saving to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['password', 'score'])
        for pwd, score in dataset:
            writer.writerow([pwd, score])

    print("Done!")

if __name__ == '__main__':
    main()