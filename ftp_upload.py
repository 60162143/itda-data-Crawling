import ftplib
import urllib.request
import time
import os

fileId = 0

def ftp(file) :
    # FTP 서버 접속
    session = ftplib.FTP()
    session.connect('서버 주소', '포트번호')  # 서버 주소, Port 번호 ( 통상 21 )
    session.login("계정 아이디", "계정 비밀번호")    # 계정 아이디, 비밀번호
    
    uploadfile = open(os.getcwd() + "\\localFileStorage\\" + file['fileName'] + "." + file['fileEts'] ,mode='rb') #업로드할 파일 open
 
    session.encoding='utf-8'
    session.storbinary('STOR ' + 'public_html/ftpFileStorage/' + file['fileName'] + "." + file['fileEts'], uploadfile) #파일 업로드
    
    uploadfile.close() # 파일 닫기
    
    session.quit() # 서버 나가기
    print(os.getcwd() + "\\localFileStorage\\" + file['fileName'] + "." + file['fileEts'])
    print('\nFile Transfer Success!!\n')

# 이미지 URL -> 로컬 스토리지에 저장후 파일 정보 Return
def url(url_path, store_id):
    url = url_path  # 이미지 URL
    
    # 카카오맵 이미지 URL 크롤링시 https: 가 안붙어 있어서 있는지 체크
    if "https:" not in url :
        url = "https:" + url
    
    file_name = "tn_" + str(store_id) + ".jpg"   # 파일명 통일
    
    # 이미지의 주소와 다운받을 경로를 적어주면 해당 위치에 이미지 다운로드
    urllib.request.urlretrieve(url, os.getcwd() + "/localFileStorage/" + file_name)
    
    global fileId   # 파일 고유 아이디 순번 ( 전역변수 )
    fileId += 1     # 파일 고유 아이디 순번 증가
    
    # 파일 정보
    file = { "fileId" : fileId  # 파일 고유 아이디
            , "filePath" : "/ftpFileStorage/"    # 파일 저장 경로 ( FTP )
            , "fileSize" : os.path.getsize(os.getcwd() + "/localFileStorage/" + file_name) / 1024  # 파일 크기
            , "fileEts" : "jpg" # 파일 확장자
            , "fileName" : file_name.replace('.jpg', '')    # 파일 이름
            }
    
    ftp(file)   # FTP 서버에 파일 업로드
    
    return file
    