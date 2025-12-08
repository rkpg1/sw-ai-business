import pandas as pd
import json
import requests
import time

# --- [설정] 카카오 REST API 키 (필수!) ---
REST_API_KEY = "74d9fc86639f5430131215628b3492f9"
# -------------------------------------

def get_coordinates(kakao_id, query):
    """
    카카오 로컬 API를 사용하여 ID에 해당하는 장소의 좌표(lat, lng)를 찾습니다.
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {REST_API_KEY}"}
    params = {"query": query, "size": 15}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        for place in data['documents']:
            # 검색 결과 중 ID가 일치하는 장소 찾기
            if place['id'] == str(kakao_id):
                return float(place['y']), float(place['x']) # lat, lng
        
        # ID로 못 찾으면 이름으로 검색된 첫 번째 장소라도 반환 (차선책)
        if data['documents']:
             # print(f"  -> ID 불일치, 이름 검색 결과 사용: {query}")
             return float(data['documents'][0]['y']), float(data['documents'][0]['x'])

        print(f" -> 좌표 찾기 실패: '{query}' (ID: {kakao_id})")
        return 0.0, 0.0
        
    except Exception as e:
        print(f" -> 에러 발생: {e}")
        return 0.0, 0.0

def main():
    # 1. CSV 파일 읽기 (파일명: list.csv)
    try:
        # 엑셀에서 저장한 CSV는 한글이 깨질 수 있으므로 encoding='utf-8-sig' 또는 'cp949' 시도
        try:
            df = pd.read_csv('list.csv', encoding='utf-8-sig')
        except:
            df = pd.read_csv('list.csv', encoding='cp949')
            
    except FileNotFoundError:
        print("'list.csv' 파일을 찾을 수 없습니다. 파일명을 확인해주세요.")
        return

    restaurants = []
    
    print(f"총 {len(df)}개의 식당 데이터를 처리합니다...\n")

    for index, row in df.iterrows():
        name_kr = str(row['name']).strip()
        name_en = str(row['engname']).strip()
        kakao_id = str(row['id']).strip()
        genre = str(row['genre']).strip()
        
        # 이름 포맷: "한글이름 (English Name)"
        full_name = f"{name_kr} ({name_en})" if name_en and name_en != 'nan' else name_kr

        print(f"[{index+1}/{len(df)}] {full_name} 좌표 찾는 중...")

        # 2. 좌표 찾기
        lat, lng = get_coordinates(kakao_id, name_kr)
        
        # 0.5초 대기 (API 호출 제한 방지)
        time.sleep(0.1)

        # 3. JSON 구조 생성
        restaurant_data = {
            "id": f"restaurant-{index + 1}",
            "kakao_id": kakao_id,
            "name": full_name,
            "category": genre, # CSV의 장르를 그대로 사용
            "score": 0,   # 초기값
            "reviews": 0, # 초기값
            "imageSrc": "img/tn-img-01.jpg", # 기본 이미지
            "lat": lat,
            "lng": lng
        }
        
        restaurants.append(restaurant_data)

    # 4. JSON 파일 저장
    with open('restaurants.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=4, ensure_ascii=False)

    print(f"\n✅ 'restaurants.json' 파일 생성이 완료되었습니다! (총 {len(restaurants)}개)")

if __name__ == "__main__":
    main()