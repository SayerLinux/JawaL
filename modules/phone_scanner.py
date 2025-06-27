#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة فحص أرقام الهواتف
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import re
import json
import logging
import requests
from bs4 import BeautifulSoup
from .utils import safe_request, get_user_agent

class PhoneScanner:
    """فئة لفحص أرقام الهواتف وجمع المعلومات المرتبطة بها"""
    
    def __init__(self, phone_number, timeout=30, verbose=False):
        """تهيئة فاحص الهاتف"""
        self.phone_number = phone_number
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('jawal')
        self.country_code = self._extract_country_code()
        self.national_number = self._extract_national_number()
        
        # قائمة بمواقع التواصل الاجتماعي للبحث
        self.social_sites = [
            {'name': 'Facebook', 'url': 'https://www.facebook.com/'},
            {'name': 'Instagram', 'url': 'https://www.instagram.com/'},
            {'name': 'Twitter', 'url': 'https://twitter.com/'},
            {'name': 'LinkedIn', 'url': 'https://www.linkedin.com/'},
            {'name': 'Telegram', 'url': 'https://t.me/'},
            {'name': 'WhatsApp', 'url': 'https://wa.me/'},
            {'name': 'Snapchat', 'url': 'https://www.snapchat.com/add/'},
            {'name': 'TikTok', 'url': 'https://www.tiktok.com/@'},
        ]
    
    def _extract_country_code(self):
        """استخراج رمز البلد من رقم الهاتف"""
        match = re.match(r'^\+(\d+)', self.phone_number)
        if match:
            return match.group(1)
        return None
    
    def _extract_national_number(self):
        """استخراج الرقم الوطني من رقم الهاتف"""
        match = re.match(r'^\+\d+(\d+)$', self.phone_number)
        if match:
            return match.group(1)
        return None
    
    def get_provider_info(self):
        """الحصول على معلومات مزود الخدمة"""
        self.logger.info(f"جاري البحث عن معلومات مزود الخدمة لرقم الهاتف: {self.phone_number}")
        
        # محاولة الحصول على معلومات مزود الخدمة من واجهة برمجة التطبيقات
        try:
            # استخدام واجهة برمجة تطبيقات numverify (مثال فقط، قد تحتاج إلى مفتاح API)
            # في الإنتاج، يجب استخدام خدمة حقيقية مثل Twilio أو Numverify
            api_url = f"https://api.apilayer.com/number_verification/validate?number={self.phone_number.replace('+', '')}"
            
            # هذا مجرد مثال، في التطبيق الحقيقي ستحتاج إلى مفتاح API
            # headers = {'apikey': 'YOUR_API_KEY'}
            # response = requests.get(api_url, headers=headers)
            
            # بدلاً من ذلك، سنقوم بمحاكاة الاستجابة للتوضيح
            provider_info = self._mock_provider_info()
            
            if self.verbose:
                self.logger.debug(f"معلومات مزود الخدمة: {json.dumps(provider_info, ensure_ascii=False)}")
            
            return provider_info
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات مزود الخدمة: {str(e)}")
            return self._mock_provider_info()  # استخدام بيانات وهمية في حالة الخطأ
    
    def _mock_provider_info(self):
        """إنشاء معلومات وهمية لمزود الخدمة (للعرض التوضيحي فقط)"""
        # تحديد مزود الخدمة بناءً على رمز البلد
        provider = "غير معروف"
        country = "غير معروف"
        valid = True
        
        # تحديد البلد ومزود الخدمة بناءً على رمز البلد
        if self.country_code == "966":  # السعودية
            country = "المملكة العربية السعودية"
            if self.national_number.startswith("50") or self.national_number.startswith("55"):
                provider = "STC"
            elif self.national_number.startswith("54") or self.national_number.startswith("56"):
                provider = "Mobily"
            elif self.national_number.startswith("53"):
                provider = "Zain"
        elif self.country_code == "971":  # الإمارات
            country = "الإمارات العربية المتحدة"
            if self.national_number.startswith("50") or self.national_number.startswith("54"):
                provider = "Etisalat"
            elif self.national_number.startswith("55") or self.national_number.startswith("56"):
                provider = "Du"
        elif self.country_code == "20":  # مصر
            country = "مصر"
            if self.national_number.startswith("10") or self.national_number.startswith("11"):
                provider = "Vodafone"
            elif self.national_number.startswith("12"):
                provider = "Orange"
            elif self.national_number.startswith("15"):
                provider = "Etisalat"
            elif self.national_number.startswith("14"):
                provider = "WE"
        
        return {
            "رقم الهاتف": self.phone_number,
            "صالح": valid,
            "البلد": country,
            "رمز البلد": self.country_code,
            "مزود الخدمة": provider,
            "نوع الرقم": "محمول",
        }
    
    def get_location_info(self):
        """الحصول على معلومات الموقع الجغرافي لرقم الهاتف"""
        self.logger.info(f"جاري البحث عن معلومات الموقع الجغرافي لرقم الهاتف: {self.phone_number}")
        
        try:
            # في التطبيق الحقيقي، يمكن استخدام خدمة مثل Google Maps Geocoding API
            # هنا نستخدم بيانات وهمية للعرض التوضيحي
            location_info = self._mock_location_info()
            
            if self.verbose:
                self.logger.debug(f"معلومات الموقع الجغرافي: {json.dumps(location_info, ensure_ascii=False)}")
            
            return location_info
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات الموقع الجغرافي: {str(e)}")
            return self._mock_location_info()  # استخدام بيانات وهمية في حالة الخطأ
    
    def _mock_location_info(self):
        """إنشاء معلومات وهمية للموقع الجغرافي (للعرض التوضيحي فقط)"""
        # تحديد الموقع الجغرافي بناءً على رمز البلد
        country = "غير معروف"
        city = "غير معروف"
        region = "غير معروف"
        timezone = "غير معروف"
        
        if self.country_code == "966":  # السعودية
            country = "المملكة العربية السعودية"
            region = "منطقة الرياض"
            city = "الرياض"
            timezone = "GMT+3"
        elif self.country_code == "971":  # الإمارات
            country = "الإمارات العربية المتحدة"
            region = "إمارة دبي"
            city = "دبي"
            timezone = "GMT+4"
        elif self.country_code == "20":  # مصر
            country = "مصر"
            region = "القاهرة"
            city = "القاهرة"
            timezone = "GMT+2"
        
        return {
            "البلد": country,
            "المنطقة": region,
            "المدينة": city,
            "المنطقة الزمنية": timezone,
        }
    
    def find_social_accounts(self):
        """البحث عن حسابات التواصل الاجتماعي المرتبطة برقم الهاتف"""
        self.logger.info(f"جاري البحث عن حسابات التواصل الاجتماعي المرتبطة برقم الهاتف: {self.phone_number}")
        
        social_accounts = []
        
        # في التطبيق الحقيقي، يمكن استخدام تقنيات مختلفة للبحث عن الحسابات
        # هنا نستخدم بيانات وهمية للعرض التوضيحي
        
        # محاكاة العثور على بعض الحسابات
        if self.phone_number.startswith("+966"):
            social_accounts.append({
                "platform": "WhatsApp",
                "username": self.phone_number,
                "url": f"https://wa.me/{self.phone_number.replace('+', '')}"
            })
            
            # إضافة حساب فيسبوك وهمي (للعرض التوضيحي فقط)
            social_accounts.append({
                "platform": "Facebook",
                "username": f"user_{self.national_number}",
                "url": f"https://www.facebook.com/profile.php?id=100{self.national_number}"
            })
        
        if self.verbose:
            self.logger.debug(f"تم العثور على {len(social_accounts)} حساب تواصل اجتماعي")
        
        return social_accounts
    
    def find_email_accounts(self):
        """البحث عن حسابات البريد الإلكتروني المرتبطة برقم الهاتف"""
        self.logger.info(f"جاري البحث عن حسابات البريد الإلكتروني المرتبطة برقم الهاتف: {self.phone_number}")
        
        email_accounts = []
        
        # في التطبيق الحقيقي، يمكن استخدام تقنيات مختلفة للبحث عن حسابات البريد الإلكتروني
        # هنا نستخدم بيانات وهمية للعرض التوضيحي
        
        # محاكاة العثور على بعض حسابات البريد الإلكتروني
        if self.national_number:
            # إنشاء بعض عناوين البريد الإلكتروني المحتملة
            email_accounts.append({
                "email": f"user{self.national_number}@gmail.com",
                "source": "تخمين"
            })
            
            email_accounts.append({
                "email": f"user{self.national_number}@yahoo.com",
                "source": "تخمين"
            })
            
            email_accounts.append({
                "email": f"user{self.national_number}@hotmail.com",
                "source": "تخمين"
            })
        
        if self.verbose:
            self.logger.debug(f"تم العثور على {len(email_accounts)} حساب بريد إلكتروني")
        
        return email_accounts
    
    def scan_leaks(self):
        """البحث عن تسريبات البيانات التي تحتوي على رقم الهاتف"""
        self.logger.info(f"جاري البحث عن تسريبات البيانات التي تحتوي على رقم الهاتف: {self.phone_number}")
        
        # في التطبيق الحقيقي، يمكن استخدام خدمات مثل Have I Been Pwned
        # هنا نستخدم بيانات وهمية للعرض التوضيحي
        
        leaks = []
        
        # محاكاة العثور على بعض التسريبات
        leaks.append({
            "source": "تسريب بيانات وهمي 1",
            "date": "2021-05-15",
            "data": ["رقم الهاتف", "الاسم", "البريد الإلكتروني"]
        })
        
        if self.verbose:
            self.logger.debug(f"تم العثور على {len(leaks)} تسريب بيانات")
        
        return leaks