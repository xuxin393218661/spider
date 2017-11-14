# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 10:41:48 2017

@author: xu_xin1
"""

# -*- coding: utf-8 -*-  
from bs4 import BeautifulSoup  
import re  
from time import sleep  
import random  
import urllib  
import requests  

class Login(object):
    def login_douban(self):
        url = "https://douban.com/accounts/login"  
        formData = {  
            "redir": "https://www.douban.com",  
            "form_email": "393218661@qq.com",  
            "form_password": "19810628xxx",  
            "login": u'登录',  
            'source': 'None',  
            }  
  
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",  
                   "Referer": "https://douban.com/accounts/login",  
                   "Host": "accounts.douban.com",  
                   "Connection": "Keep-Alive",  
                   "Content-Type": "application/x-www-form-urlencoded"  
                   }  
        s = requests.session()


        r_ = s.post(url, data=formData, headers=headers)  
        a = r_.text  
        soup_ = BeautifulSoup(a, "html.parser")  
        captchaAddr = soup_.find('img', id='captcha_image')['src']  
        reCaptchaID = r'<input type="hidden" name="captcha-id" value="(.*?)"/'  
        captchaID = re.findall(reCaptchaID, a)  
        urllib.urlretrieve(captchaAddr, "captcha.jpg")  
  
        captcha = raw_input('please input the captcha:')  
        formData['captcha-solution'] = captcha  
        formData['captcha-id'] = captchaID  
                
        r_ = s.post(url, data=formData, headers=headers)  
        page_ = r_.text  
        print page_
        co = r_.cookies
        
if __name__ == '__main__':
        login = Login()
        for i in range(100):
            login.login_douban()