# TasteHouse (맛집 상대평가 비교 서비스)

**2025-2 연세대학교 SW-AI 비즈니스응용설계 프로젝트**

현재 배달 앱이나 지도 앱에서 사용하고 있는 음식점 평가 제도는 만점 부여를 전제로 운영되어 음식점 간 비교가 실제로 이루어질 수 없는 환경이며, 바이럴 마케팅이 많아 별점 조작이 쉽게 이루어지므로 신뢰도가 매우 낮습니다. 음식점에서 제공하는 리뷰 이벤트로 인해 음식의 퀄리티에 비해 식당이 높은 평가를 받는 경우가 많고, 음식점의 주관에 따라 리뷰를 삭제하거나 표시하지 않을 수도 있기 때문에 외부적 요소가 크게 개입될 수 있으므로 오로지 음식의 맛을 중점으로 한 비교가 어려운 상황입니다.

TasteHouse는 기존 절대평가 위주의 별점 시스템이 가진 한계를 극복하고, **상대평가식 별점**을 도입하여 '진짜 맛집'을 찾을 수 있도록 도와주는 웹 서비스 프로토타입입니다.

---

## 주요 기능 (Features)

1.  **상대평가 별점 시스템**: 리뷰 수와 리뷰어의 신뢰도를 반영한 베이지안 추정 기반의 독자적인 별점 알고리즘 적용
2.  **인터랙티브 지도**: Kakao Maps API를 활용하여 지도 드래그/줌에 따라 해당 영역의 식당만 필터링하여 표시
3.  **실시간 필터링 & 정렬**: 현재 화면에 있는 식당들을 별점순으로 자동 정렬 및 카테고리별 필터링
4.   **자동화된 데이터 파이프라인**: Python Selenium을 활용한 데이터 크롤링 및 GitHub Actions를 통한 자동 업데이트 구조

---

## 실행 환경 및 필수 요건 (Prerequisites)

이 프로젝트를 실행하기 위해서는 다음 환경이 필요합니다.

* **Python**
* **Web Browser** (크롤링 데이터 수집)
* **Kakao Map API Key** (JavaScript Key & REST API Key)
* **Visual Studio Code**와 **VS Code 'Live Server' Extension** 사용을 권장합니다.

---

## 설치 및 실행 가이드 (Installation & Usage)

평가를 위해 코드를 실행하는 순서는 다음과 같습니다.

### 1. 저장소 복제

git clone을 통해 저장소를 복제하세요.

### 2. Python 라이브러리 설치

requirements.txt에는 selenium, beautifulsoup4, webdriver-manager, pandas, requests, Pillow가 포함되어 있어야 합니다.

### 3. Kakao API 키 설정

실행 전 다음 파일들에 본인의 카카오 API 키를 입력해주세요.

1. index.html

 - <head> 태그 내의 스크립트 주소에 JavaScript Key 입력
 - src="https://dapi.kakao.com/v2/maps/sdk.js?appkey=YOUR_JS_API_KEY"

2. csv_to_json.py 등의 Backend 파일

 - 코드 상단 REST_API_KEY 변수에 REST API Key 입력

### 4. 데이터 생성 및 업데이트

데이터 업데이트는 매일 9시 daily_update.yml 파일에 의해 자동으로 이루어집니다.

데이터를 추가하지 않는 경우 기본 제공되는 restaurants.json을 사용하는 것을 권장합니다.

**4-1. 초기 데이터 생성 (csv_to_json.py)**

list.csv에 있는 식당 목록을 읽어 카카오 API로 좌표를 찾고 JSON 파일을 생성합니다.

**4-2. 별점 데이터 크롤링 및 업데이트 (update_ratings.py)**

생성된 JSON 파일을 기반으로 카카오맵 리뷰를 크롤링하여 독자적인 별점을 계산하고 이미지를 다운로드합니다.

실행 시 img/ 폴더에 식당 이미지들이 다운로드되고, restaurants.json의 score가 업데이트됩니다.

### 5. 웹사이트 실행

index.html 파일을 직접 더블 클릭해서 열면 브라우저 보안 정책(CORS)으로 인해 JSON 데이터를 불러오지 못합니다. 반드시 로컬 웹 서버를 통해 실행해야 합니다.

## 프로젝트 구조 (Project Structure)

project/    
├── index.html             # 메인 프론트엔드 코드 (지도, 리스트, 필터 로직 포함)    
├── css/                   # 스타일시트 (tooplate-style.css 등)    
├── js/                    # 외부 라이브러리 (Bootstrap, Slick 등)    
├── img/                   # 식당 이미지 및 마커 아이콘 저장소    
├── restaurants.json       # [Data] 식당 정보 및 별점 데이터베이스    
├── list.csv               # [Source] 크롤링 대상 식당 목록 원본    
├── csv_to_json.py         # [Script] CSV -> JSON 변환 및 좌표 추출    
├── update_ratings.py      # [Script] 리뷰 크롤링, 별점 알고리즘 계산, 이미지 처리    
├── requirements.txt       # Python 의존성 목록    
└── README.md              # 프로젝트 설명서