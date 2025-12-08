import json
import sys
import time
import math # log10 사용
from datetime import datetime # 날짜 계산용
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- 1. 최종 별점 계산을 위한 상수 ---
MU_0 = 3.0           # (μ₀) 관찰된 리뷰어의 글로벌 평균 (설정값)
S_BASELINE = 3.0      # (S_baseline) 목표하는 식당의 글로벌 기준점 (설정값)
K_PARAM = 10          # (k) 신뢰도 계수 (후기 10개 미만 필터와 동일하게 설정)
MAX_DAYS = 1095       # (3년) 이보다 오래된 리뷰는 제외
# -------------------------------------------

# --- 2. Colab을 위한 Selenium 옵션 ---

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver
# -------------------------------------------

def calculate_rating(driver, kakao_id):
    # 3. 페이지 접속 및 스크롤
    url = "https://place.map.kakao.com/{kakao_id}#review"
    driver.get(url)

    print("페이지 접속")
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    print("스크롤 시작")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("데이터 파싱 시작")
            break
        last_height = new_height

    # 4. 페이지 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 5. 데이터 추출 및 최종 평점 계산
    review_ul = soup.find('ul', class_='list_review')

    if review_ul:
        reviews = review_ul.find_all('li')

        print(f"총 {len(reviews)}개의 리뷰 태그를 찾았습니다.")

        # 최종 가중 평균 계산을 위한 변수
        weighted_scores_sum = 0.0 # (S_rel * W_time * W_cred)의 합계
        total_weights_sum = 0.0   # (W_time * W_cred)의 합계

        parsed_review_count = 0 # [수정] 파싱에 성공한 리뷰만 카운트
        valid_review_count = 0  # [수정] 필터까지 통과한 리뷰만 카운트

        today = datetime.now()    # 오늘 날짜 (리뷰 날짜 계산용)

        for review in reviews: # 'i' 제거

            try:
                # --- [STEP 1] 필수 데이터 4개 모두 파싱 시도 ---

                # 1. S_review (리뷰 평점)
                starred_grade_tag = review.find('span', class_='starred_grade')
                rating_spans = starred_grade_tag.find_all('span', class_='screen_out')
                rating = float(rating_spans[1].get_text(strip=True))

                # 2. D_age (리뷰 날짜)
                date_tag = review.find('span', class_='txt_date')
                date_str = date_tag.get_text(strip=True)
                date_obj = datetime.strptime(date_str, '%Y.%m.%d.')
                d_age = (today - date_obj).days

                # 3 & 4. N_reviews (후기 수) & S_avg (별점 평균)
                list_detail_tag = review.find('ul', class_='list_detail')

                review_count_str = None
                reviewer_avg_str = None

                # 'list_detail' 태그가 없으면 이 시점에서 None.find_all() -> AttributeError 발생
                for stat_item in list_detail_tag.find_all('li'):
                    text = stat_item.get_text(strip=True)
                    if text.startswith('후기'):
                        review_count_str = text.replace('후기', '').strip()
                    elif text.startswith('별점평균'):
                        reviewer_avg_str = text.replace('별점평균', '').strip()

                # '후기' 또는 '별점평균' 태그가 없으면 (None), int(None) 또는 float(None) 시도 -> TypeError 발생
                review_count = int(review_count_str)
                reviewer_avg_rating = float(reviewer_avg_str)

            except Exception as e:
                # --- [STEP 2] 파싱 오류 발생 시 ---
                # (AttributeError, TypeError, ValueError, IndexError 등)
                # 아무것도 출력하지 않고 조용히 건너뜀 (넘버링 X)
                continue

            # --- [STEP 3] 파싱 성공 시 (try 블록 통과) ---

            # 파싱 성공한 리뷰만 넘버링 및 기본 정보 출력
            parsed_review_count += 1
            print("---")
            print(f"[파싱 성공 리뷰 #{parsed_review_count}]")
            print(f"  원본점수: {rating} | 리뷰어평균: {reviewer_avg_rating} | 후기수: {review_count} | 날짜: {d_age}일 전")

            # --- [STEP 4] 필터링 로직 (및 제외 사유 출력) ---

            # 1. 날짜 필터 (3년 이내)
            if d_age > MAX_DAYS:
                print(f"  [처리 상태: 제외 (3년 초과 - {d_age}일 전)]")
                continue

            # 2. 리뷰어 신뢰도 필터 (후기 10개 미만)
            if review_count < K_PARAM:
                print(f"  [처리 상태: 제외 (리뷰어 후기 {K_PARAM}개 미만 - {review_count}개)]")
                continue

            # --- [STEP 5] 계산 로직 (필터 통과 시) ---
            valid_review_count += 1
            print(f"  [처리 상태: 포함 (유효 리뷰 #{valid_review_count})] ★") # 계산에 포함됨을 표시

            # 1. W_time (최신순 가중치)
            w_time = 1.0 - (d_age / MAX_DAYS)

            # 2. W_cred (리뷰어 신뢰도 가중치)
            if review_count >= 100:
                w_cred = 1.0
            else:
                w_cred = math.log10(review_count) - 1.0

            # 3. S_rel (상대적 평점)
            s_adjusted_avg = ((review_count * reviewer_avg_rating) + (K_PARAM * MU_0)) / (review_count + K_PARAM)
            s_rel_temp = S_BASELINE + (rating - s_adjusted_avg)
            s_rel = max(1.0, min(5.0, s_rel_temp))

            # 4. 합산
            final_weight = w_time * w_cred
            weighted_scores_sum += (s_rel * final_weight)
            total_weights_sum += final_weight

            # [출력] 유효 리뷰의 계산 상세 내역
            print(f"  S_adjusted_avg (보정된 리뷰어 평균): {s_adjusted_avg:.3f}")
            print(f"  S_rel (상대 평점): {s_rel:.3f}")
            print(f"  W_time (날짜 가중치): {w_time:.3f} | W_cred (신뢰도 가중치): {w_cred:.3f}")


        # --- 최종 평점 계산 ---
        print("---" * 10)

        # [출력] 총 유효 리뷰 개수 (수정됨)
        print(f"총 {parsed_review_count}개의 파싱 성공 리뷰 중,")
        print(f"총 {valid_review_count}개의 유효한 리뷰를 기반으로 계산합니다.")

        if total_weights_sum > 0:
            final_score = weighted_scores_sum / total_weights_sum
            print(f"\n이 식당의 새로운 평점: {final_score:.2f} / 5.0")
        else:
            print("\n계산에 사용할 수 있는 유효한 리뷰가 없습니다.")
            print(" (필터 기준: 3년 이내 작성, 리뷰어 후기 10개 이상)")

        return final_score, valid_review_count

    else:
        print("리뷰 목록('ul.list_review')을 찾을 수 없습니다.")
        return 0.0, 0
    
def main():
    json_path = 'restaurants.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("restaurants.json 파일을 찾을 수 없습니다.")
        return

    driver = get_driver()

    try:
        for restaurant in data:
            if 'kakao_id' in restaurant and restaurant['kakao_id']:
                print(f"\n[{restaurant['name']}] 업데이트 시작...")
                score, reviews = calculate_rating(driver, restaurant['kakao_id'])
                
                # 결과 업데이트
                restaurant['score'] = score
                restaurant['reviews'] = reviews
            else:
                print(f"\n[{restaurant.get('name')}] kakao_id가 없어 건너뜁니다.")

        # 파일 저장
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("\n모든 업데이트가 완료되었습니다.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()