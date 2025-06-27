#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة فحص مواقع جوملا
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

class JoomlaScanner:
    """فئة لفحص مواقع جوملا وكشف الثغرات الأمنية"""
    
    def __init__(self, url, timeout=30, verbose=False):
        """تهيئة فاحص جوملا"""
        self.url = url
        self.domain = extract_domain(url)
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('jawal')
        
        # قائمة بالمسارات الشائعة في جوملا
        self.common_paths = [
            '/administrator/',
            '/administrator/index.php',
            '/administrator/manifests/files/joomla.xml',
            '/language/en-GB/en-GB.xml',
            '/robots.txt',
            '/htaccess.txt',
            '/README.txt',
            '/configuration.php',
            '/components/',
            '/modules/',
            '/templates/',
            '/plugins/',
            '/images/',
            '/includes/',
            '/cache/',
            '/libraries/',
            '/installation/',
        ]
        
        # قائمة بالثغرات الشائعة في جوملا
        self.common_vulnerabilities = [
            {
                'name': 'كشف إصدار جوملا',
                'path': '/administrator/manifests/files/joomla.xml',
                'pattern': r'<version>([\d.]+)</version>',
                'severity': 'منخفضة',
                'description': 'يمكن معرفة إصدار جوملا من خلال ملف joomla.xml.'
            },
            {
                'name': 'كشف إصدار جوملا (طريقة بديلة)',
                'path': '/language/en-GB/en-GB.xml',
                'pattern': r'<version>([\d.]+)</version>',
                'severity': 'منخفضة',
                'description': 'يمكن معرفة إصدار جوملا من خلال ملف اللغة.'
            },
            {
                'name': 'وجود مجلد التثبيت',
                'path': '/installation/',
                'pattern': None,  # سيتم التحقق من الاستجابة في دالة منفصلة
                'severity': 'عالية',
                'description': 'مجلد التثبيت لا يزال موجودًا، مما قد يسمح بإعادة تثبيت الموقع.'
            },
            {
                'name': 'كشف قائمة المكونات',
                'path': '/components/',
                'pattern': 'Index of',
                'severity': 'متوسطة',
                'description': 'يمكن الوصول إلى قائمة المكونات من خلال مجلد components.'
            },
            {
                'name': 'كشف قائمة الموديولات',
                'path': '/modules/',
                'pattern': 'Index of',
                'severity': 'متوسطة',
                'description': 'يمكن الوصول إلى قائمة الموديولات من خلال مجلد modules.'
            },
            {
                'name': 'كشف قائمة القوالب',
                'path': '/templates/',
                'pattern': 'Index of',
                'severity': 'متوسطة',
                'description': 'يمكن الوصول إلى قائمة القوالب من خلال مجلد templates.'
            },
            {
                'name': 'كشف ملف التكوين',
                'path': '/configuration.php-dist',
                'pattern': None,  # سيتم التحقق من الاستجابة في دالة منفصلة
                'severity': 'عالية',
                'description': 'ملف التكوين النموذجي متاح، مما قد يكشف عن معلومات حساسة.'
            },
            {
                'name': 'كشف ملف README',
                'path': '/README.txt',
                'pattern': 'Joomla',
                'severity': 'منخفضة',
                'description': 'ملف README متاح، مما قد يكشف عن معلومات حول الإصدار.'
            },
        ]
    
    def verify_joomla(self):
        """التحقق من أن الموقع يستخدم جوملا"""
        self.logger.info(f"جاري التحقق من استخدام جوملا في الموقع: {self.url}")
        
        # عدد المسارات التي تم العثور عليها
        found_paths = 0
        
        try:
            # التحقق من المسارات الشائعة في جوملا
            for path in self.common_paths:
                full_url = urljoin(self.url, path)
                response = safe_request(full_url, timeout=self.timeout)
                
                if response and response.status_code != 404:
                    found_paths += 1
                    
                    if self.verbose:
                        self.logger.debug(f"تم العثور على المسار: {path}")
                    
                    # إذا تم العثور على 3 مسارات على الأقل، فمن المحتمل أن يكون جوملا
                    if found_paths >= 3:
                        self.logger.info(f"تم التأكد من استخدام جوملا في الموقع: {self.url}")
                        return True
            
            # التحقق من وجود علامات جوملا في صفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            if response:
                # البحث عن علامات جوملا في محتوى الصفحة
                joomla_indicators = [
                    'joomla',
                    'Joomla',
                    'com_content',
                    'com_users',
                    'mod_',
                    '/templates/',
                    '/components/',
                ]
                
                for indicator in joomla_indicators:
                    if indicator in response.text:
                        self.logger.info(f"تم التأكد من استخدام جوملا في الموقع: {self.url}")
                        return True
                
                # البحث عن علامات جوملا في رؤوس HTTP
                if 'generator' in response.headers:
                    if 'joomla' in response.headers['generator'].lower():
                        self.logger.info(f"تم التأكد من استخدام جوملا في الموقع: {self.url}")
                        return True
                
                # البحث عن وسم generator في HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                generator = soup.find('meta', attrs={'name': 'generator'})
                if generator and 'joomla' in generator.get('content', '').lower():
                    self.logger.info(f"تم التأكد من استخدام جوملا في الموقع: {self.url}")
                    return True
            
            self.logger.info(f"لم يتم التأكد من استخدام جوملا في الموقع: {self.url}")
            return False
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من استخدام جوملا: {str(e)}")
            return False
    
    def get_joomla_info(self):
        """الحصول على معلومات جوملا"""
        self.logger.info(f"جاري جمع معلومات جوملا للموقع: {self.url}")
        
        joomla_info = {}
        
        try:
            # التحقق من إصدار جوملا
            version = self._get_joomla_version()
            if version:
                joomla_info['الإصدار'] = version
            
            # الحصول على القالب المستخدم
            template = self._get_joomla_template()
            if template:
                joomla_info['القالب'] = template
            
            # الحصول على قائمة المكونات
            components = self._get_joomla_components()
            if components:
                joomla_info['المكونات'] = components
            
            if self.verbose:
                self.logger.debug(f"تم جمع معلومات جوملا: {json.dumps(joomla_info, ensure_ascii=False)}")
            
            return joomla_info
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات جوملا: {str(e)}")
            return {'خطأ': str(e)}
    
    def _get_joomla_version(self):
        """الحصول على إصدار جوملا"""
        version = None
        
        # طرق مختلفة للحصول على إصدار جوملا
        methods = [
            # من ملف joomla.xml
            {'path': '/administrator/manifests/files/joomla.xml', 'pattern': r'<version>([\d.]+)</version>'},
            # من ملف اللغة
            {'path': '/language/en-GB/en-GB.xml', 'pattern': r'<version>([\d.]+)</version>'},
            # من ملف README.txt
            {'path': '/README.txt', 'pattern': r'Joomla!\s+([\d.]+)'},
            # من وسم generator
            {'path': '/', 'pattern': r'<meta\s+name="generator"\s+content="Joomla!\s+([\d.]+)'},
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
                self.logger.error(f"خطأ في الحصول على إصدار جوملا من {method['path']}: {str(e)}")
        
        return version
    
    def _get_joomla_template(self):
        """الحصول على القالب المستخدم في جوملا"""
        template_info = {}
        
        try:
            # الحصول على محتوى الصفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            
            if response and response.status_code == 200:
                # البحث عن مسار القالب في محتوى الصفحة
                template_pattern = r'/templates/([^/]+)'
                template_matches = re.findall(template_pattern, response.text)
                
                if template_matches:
                    template_name = template_matches[0]
                    template_info['الاسم'] = template_name
                    
                    # التحقق من وجود ملف templateDetails.xml للقالب
                    template_details_url = urljoin(self.url, f'/templates/{template_name}/templateDetails.xml')
                    template_details_response = safe_request(template_details_url, timeout=self.timeout)
                    
                    if template_details_response and template_details_response.status_code == 200:
                        # البحث عن معلومات القالب في ملف templateDetails.xml
                        template_version_pattern = r'<version>([\d.]+)</version>'
                        template_version_match = re.search(template_version_pattern, template_details_response.text)
                        
                        if template_version_match:
                            template_info['الإصدار'] = template_version_match.group(1)
                        
                        template_author_pattern = r'<author>(.+)</author>'
                        template_author_match = re.search(template_author_pattern, template_details_response.text)
                        
                        if template_author_match:
                            template_info['المطور'] = template_author_match.group(1)
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات القالب: {str(e)}")
        
        return template_info
    
    def _get_joomla_components(self):
        """الحصول على قائمة المكونات المستخدمة في جوملا"""
        components = []
        
        try:
            # الحصول على محتوى الصفحة الرئيسية
            response = safe_request(self.url, timeout=self.timeout)
            
            if response and response.status_code == 200:
                # البحث عن مسارات المكونات في محتوى الصفحة
                component_pattern = r'com_([a-zA-Z0-9_]+)'
                component_matches = re.findall(component_pattern, response.text)
                
                # إزالة التكرارات
                unique_components = set(component_matches)
                
                for component_name in unique_components:
                    components.append({'الاسم': f'com_{component_name}'})
                    
                    # محاولة التحقق من وجود ملف XML للمكون
                    component_xml_url = urljoin(self.url, f'/administrator/components/com_{component_name}/{component_name}.xml')
                    component_xml_response = safe_request(component_xml_url, timeout=self.timeout)
                    
                    if component_xml_response and component_xml_response.status_code == 200:
                        # البحث عن إصدار المكون في ملف XML
                        component_version_pattern = r'<version>([\d.]+)</version>'
                        component_version_match = re.search(component_version_pattern, component_xml_response.text)
                        
                        if component_version_match:
                            components[-1]['الإصدار'] = component_version_match.group(1)
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على قائمة المكونات: {str(e)}")
        
        return components
    
    def scan_vulnerabilities(self):
        """فحص الثغرات الأمنية في جوملا"""
        self.logger.info(f"جاري فحص الثغرات الأمنية في جوملا للموقع: {self.url}")
        
        vulnerabilities = []
        
        try:
            # التحقق من الثغرات الشائعة في جوملا
            with ThreadPoolExecutor(max_workers=5) as executor:
                # إنشاء قائمة بالمهام
                futures = [executor.submit(self._check_vulnerability, vuln) for vuln in self.common_vulnerabilities]
                
                # جمع النتائج
                for future in futures:
                    result = future.result()
                    if result:
                        vulnerabilities.append(result)
            
            # التحقق من إصدار جوملا
            version = self._get_joomla_version()
            if version:
                # التحقق من الإصدار القديم
                if self._is_outdated_version(version):
                    vulnerabilities.append({
                        'name': 'إصدار جوملا قديم',
                        'severity': 'عالية',
                        'description': f'يستخدم الموقع إصدار قديم من جوملا ({version})، مما قد يعرضه للثغرات الأمنية.',
                        'evidence': f'الإصدار: {version}'
                    })
            
            # التحقق من وجود صفحة تسجيل الدخول الافتراضية
            admin_url = urljoin(self.url, '/administrator/')
            admin_response = safe_request(admin_url, timeout=self.timeout)
            if admin_response and admin_response.status_code == 200:
                vulnerabilities.append({
                    'name': 'صفحة تسجيل الدخول الافتراضية',
                    'severity': 'منخفضة',
                    'description': 'صفحة تسجيل الدخول الافتراضية متاحة، مما قد يسهل هجمات القوة الغاشمة.',
                    'evidence': admin_url
                })
            
            if self.verbose:
                self.logger.debug(f"تم اكتشاف {len(vulnerabilities)} ثغرة أمنية في جوملا")
            
            return vulnerabilities
        
        except Exception as e:
            self.logger.error(f"خطأ في فحص الثغرات الأمنية في جوملا: {str(e)}")
            return []
    
    def _check_vulnerability(self, vuln):
        """التحقق من ثغرة أمنية محددة"""
        try:
            full_url = urljoin(self.url, vuln['path'])
            response = safe_request(full_url, timeout=self.timeout)
            
            if response:
                # إذا كان هناك نمط محدد للبحث
                if vuln['pattern']:
                    match = re.search(vuln['pattern'], response.text)
                    if match:
                        evidence = match.group(1) if '(' in vuln['pattern'] else vuln['pattern']
                        return {
                            'name': vuln['name'],
                            'severity': vuln['severity'],
                            'description': vuln['description'],
                            'evidence': f'تم العثور على "{evidence}" في {vuln["path"]}'
                        }
                # حالات خاصة
                elif vuln['path'] == '/installation/' and response.status_code != 404:
                    return {
                        'name': vuln['name'],
                        'severity': vuln['severity'],
                        'description': vuln['description'],
                        'evidence': f'مجلد التثبيت متاح (رمز الحالة: {response.status_code})'
                    }
                elif vuln['path'] == '/configuration.php-dist' and response.status_code != 404:
                    return {
                        'name': vuln['name'],
                        'severity': vuln['severity'],
                        'description': vuln['description'],
                        'evidence': f'ملف التكوين النموذجي متاح (رمز الحالة: {response.status_code})'
                    }
            
            return None
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الثغرة {vuln['name']}: {str(e)}")
            return None
    
    def _is_outdated_version(self, version):
        """التحقق مما إذا كان إصدار جوملا قديمًا"""
        # هذه مجرد قيمة افتراضية، يجب تحديثها بانتظام
        latest_version = '4.3.3'  # آخر إصدار من جوملا وقت كتابة الكود
        
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