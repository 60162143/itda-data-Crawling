# itda-data-Crawling

## **📝 개요**

> **프로젝트:** 세상을 연결해주는 도구 **잇다(Itda**)
>
> **기획 및 제작:** 오태근
>
> **분류:** 가게 데이터 크롤링
>
> **제작 기간:** 23.03
>
> **사용 라이브러리:**
  - Selenium Library : 웹 브라우저를 이용하는 자동화 동적 라이브러리
    ```python
    import os
    from selenium import webdriver

    options = webdriver.ChromeOptions() # 크롬 브라우저 옵션
    options.add_argument('headless')    # 브라우저 안 띄우기
    options.add_argument('lang=ko_KR')  # KR 언어
    chromedriver_path = "chromedriver"  # 크롬 드라이버 위치
    driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)  # chromedriver 열기

    ############
    ### 로직 ###
    ############

    driver.quit() # driver 종료, 브라우저 닫기

> **흐름도:**
  1. 카카오 맵 화면에서 카테고리 별로 검색 후 상세 화면 Open
  2. 가게 상세 화면에서 데이터 크롤링
  3. 위도 경도 구하는 사이트 Open후 주소값으로 위도, 경도 값 추출
  4. 가게 썸네일 이미지 있을 경우 localStorage에 파일 저장
  5. 저장된 파일을 FTP 서버에 업로드
  6. 크롤링된 최종 데이터 DB에 Insert

> **크롤링 데이터:**
  ```json
    { 
      "store" : { "storeId" : "가게 고유 아이디", 
                  "storeName" : "가게 명", 
                  "storeThumbnailId" : "가게 썸네일 고유 아이디",
                  "storeAddress" : "가게 주소",
                  "storeLatitude" : "가게 위도",
                  "storeLongitude" : "가게 경도",
                  "storeNumber" : "가게 연락처",
                  "storeDetail" : "가게 간단 제공 서비스",
                  "storeInformation" : "가게 소개",
                  "storeFacility" : "가게 제공 시설",
                  "storeCategoryId" : "카테고리 고유 아이디"
        },
        "file" : { "fileId" : "파일 고유 아이디",
                   "filePath" : "파일 저장 경로 ( FTP )",
                   "fileSize" : "파일 크기",
                   "fileEts" : "파일 확장자",
                   "fileName" : "파일 이름"
        },
        "workingTime" : { "workingId" : "가게 운영시간 고유 아이디",
                          "storeId" : "가게 고유 아이디",
                          "workingTime" : "가게 운영시간"
        },
        "hashTag" : { "hasTagId" : "해시태그 고유 아이디",
                      "storeId" : "가게 고유 아이디",
                      "hashTagName" : "해시태그"
        },
        "menu" : { "menuId" : "메뉴 고유 아이디"
                   "storeId" : "가게 고유 아이디"
                   "menuName" : "메뉴 이름"
                   "menuPrice" : "메뉴 가격"
                    "menuOrder" : "메뉴 정렬 순서"
        } 
  }
  ```
> **문의:** no2955922@naver.com
