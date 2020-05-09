from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.request
from tika import parser
import tabula
from PyPDF2 import PdfFileReader, PdfFileWriter
import requests, PyPDF2
import datetime
import os
import cv2
from pdf2image import convert_from_path
import subprocess


  
def crawling(today):
  #  try:
    # 헤드리스로 바꿔야됨.
        # 크롤링.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver =  webdriver.Chrome("./chromedriver", chrome_options = chrome_options)
   # driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', DesiredCapabilities.CHROME)
    driver.implicitly_wait(3)

        # 1. 게시판 들어가서 첫번째 게시물 url 가져오기
    board_url = 'http://www.pvv.co.kr/bbs/index.php?code=bbs_menu01'
    driver.get(board_url)
    post = driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/table[1]/tbody/tr[2]/td[3]/a[1]")
    post_url = post.click()

        # 2. 게시물 들어가서 다운로드 url 가져오기
    download_url = driver.find_element_by_xpath('//*[@id="DivAndPrint"]/table/tbody/tr/td/table[6]/tbody/tr[4]/td[2]/a')
    url = download_url.get_attribute('href')

    response = requests.get(url)
    my_raw_data = response.content

    with open("./"+today+"/"+today+".pdf", 'wb') as my_data:
        my_data.write(my_raw_data)

    return True
    #except:
    #    return False
#    else:
 #       return False
        #로그 남기기

        
def make_img(today):
   # try:
    pages = convert_from_path("./" + today + "/" + today + '.pdf', 100)
    for page in pages:
        page.save(today + '.jpg', 'JPEG')

    return True
   # except:
    #    return False
   # else:
     #   return False


def devide_img(today):
    try:
        src = cv2.imread(todayDir + ".jpg", cv2.IMREAD_ANYCOLOR)
        dst = src.copy()
        #월화수목금
        week_day_s = [95, 305, 510, 736, 945]
        week_day_e = [300,510, 736, 945, 1155]
        #조식 A코너 B코너 샐러드바 석식
        menus_s = [150, 305, 365, 460, 570]
        menus_e = [275, 365, 430, 543, 695]

        days = ['mon', 'tue', 'wed', 'tur', 'fri']
        #names = ['morning', 'lunch_a', 'lunch_b', 'salad', 'dinner']
        #dst = src[100:600, 200:700]

        # 구분 이미지 생성
        src = cv2.imread(todayDir + ".jpg", cv2.IMREAD_ANYCOLOR)
        dst = src[130:695,0:105]
        cv2.imwrite("./" + todayDir + '/images/guboon.jpg', dst)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        guboon = "./" + todayDir + '/images/guboon.jpg'
        guboonsrc = cv2.imread(guboon, cv2.IMREAD_ANYCOLOR)

        for i in range(5):
            dst = src[130:695, week_day_s[i]:week_day_e[i]]
            cv2.imwrite("./" + today + '/images/' + days[i] + '.jpg', dst)
            dayimg = cv2.imread("./" + today + '/images/' + days[i] + '.jpg', cv2.IMREAD_ANYCOLOR)
            himg = cv2.hconcat([guboonsrc, dayimg])
            cv2.imwrite("./" + today + '/images/' + days[i] + '.jpg', himg)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return True
    except:
        return False
    else:
        return False


# 작동되는 날 폴더 없으면 만들기
dt = datetime.datetime.now()
#dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond
month = '{:02d}'.format(dt.month)
todayDir = str(dt.year)+month+str(dt.day)

if not os.path.isdir(todayDir):
    os.mkdir(todayDir)
if not os.path.isdir(todayDir + '/images'):
    os.mkdir(todayDir+ '/images')


if(crawling(todayDir)):
    if(make_img(todayDir)):
        devide_img(todayDir)
        subprocess.call(['aws', 's3', 'cp', "./" + todayDir +  "/images", 's3://sunukim-image-bucket', '--recursive'])
        