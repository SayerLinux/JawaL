#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة فحص مواقع ووردبريس
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import re
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .utils import safe_request, get_user_agent, extract_domain

class WordpressScanner:
    """فئة لفحص مواقع ووردبريس وكشف الثغرات الأمنية"""
    
    def __init__(self, url, timeout=30, verbose=False):
        """تهيئة فاحص ووردبريس"""
        self.url = url
        self.domain = extract_domain(url)
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('jawal')
        
        # قائمة بالمسارات الشائعة في ووردبريس
        self.common_paths = [
            '/wp-login.php',
            '/wp-admin/',
            '/wp-content/',
            '/wp-includes/',
            '/wp-json/',
            '/xmlrpc.php',
            '/wp-config.php',
            '/wp-cron.php',
            '/readme.html',
            '/license.txt',
        ]
        
        # قائمة بالثغرات الشائعة في ووردبريس
        self.common_vulnerabilities = [
            {
                'name': 'كشف إصدار ووردبريس',
                'path': '/readme.html',
                'pattern': r'Version ([\d.]+)',
                'severity': 'منخفضة',
                'description': 'يمكن معرفة إصدار ووردبريس من خلال ملف readme.html.'
            },
            {
                'name': 'كشف المستخدمين',
                'path': '/wp-json/wp/v2/users',
                'pattern': None,  # سيتم التحقق من الاستجابة في دالة منفصلة
                'severity': 'متوسطة',
                'description': 'يمكن كشف أسماء المستخدمين من خلال واجهة برمجة التطبيقات REST.'
            },
            {
                'name': 'تمكين xmlrpc.php',
                'path': '/xmlrpc.php',
                'pattern': None,  # سيتم التحقق من الاستجابة في دالة منفصلة
                'severity': 'متوسطة',
                'description': 'ملف xmlrpc.php مفعل، مما قد يسمح بهجمات القوة الغاشمة.'
            },
            {
                'name': 'كشف قائمة المقالات',
                'path': '/wp-json/wp/v2/posts',
                'pattern': None,  # سيتم التحقق من الاستجابة في دالة منفصلة
                'severity': 'منخفضة',
                'description': 'يمكن الوصول إلى قائمة المقالات من خلال واجهة برمجة التطبيقات REST.'
            },
            {
                'name': 'كشف قائمة القوالب',
                'path': '/wp-content/themes/',
                'pattern': 'Index of',
                'severity': 'متوسطة',
                'description': 'يمكن الوصول إلى قائمة القوالب من خلال مجلد themes.'
            },
            {
                'name': 'كشف قائمة الإضافات',
                'path': '/wp-content/plugins/',
                'pattern': 'Index of',
                'severity': 'متوسطة',
                'description': 'يمكن الوصول إلى قائمة الإضافات من خلال مجلد plugins.'
            },
        ]
    
    def verify_wordpress(self):
        """التحقق من أن الموقع يستخدم ووردبريس"""
        self.logger.info(f"جاري التحقق من استخدام ووردبريس في الموقع: {self.url}")
        
        # عدد المسارات التي تم العثور عليها
        found_paths = 0
        
        try:
            # التحقق من المسارات الشائعة في ووردبريس
            for path in self.common_paths:
                full_url = urljoin(self.url, path)
                response = safe_request(full_url, timeout=self.timeout)
                
                if response and response.status_code != 404:
                    found_paths += 1
                    
                    if self.verbose:
                        self.logger.debug(f"تم العثور على المسار: {path}")
                    
                    # إذا تم العثور على 3 مسارات على الأقل، فمن المحتمل أن يكون ووردبريس
                    if found_paths >= 3:
                        self.logger.info(f"تم التأكد من استخدام ووردبريس في الموقع: {self.url}")
                        return True
            
            # التحقق من وجود علامات ووردبريس في صفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            if response:
                # البحث عن علامات ووردبريس في محتوى الصفحة
                wp_indicators = [
                    'wp-content',
                    'wp-includes',
                    'WordPress',
                    'wp-json',
                ]
                
                for indicator in wp_indicators:
                    if indicator in response.text:
                        self.logger.info(f"تم التأكد من استخدام ووردبريس في الموقع: {self.url}")
                        return True
            
            self.logger.info(f"لم يتم التأكد من استخدام ووردبريس في الموقع: {self.url}")
            return False
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من استخدام ووردبريس: {str(e)}")
            return False
    
    def get_wordpress_info(self):
        """الحصول على معلومات ووردبريس"""
        self.logger.info(f"جاري جمع معلومات ووردبريس للموقع: {self.url}")
        
        wordpress_info = {}
        
        try:
            # التحقق من إصدار ووردبريس
            version = self._get_wordpress_version()
            if version:
                wordpress_info['الإصدار'] = version
            
            # الحصول على القالب المستخدم
            theme = self._get_wordpress_theme()
            if theme:
                wordpress_info['القالب'] = theme
            
            # الحصول على قائمة الإضافات
            plugins = self._get_wordpress_plugins()
            if plugins:
                wordpress_info['الإضافات'] = plugins
            
            if self.verbose:
                self.logger.debug(f"تم جمع معلومات ووردبريس: {json.dumps(wordpress_info, ensure_ascii=False)}")
            
            return wordpress_info
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات ووردبريس: {str(e)}")
            return {'خطأ': str(e)}
    
    def _get_wordpress_version(self):
        """الحصول على إصدار ووردبريس"""
        version = None
        
        # طرق مختلفة للحصول على إصدار ووردبريس
        methods = [
            # من ملف readme.html
            {'path': '/readme.html', 'pattern': r'Version ([\d.]+)'},
            # من رأس الصفحة
            {'path': '/', 'pattern': r'<meta name="generator" content="WordPress ([\d.]+)">'},
            # من ملف feed
            {'path': '/feed/', 'pattern': r'<generator>https://wordpress.org/\?v=([\d.]+)</generator>'},
        ]
        
        for method in methods:
            try:
                full_url = urljoin(self.url, method['path'])
                response = safe_request(full_url, timeout=self.timeout)
                
                if response and response.status_code == 200:
                    match = re.search(method['pattern'], response.text)
                    if match:
                        version = match.group(1)
                        break
            except Exception as e:
                self.logger.error(f"خطأ في الحصول على إصدار ووردبريس من {method['path']}: {str(e)}")
        
        return version
    
    def _get_wordpress_theme(self):
        """الحصول على القالب المستخدم في ووردبريس"""
        theme_info = {}
        
        try:
            # الحصول على محتوى الصفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            
            if response and response.status_code == 200:
                # البحث عن مسار القالب في محتوى الصفحة
                theme_pattern = r'wp-content/themes/([^/]+)'
                theme_matches = re.findall(theme_pattern, response.text)
                
                if theme_matches:
                    theme_name = theme_matches[0]
                    theme_info['الاسم'] = theme_name
                    
                    # محاولة الحصول على إصدار القالب
                    theme_version_pattern = r'wp-content/themes/' + theme_name + r'[^>]+ver=([\d.]+)'
                    theme_version_match = re.search(theme_version_pattern, response.text)
                    
                    if theme_version_match:
                        theme_info['الإصدار'] = theme_version_match.group(1)
                    
                    # التحقق من وجود ملف style.css للقالب
                    theme_style_url = urljoin(self.url, f'/wp-content/themes/{theme_name}/style.css')
                    theme_style_response = safe_request(theme_style_url, timeout=self.timeout)
                    
                    if theme_style_response and theme_style_response.status_code == 200:
                        # البحث عن معلومات القالب في ملف style.css
                        theme_author_pattern = r'Author: (.+)'
                        theme_author_match = re.search(theme_author_pattern, theme_style_response.text)
                        
                        if theme_author_match:
                            theme_info['المطور'] = theme_author_match.group(1)
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات القالب: {str(e)}")
        
        return theme_info
    
    def _get_wordpress_plugins(self):
        """الحصول على قائمة الإضافات المستخدمة في ووردبريس"""
        plugins = []
        
        try:
            # الحصول على محتوى الصفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            
            if response and response.status_code == 200:
                # البحث عن مسارات الإضافات في محتوى الصفحة
                plugin_pattern = r'wp-content/plugins/([^/]+)'
                plugin_matches = re.findall(plugin_pattern, response.text)
                
                # إزالة التكرارات
                unique_plugins = set(plugin_matches)
                
                for plugin_name in unique_plugins:
                    plugin_info = {'الاسم': plugin_name}
                    
                    # محاولة الحصول على إصدار الإضافة
                    plugin_version_pattern = r'wp-content/plugins/' + plugin_name + r'[^>]+ver=([\d.]+)'
                    plugin_version_match = re.search(plugin_version_pattern, response.text)
                    
                    if plugin_version_match:
                        plugin_info['الإصدار'] = plugin_version_match.group(1)
                    
                    plugins.append(plugin_info)
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على قائمة الإضافات: {str(e)}")
        
        return plugins
    
    def scan_vulnerabilities(self):
        """فحص الثغرات الأمنية في ووردبريس"""
        self.logger.info(f"جاري فحص الثغرات الأمنية في ووردبريس للموقع: {self.url}")
        
        vulnerabilities = []
        
        try:
            # التحقق من الثغرات الشائعة في ووردبريس
            with ThreadPoolExecutor(max_workers=5) as executor:
                # إنشاء قائمة بالمهام
                futures = [executor.submit(self._check_vulnerability, vuln) for vuln in self.common_vulnerabilities]
                
                # جمع النتائج
                for future in futures:
                    result = future.result()
                    if result:
                        vulnerabilities.append(result)
            
            # التحقق من إصدار ووردبريس
            version = self._get_wordpress_version()
            if version:
                # التحقق من الإصدار القديم
                if self._is_outdated_version(version):
                    vulnerabilities.append({
                        'name': 'إصدار ووردبريس قديم',
                        'severity': 'عالية',
                        'description': f'يستخدم الموقع إصدار قديم من ووردبريس ({version})، مما قد يعرضه للثغرات الأمنية.',
                        'evidence': f'الإصدار: {version}'
                    })
            
            # التحقق من الإضافات القديمة
            plugins = self._get_wordpress_plugins()
            for plugin in plugins:
                if 'الإصدار' in plugin and self._is_outdated_plugin(plugin['الاسم'], plugin['الإصدار']):
                    vulnerabilities.append({
                        'name': f'إضافة قديمة: {plugin["الاسم"]}',
                        'severity': 'متوسطة',
                        'description': f'يستخدم الموقع إصدار قديم من الإضافة {plugin["الاسم"]} ({plugin["الإصدار"]}), مما قد يعرضه للثغرات الأمنية.',
                        'evidence': f'الإضافة: {plugin["الاسم"]}, الإصدار: {plugin["الإصدار"]}'
                    })
            
            if self.verbose:
                self.logger.debug(f"تم اكتشاف {len(vulnerabilities)} ثغرة أمنية في ووردبريس")
            
            return vulnerabilities
        
        except Exception as e:
            self.logger.error(f"خطأ في فحص الثغرات الأمنية في ووردبريس: {str(e)}")
            return []
    
    def _check_vulnerability(self, vuln):
        """التحقق من ثغرة أمنية محددة"""
        try:
            full_url = urljoin(self.url, vuln['path'])
            response = safe_request(full_url, timeout=self.timeout)
            
            if response:
                # إذا كان هناك نمط محدد للبحث
                if vuln['pattern']:
                    if vuln['pattern'] in response.text:
                        return {
                            'name': vuln['name'],
                            'severity': vuln['severity'],
                            'description': vuln['description'],
                            'evidence': f'تم العثور على النمط "{vuln["pattern"]}" في {vuln["path"]}'
                        }
                # حالات خاصة
                elif vuln['path'] == '/wp-json/wp/v2/users' and response.status_code == 200:
                    try:
                        users_data = response.json()
                        if isinstance(users_data, list) and len(users_data) > 0:
                            user_names = [user.get('name', '') for user in users_data if 'name' in user]
                            return {
                                'name': vuln['name'],
                                'severity': vuln['severity'],
                                'description': vuln['description'],
                                'evidence': f'تم العثور على {len(user_names)} مستخدم: {", ".join(user_names)}'
                            }
                    except json.JSONDecodeError:
                        pass
                elif vuln['path'] == '/xmlrpc.php' and response.status_code != 404:
                    return {
                        'name': vuln['name'],
                        'severity': vuln['severity'],
                        'description': vuln['description'],
                        'evidence': f'ملف xmlrpc.php متاح (رمز الحالة: {response.status_code})'
                    }
                elif vuln['path'] == '/wp-json/wp/v2/posts' and response.status_code == 200:
                    try:
                        posts_data = response.json()
                        if isinstance(posts_data, list) and len(posts_data) > 0:
                            return {
                                'name': vuln['name'],
                                'severity': vuln['severity'],
                                'description': vuln['description'],
                                'evidence': f'تم العثور على {len(posts_data)} مقالة'
                            }
                    except json.JSONDecodeError:
                        pass
            
            return None
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الثغرة {vuln['name']}: {str(e)}")
            return None
    
    def _is_outdated_version(self, version):
        """التحقق مما إذا كان إصدار ووردبريس قديمًا"""
        # هذه مجرد قيمة افتراضية، يجب تحديثها بانتظام
        latest_version = '6.4.2'  # آخر إصدار من ووردبريس وقت كتابة الكود
        
        # تحويل الإصدارات إلى قوائم من الأرقام
        version_parts = list(map(int, version.split('.')))
        latest_parts = list(map(int, latest_version.split('.')))
        
        # مقارنة الإصدارات
        for i in range(min(len(version_parts), len(latest_parts))):
            if version_parts[i] < latest_parts[i]:
                return True
            elif version_parts[i] > latest_parts[i]:
                return False
        
        # إذا كانت جميع الأجزاء متساوية حتى الآن، فإن الإصدار الأقصر هو الأقدم
        return len(version_parts) < len(latest_parts)
    
    def _is_outdated_plugin(self, plugin_name, plugin_version):
        """التحقق مما إذا كانت إضافة ووردبريس قديمة"""
        # هذه مجرد قيمة افتراضية، يجب تحديثها بانتظام أو استخدام API للتحقق
        # في تطبيق حقيقي، يمكن استخدام API ووردبريس للتحقق من أحدث إصدار
        
        # افتراضيًا، نعتبر أن الإصدارات التي تبدأ بـ 1. أو 2. قديمة
        if plugin_version.startswith('1.') or plugin_version.startswith('2.'):
            return True
        
        return False