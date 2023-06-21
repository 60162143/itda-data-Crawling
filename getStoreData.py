import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
import requests
import json

from ftp_upload import *

options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
chromedriver_path = 'chromedriver.exe'
driver = webdriver.Chrome(os.path.join(os.getcwd(), chromedriver_path), options=options)
host = '서버 호스트'         # 호스트
path = '서버 파일 위치'   # 서버 파일 위치 ( FTP 경로 )
category = {1:"치킨", 2:"중식", 3:"커피", 4:"햄버거", 5:"아이스크림", 6:"한식", 7:"피자", 8:"일식"}

storeId = 0     # 가게 고유 아이디 순번
hashId = 0      # 해시태그 고유 아이디 순번
menuId = 0      # 메뉴 고유 아이디 순번
workingId = 0   # 가게 운영시간 고유 아이디 순번

def main():
    global driver, menu_wb

    driver.implicitly_wait(4)  # 렌더링 될때까지 기다린다 4초
    driver.get('https://map.kakao.com/')  # 주소 가져오기

    for categoryId, categoryName in category.items() :
        search(categoryId, categoryName)

    driver.quit()
    print("finish")

# 카테고리 이름으로 검색
# placeId : 카테고리 고유 아이디 순번, placeName : 카테고리 이름
def search(placeId, placeName):
    global driver

    # 현재 위치 GPS 버튼 클릭
    driver.find_element_by_xpath('//*[@id="view.map"]/div[15]/a').send_keys(Keys.ENTER)

    # 줌 아웃 버튼 클릭
    driver.find_element_by_xpath('//*[@id="view.map"]/div[15]/div[1]/div/button[2]').send_keys(Keys.ENTER)
    
    # 검색 창에 검색어 입력
    search_area = driver.find_element_by_xpath('//*[@id="search.keyword.query"]')
    search_area.send_keys(placeName)
    
    # 검색 버튼 클릭
    driver.find_element_by_xpath('//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  
    sleep(1)
    
    # 우선 더보기 클릭해서 2페이지 이동
    try:
        driver.find_element_by_xpath('//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)
        sleep(1)
        print('More Button Click!!')
    except ElementNotInteractableException:
        print('More Button Not Here!!')
        
    # 검색된 정보가 있는 경우에만 탐색
    # 1번 페이지 place list 읽기
    html = driver.page_source
    # BeautifulSoup: 웹 페이지의 정보를 쉽게 스크랩할 수 있도록 기능을 제공하는 라이브러리
    soup = BeautifulSoup(html, 'html.parser')
    # 검색된 장소 목록
    place_lists = soup.select('.placelist > .PlaceItem') 

    # 검색된 첫 페이지 장소 목록 크롤링하기
    crawling(placeId, place_lists)
    search_area.clear()

def crawling(placeId, placeLists):
    # 장소 목록을 하나씩 크롤링
    print("length : " + str(len(placeLists)))
    for index in range(len(placeLists)):
        if index < 10 :
            storeData, thumbnailFileData, hashTagData, workingTimeData = getStore(placeId, index, driver)
            menuData = getMenuInfo(index, driver)
            
            callAPI(storeData, thumbnailFileData, workingTimeData, hashTagData, menuData)
        
# 가게 정보 조회
def getStore(categoryId, index, driver):
    # 상세페이지로 가서 가게 정보 찾기
    detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(index + 1) + ']/div[5]/div[4]/a[1]'
    driver.find_element_by_xpath(detail_page_xpath).send_keys(Keys.ENTER)
    driver.switch_to.window(driver.window_handles[-1])  # 상세정보 탭으로 변환
    sleep(1)
    
    global storeId      # 가게 고유 아이디 순번 ( 전역변수 )
    global hashId       # 해시태그 고유 아이디 순번 ( 전역변수 )
    global menuId       # 메뉴 고유 아이디 순번 ( 전역변수 )
    global workingId    # 가게 운영시간 고유 아이디 ( 전역변수 )
    
    storeId += 1    # 가게 고유 아이디 순번 증가
    # 가게 정보 초기화
    store = { "storeId" : storeId               # 가게 고유 아이디
             , "storeName" : ""                 # 가게 명
             , "storeThumbnailId" : 0           # 가게 썸네일 고유 아이디
             , "storeAddress" : ""              # 가게 주소
             , "storeLatitude" : 0              # 가게 위도
             , "storeLongitude" : 0             # 가게 경도
             , "storeNumber" : ""               # 가게 연락처
             , "storeDetail" : ""               # 가게 간단 제공 서비스
             , "storeInformation" : ""          # 가게 소개
             , "storeFacility" : ""             # 가게 제공 시설
             , "storeCategoryId" : categoryId   # 카테고리 고유 아이디
             }        
    
    thumbnailFile = {}     # 썸네일 파일 저장 정보
    hashTag = []            # 해시태그 정보
    workingTime = []        # 가게 운영시간 정보
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 가게 이름
    store['storeName'] = soup.select_one('#mArticle > div.cont_essential > div:nth-child(1) > div.place_details > div > h2').text

    # 가게 썸네일
    thumbnail = soup.select_one('#mArticle > div.cont_photo > div.photo_area > ul > li:nth-child(1) > a')
    if thumbnail :  # 썸네일이 등록되어 있을 경우
        thumbnail_url = thumbnail.get('style').split("\'")[1]   # url 추출
        
        thumbnailFile = url(thumbnail_url, store['storeId'])    # url 이미지 파일 로컬 저장
        store['storeThumbnailId'] = thumbnailFile['fileId']    # 썸네일 이미지 고유 아이디 순번 저장
    
    # 가게 상세 정보
    placeInfo_default = soup.select('#mArticle > div.cont_essential > div.details_placeinfo > div.placeinfo_default')
    
    # 장소 목록에 대한 개별 데이터 수집
    for j, placeInfo in enumerate(placeInfo_default) :
        placeInfoTitle = placeInfo.select_one('h4.tit_detail > span.ico_comm')  # 개별 위치에 대한 태그 타이틀
        placeFacility = placeInfo.select_one('h4.tit_facility') # 시설 타이틀은 다른 클래스에 등록되어 있어서 따로 뺌
        
        # 개별 데이터 태그가 있을 경우만 등록
        if placeInfoTitle : # 시설정보를 제외한 나머지 정보
            if placeInfoTitle.text == '위치' :  
                # 가게 주소
                address = ' '.join(placeInfo.select_one('div.location_detail > span.txt_address').text.split())
                
                # 가게 주소 정보에서 우편 정보 제거
                if '(우)' in address :
                    address = address.split('(우)')[0].strip()
                store['storeAddress'] = address
                
                # 위도, 경도 구하는 웹사이트 Open ( 주소 입력 시 위도, 경도 구할 수 있음 )
                driver.execute_script('window.open("http://www.moamodu.com/develop/daum_map.php", "_black");')
                # Open한 페이지 탭으로 전환
                driver.switch_to.window(driver.window_handles[2])
                
                # 현재 렌더링 된 페이지의 Elements
                html_address = driver.page_source
                soup_address = BeautifulSoup(html_address, 'html.parser')
                
                # 주소 입력 창
                driver.find_element_by_xpath('//*[@id="addr"]').send_keys(store.get('storeAddress'))
                #주소 입력 버튼
                driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div[1]/span/input').send_keys(Keys.ENTER)
                sleep(1)
                
                # 유효한 주소가 아닐 경우 Alert 창이 뜸
                # Alert 창 제어
                
                try :
                    # 유효한 주소가 아닐 경우 Alert 창 확인 버튼 클릭
                    driverAlert = driver.switch_to_alert()
                    driverAlert.accept()
                except :
                    # 유효한 주소일 경우 위도, 경도 저장
                    location = driver.find_element_by_xpath('//*[@id="coord"]') # 위도, 경도를 포함한 정보
                    sleep(1)
                    # 위도, 경도 추출
                    position = location.text.split("위도(Lat) : ")[1].replace("\n\n", " ").split(" 경도(Lng) : ")
                    # 위도, 경도 저장
                    store['storeLatitude'] = float(position[0])
                    store['storeLongitude'] = float(position[1])
                
                # 위도, 경도 구하는 페이지 Close
                driver.close()
                # 상세 정보 탭으로 전환
                driver.switch_to.window(driver.window_handles[1])  
            elif placeInfoTitle.text == '운영시간 안내' :
                # 가게 운영 시간 정보 ( 여러 개일 경우 )
                workingArr = placeInfo.select('div.location_detail > div.fold_floor > div.inner_floor > ul:nth-child(2) > li')
                
                # 가게 운영시간 정보 데이터
                if workingArr : # 운영 정보가 여러 개 있을 경우 
                    # 운영 정보가 여러개일 경우 String 형태로 저장 ( 구분자 '\n'로 설정되어 있음 )
                    for work in workingArr :
                        workingId += 1  # 가게 운영시간 고유 아이디 순번 증가
                        working = {}    # 가게 운영시간 정보
                        working['workingId'] = workingId    # 가게 운영시간 고유 아이디
                        working['storeId'] = storeId        # 가게 고유 아이디
                        working['workingTime'] = work.text.replace("\n", "")    # 가게 운영시간, 처음과 끝의 '\n' 구분자 제거
                        workingTime.append(working)         # 가게 운영시간 정보 저장
                else :
                    # 운영 정보가 1개일 경우
                    work = placeInfo.select_one('div.location_detail > div.location_present > ul > li')
                    workingId += 1  # 가게 운영시간 고유 아이디 순번 증가
                    working = {}    # 가게 운영시간 정보
                    working['workingId'] = workingId    # 가게 운영시간 고유 아이디
                    working['storeId'] = storeId        # 가게 고유 아이디
                    working['workingTime'] = work.text.replace("\n", "")    # 가게 운영시간, 처음과 끝의 '\n' 구분자 제거
                    workingTime.append(working)         # 가게 운영시간 정보 저장
            elif placeInfoTitle.text == '연락처' :
                # 가게 연락처
                store['storeNumber'] = placeInfo.select_one('div.location_detail > div.location_present > span.num_contact > span.txt_contact').text
            elif placeInfoTitle.text == '예약, 배달, 포장' :
                # 가게 간단 제공 서비스
                store['storeDetail'] = placeInfo.select_one('div.location_detail').text
            elif placeInfoTitle.text == '소개' :
                # 가게 간단 소개
                store['storeInformation'] = placeInfo.select_one('div.location_detail > p.txt_introduce').text
            elif placeInfoTitle.text == '태그' :
                # 가게 해시태그, 공백을 구분자로 String 형태로 저장
                hashArr = placeInfo.select_one('div.location_detail > div.txt_tag > span.tag_g').text.replace("\n", " ").strip().split(" ")
                
                for hash in hashArr :
                    hashId += 1     # 해시태그 고유 아이디 순번 증가
                    hashTagData = {}    # 해시태그 정보
                    hashTagData['hashTagId'] = hashId   # 해시태그 고유 아이디
                    hashTagData['storeId'] = storeId    # 가게 고유 아이디
                    hashTagData['hashTagName'] = hash   # 해시태그
                    hashTag.append(hashTagData) # 해시태그 정보 저장
                    
        # 가게 제공 시설 정보 있을 경우
        elif placeFacility and placeFacility.text == '시설정보':
            # 가게 제공 시설 정보 있을 경우
            facility_li = placeInfo.select('ul > li')
            # 가게 시설 정보 데이터
            facility_text = ''
            # 가게 제공 시설 정보가 여러개일 경우 String 형태로 저장
            for faclity_main in facility_li :
                facility_text += ' ' + faclity_main.text.replace("\n", "")
            # 가게 제공 시설 정보 저장
            store['storeFacility'] =facility_text.strip()

    driver.close()
    driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환

    return store, thumbnailFile, hashTag, workingTime

def getMenuInfo(i, driver):
    # 상세페이지로 가서 메뉴찾기
    detail_page_xpath = '//*[@id="info.search.place.list"]/li[' + str(i + 1) + ']/div[5]/div[4]/a[1]'
    driver.find_element_by_xpath(detail_page_xpath).send_keys(Keys.ENTER)
    driver.switch_to.window(driver.window_handles[-1])  # 상세정보 탭으로 변환
    sleep(1)

    menuInfos = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 메뉴의 3가지 타입
    menuonlyType = soup.select('.cont_menu > .list_menu > .menuonly_type')
    nophotoType = soup.select('.cont_menu > .list_menu > .nophoto_type')
    photoType = soup.select('.cont_menu > .list_menu > .photo_type')

    if len(menuonlyType) != 0:
        for i, menu in enumerate(menuonlyType) :
            #if i < 5 :
            menuInfos.append(_getMenuInfo(i + 1, menu))
    elif len(nophotoType) != 0:
        for i, menu in enumerate(nophotoType) :
            #if i < 5 :
            menuInfos.append(_getMenuInfo(i + 1, menu))
    else:
        for i, menu in enumerate(photoType) :
            #if i < 5 :
            menuInfos.append(_getMenuInfo(i + 1, menu))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 전환

    return menuInfos

def _getMenuInfo(order, menu):
    menuName = menu.select('.info_menu > .loss_word')[0].text   # 메뉴 이름
    menuPrices = menu.select('.info_menu > .price_menu')        # 메뉴 가격
    
    global storeId  # 가게 고유 아이디 순번 ( 전역변수 )
    global menuId   # 메뉴 고유 아이디 순번 ( 전역변수 )
    menuId += 1     # 메뉴 고유 아이디 순번 증가
    
    # 메뉴 정보 초기화
    menu = { "menuId" : menuId          # 메뉴 고유 아이디
            , "storeId" : storeId       # 가게 고유 아이디
            , "menuName" : menuName     # 메뉴 이름
            , "menuPrice" : 0           # 메뉴 가격
            , "menuOrder" : order       # 메뉴 정렬 순서
            }
    
    # 메뉴 가격이 있으면 저장
    if len(menuPrices) != 0:
        menu['menuPrice'] = int(menuPrices[0].text.split(' ')[1].replace(",", ""))

    return menu

# Insert 하기 위한 API 호출 메소드
def callAPI(storeData, thumbnailFileData, workingTimeData, hashTagData, menuData) :
    jsonData = { 'store' : storeData
                ,'file' : thumbnailFileData 
                ,'workingTime' : workingTimeData
                ,'hashTag' : hashTagData
                ,'menu' : menuData }    
    url = host + path
    headers = {'Content-Type' : 'application/json; charset=utf-8'}
    print("\n---------------------------- 가게 정보 입니다 -----------------------------------\n")
    print(jsonData)
            
    response = requests.post(url, json=jsonData, headers=headers)
    
    if response.status_code == 200 :
        print("\nsuccess")
        print(response.text)
    else :
        print("\nfalse")
        print(response.text)

if __name__ == "__main__":
    main()