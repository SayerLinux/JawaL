#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة فحص أسماء المستخدمين
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import re
import json
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from .utils import safe_request, get_user_agent

class UsernameScanner:
    """فئة لفحص أسماء المستخدمين وجمع المعلومات المرتبطة بها"""
    
    def __init__(self, username, timeout=30, verbose=False):
        """تهيئة فاحص اسم المستخدم"""
        self.username = username
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('jawal')
        
        # قائمة بمواقع التواصل الاجتماعي للبحث
        self.social_sites = [
            {
                'name': 'Facebook',
                'url': f'https://www.facebook.com/{username}',
                'check_string': ['<title>Facebook</title>', 'لم يتم العثور على الصفحة']
            },
            {
                'name': 'Twitter',
                'url': f'https://twitter.com/{username}',
                'check_string': ['<title>X</title>', 'هذا الحساب لا يوجد']
            },
            {
                'name': 'Instagram',
                'url': f'https://www.instagram.com/{username}/',
                'check_string': ['<title>Instagram</title>', 'الصفحة غير متوفرة']
            },
            {
                'name': 'LinkedIn',
                'url': f'https://www.linkedin.com/in/{username}/',
                'check_string': ['<title>LinkedIn</title>', 'هذا الملف الشخصي غير متوفر']
            },
            {
                'name': 'GitHub',
                'url': f'https://github.com/{username}',
                'check_string': ['<title>GitHub</title>', '404']
            },
            {
                'name': 'YouTube',
                'url': f'https://www.youtube.com/@{username}',
                'check_string': ['<title>YouTube</title>', 'لم يتم العثور على القناة']
            },
            {
                'name': 'TikTok',
                'url': f'https://www.tiktok.com/@{username}',
                'check_string': ['<title>TikTok</title>', 'لم يتم العثور على الصفحة']
            },
            {
                'name': 'Reddit',
                'url': f'https://www.reddit.com/user/{username}',
                'check_string': ['<title>reddit.com</title>', 'لا يوجد أحد يستخدم هذا الاسم']
            },
            {
                'name': 'Pinterest',
                'url': f'https://www.pinterest.com/{username}/',
                'check_string': ['<title>Pinterest</title>', 'لم يتم العثور على الصفحة']
            },
            {
                'name': 'Snapchat',
                'url': f'https://www.snapchat.com/add/{username}',
                'check_string': ['<title>Snapchat</title>', 'لم يتم العثور على المستخدم']
            },
            {
                'name': 'Telegram',
                'url': f'https://t.me/{username}',
                'check_string': ['<title>Telegram</title>', 'لم يتم العثور على الصفحة']
            },
            {
                'name': 'Medium',
                'url': f'https://medium.com/@{username}',
                'check_string': ['<title>Medium</title>', '404']
            },
            {
                'name': 'Quora',
                'url': f'https://www.quora.com/profile/{username}',
                'check_string': ['<title>Quora</title>', 'لم يتم العثور على الملف الشخصي']
            },
            {
                'name': 'Twitch',
                'url': f'https://www.twitch.tv/{username}',
                'check_string': ['<title>Twitch</title>', 'لم يتم العثور على القناة']
            },
            {
                'name': 'SoundCloud',
                'url': f'https://soundcloud.com/{username}',
                'check_string': ['<title>SoundCloud</title>', 'لم يتم العثور على الصفحة']
            },
        ]
    
    def find_social_accounts(self):
        """البحث عن حسابات التواصل الاجتماعي المرتبطة باسم المستخدم"""
        self.logger.info(f"جاري البحث عن حسابات التواصل الاجتماعي لاسم المستخدم: {self.username}")
        
        social_accounts = []
        
        # استخدام ThreadPoolExecutor للبحث بشكل متوازي
        with ThreadPoolExecutor(max_workers=5) as executor:
            # إنشاء قائمة بالمهام
            futures = [executor.submit(self._check_social_site, site) for site in self.social_sites]
            
            # جمع النتائج
            for future in futures:
                result = future.result()
                if result:
                    social_accounts.append(result)
        
        if self.verbose:
            self.logger.debug(f"تم العثور على {len(social_accounts)} حساب تواصل اجتماعي")
        
        return social_accounts
    
    def _check_social_site(self, site):
        """التحقق من وجود اسم المستخدم على موقع تواصل اجتماعي محدد"""
        try:
            if self.verbose:
                self.logger.debug(f"جاري التحقق من {site['name']}: {site['url']}")
            
            # إجراء طلب HTTP للتحقق من وجود الصفحة
            response = safe_request(site['url'], timeout=self.timeout)
            
            # التحقق من وجود الحساب
            exists = False
            if response and response.status_code == 200:
                # التحقق من وجود سلسلة نصية تشير إلى عدم وجود الحساب
                page_content = response.text.lower()
                if not any(check_str.lower() in page_content for check_str in site['check_string']):
                    exists = True
            
            # إنشاء معلومات الحساب
            account_info = {
                'platform': site['name'],
                'username': self.username,
                'url': site['url'],
                'exists': exists
            }
            
            # إضافة معلومات إضافية إذا كان الحساب موجودًا
            if exists and response:
                # محاولة استخراج العنوان
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string if soup.title else ''
                    account_info['title'] = title
                except:
                    pass
            
            return account_info
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من {site['name']}: {str(e)}")
            return None
    
    def find_email_accounts(self):
        """البحث عن حسابات البريد الإلكتروني المرتبطة باسم المستخدم"""
        self.logger.info(f"جاري البحث عن حسابات البريد الإلكتروني المرتبطة باسم المستخدم: {self.username}")
        
        email_accounts = []
        
        # في التطبيق الحقيقي، يمكن استخدام تقنيات مختلفة للبحث عن حسابات البريد الإلكتروني
        # هنا نستخدم بيانات وهمية للعرض التوضيحي
        
        # إنشاء بعض عناوين البريد الإلكتروني المحتملة
        email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com', 'icloud.com']
        
        for domain in email_domains:
            email_accounts.append({
                'email': f"{self.username}@{domain}",
                'source': 'تخمين'
            })
        
        if self.verbose:
            self.logger.debug(f"تم إنشاء {len(email_accounts)} حساب بريد إلكتروني محتمل")
        
        return email_accounts
    
    def deep_search(self):
        """إجراء بحث عميق عن اسم المستخدم"""
        self.logger.info(f"جاري إجراء بحث عميق عن اسم المستخدم: {self.username}")
        
        results = {}
        
        # في التطبيق الحقيقي، يمكن استخدام تقنيات مختلفة للبحث العميق
        # مثل البحث في محركات البحث، وقواعد بيانات تسريبات البيانات، وغيرها
        # هنا نستخدم بيانات وهمية للعرض التوضيحي
        
        # محاكاة البحث في محركات البحث
        search_results = self._mock_search_engine_results()
        if search_results:
            results['نتائج محركات البحث'] = search_results
        
        # محاكاة البحث في قواعد بيانات تسريبات البيانات
        leak_results = self._mock_leak_database_results()
        if leak_results:
            results['تسريبات البيانات'] = leak_results
        
        # محاكاة البحث في المنتديات
        forum_results = self._mock_forum_results()
        if forum_results:
            results['المنتديات'] = forum_results
        
        if self.verbose:
            self.logger.debug(f"تم العثور على {len(results)} نوع من النتائج في البحث العميق")
        
        return results
    
    def _mock_search_engine_results(self):
        """محاكاة نتائج محركات البحث (للعرض التوضيحي فقط)"""
        return [
            {
                'title': f'الملف الشخصي لـ {self.username} على LinkedIn',
                'url': f'https://www.linkedin.com/in/{self.username}/',
                'snippet': f'اعرض الملف الشخصي الكامل لـ {self.username} على LinkedIn، أكبر شبكة للمحترفين في العالم.'
            },
            {
                'title': f'{self.username} على Twitter',
                'url': f'https://twitter.com/{self.username}',
                'snippet': f'أحدث التغريدات من {self.username} (@{self.username}).'
            },
            {
                'title': f'{self.username} - GitHub',
                'url': f'https://github.com/{self.username}',
                'snippet': f'مستودعات {self.username} على GitHub.'
            }
        ]
    
    def _mock_leak_database_results(self):
        """محاكاة نتائج قواعد بيانات تسريبات البيانات (للعرض التوضيحي فقط)"""
        return [
            {
                'source': 'تسريب بيانات وهمي 1',
                'date': '2021-05-15',
                'data': ['اسم المستخدم', 'البريد الإلكتروني', 'كلمة المرور المشفرة']
            },
            {
                'source': 'تسريب بيانات وهمي 2',
                'date': '2020-11-23',
                'data': ['اسم المستخدم', 'رقم الهاتف']
            }
        ]
    
    def _mock_forum_results(self):
        """محاكاة نتائج المنتديات (للعرض التوضيحي فقط)"""
        return [
            {
                'forum': 'منتدى وهمي 1',
                'url': f'https://forum1.example.com/user/{self.username}',
                'last_active': '2022-03-10',
                'posts': 15
            },
            {
                'forum': 'منتدى وهمي 2',
                'url': f'https://forum2.example.com/profile/{self.username}',
                'last_active': '2021-12-05',
                'posts': 7
            }
        ]