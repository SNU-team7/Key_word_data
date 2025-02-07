import pandas as pd
import re
from konlpy.tag import Okt
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import json

# JSON 파일 경로
json_file_path = 'keyword.json'

# JSON 파일에서 불용어와 기술 키워드 불러오기
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

stop_words = set(data['stop_words'])
tech_keywords = data['tech_keywords']

# Okt 형태소 분석기
okt = Okt()

# 직무 관련 키워드 추출 함수 (2-gram 포함)
def extract_keywords_with_bigrams(text):
    # 한글 단어 추출
    korean_words = okt.nouns(text)
    korean_words = [word for word in korean_words if word not in stop_words]

    # 영어 단어 추출
    english_words = re.findall(r'[a-zA-Z]+', text)
    english_words = [word for word in english_words if word not in stop_words]

    # 모든 단어 결합
    all_words = korean_words + english_words

    # 단일 단어 및 2-gram 저장 리스트
    extracted_words = []

    for i, word in enumerate(all_words):
        if len(word) > 1:  # 단일 단어 저장 (길이가 1 초과)
            extracted_words.append(word)

        # 2-gram (이전 단어 + 현재 단어)
        if i > 0:
            bigram_prev = all_words[i-1] + ' ' + word
            if bigram_prev not in stop_words:
                extracted_words.append(bigram_prev)

        # 2-gram (현재 단어 + 다음 단어)
        if i < len(all_words) - 1:
            bigram_next = word + ' ' + all_words[i+1]
            if bigram_next not in stop_words:
                extracted_words.append(bigram_next)

    return extracted_words

# CSV 파일 읽기 (두 파일)
file_path_AI = 'job_details_AI.csv'
file_path_back = 'job_details_back.csv'
file_path_front = 'job_details_front.csv'

df_AI = pd.read_csv(file_path_AI)
df_back = pd.read_csv(file_path_back)
df_front = pd.read_csv(file_path_front)

# CSV 파일에서 직무 관련 열 추출
columns_to_process = ['직무 상세', '주요 업무', '자격요건', '우대 사항']

# 모든 키워드 저장 (각 직종별로)
extracted_keywords_AI = {col: df_AI[col].apply(extract_keywords_with_bigrams).explode().dropna().tolist() for col in columns_to_process}
extracted_keywords_back = {col: df_back[col].apply(extract_keywords_with_bigrams).explode().dropna().tolist() for col in columns_to_process}
extracted_keywords_front = {col: df_front[col].apply(extract_keywords_with_bigrams).explode().dropna().tolist() for col in columns_to_process}

# 상위 키워드 추출 함수
def get_top_keywords(keywords, top_n=20):
    count = Counter(keywords)
    return count.most_common(top_n)

# 각 직종별 상위 키워드 추출
top_keywords_AI = {col: get_top_keywords(extracted_keywords_AI[col]) for col in columns_to_process}
top_keywords_back = {col: get_top_keywords(extracted_keywords_back[col]) for col in columns_to_process}
top_keywords_front = {col: get_top_keywords(extracted_keywords_front[col]) for col in columns_to_process}

# 결과 출력
for col in columns_to_process:
    print(f"\n{col} (AI 직종) 키워드 (상위 10개):")
    print(top_keywords_AI[col])

    print(f"\n{col} (Back-End 직종) 키워드 (상위 10개):")
    print(top_keywords_back[col])

    print(f"\n{col} (AI 직종) 키워드 (상위 10개):")
    print(top_keywords_front[col])

# 주요 업무와 자격요건에서 기술 키워드 등장 횟수 카운트
def extract_tech_keywords(text):
    words = text.split()
    return [word for word in words if word in tech_keywords]

# 기술 키워드 등장 횟수 계산 (각 직종별로)
tech_counts_AI = Counter()
tech_counts_back = Counter()
tech_counts_front = Counter()

for col in ['주요 업무', '자격요건', '우대 사항']:
    df_AI[col].dropna().apply(lambda x: tech_counts_AI.update(extract_tech_keywords(x)))
    df_back[col].dropna().apply(lambda x: tech_counts_back.update(extract_tech_keywords(x)))
    df_front[col].dropna().apply(lambda x: tech_counts_front.update(extract_tech_keywords(x)))

# 상위 5개 기술 키워드 출력
top_tech_keywords_AI = tech_counts_AI.most_common(10)
top_tech_keywords_back = tech_counts_back.most_common(10)
top_tech_keywords_front = tech_counts_front.most_common(10)

print("\nAI 직종 주요 업무 및 자격요건에서 가장 많이 등장한 기술 키워드 TOP 5:")
for keyword, count in top_tech_keywords_AI:
    print(f"{keyword}: {count}회")

print("\nBack-End 직종 주요 업무 및 자격요건에서 가장 많이 등장한 기술 키워드 TOP 5:")
for keyword, count in top_tech_keywords_back:
    print(f"{keyword}: {count}회")

print("\nFront-End 직종 주요 업무 및 자격요건에서 가장 많이 등장한 기술 키워드 TOP 5:")
for keyword, count in top_tech_keywords_front:
    print(f"{keyword}: {count}회")

# 워드클라우드 생성 함수
def generate_wordcloud(keywords, title):
    font_path = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'  # MacOS 폰트 경로

    if not os.path.exists(font_path):
        print(f"폰트 경로 {font_path}를 찾을 수 없습니다.")
        return

    wordcloud = WordCloud(font_path=font_path,
                          width=800, height=400,
                          background_color='white').generate_from_frequencies(dict(keywords))
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.show()

# 워드클라우드 생성
for col in columns_to_process:
    print(f"\n{col} (AI 직종) 키워드 워드클라우드:")
    generate_wordcloud(top_keywords_AI[col], f"AI 직종 - {col}")

    print(f"\n{col} (Back-End 직종) 키워드 워드클라우드:")
    generate_wordcloud(top_keywords_back[col], f"Back-End 직종 - {col}")

    print(f"\n{col} (Front_end 직종) 키워드 워드클라우드:")
    generate_wordcloud(top_keywords_front[col], f"Front_end 직종 - {col}")
