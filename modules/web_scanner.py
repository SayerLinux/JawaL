#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة فحص مواقع الويب
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import re
import json
import socket
import logging
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from .utils import safe_request, get_user_agent, extract_domain, is_ip_address

class WebScanner:
    """فئة لفحص مواقع الويب وجمع المعلومات المرتبطة بها"""
    
    def __init__(self, url, ports=None, timeout=30, verbose=False):
        """تهيئة فاحص موقع الويب"""
        self.url = url
        self.domain = extract_domain(url)
        self.timeout = timeout
        self.verbose = verbose
        self.logger = logging.getLogger('jawal')
        self.ports = ports if ports else [80, 443]
        
        # قائمة بالتقنيات الشائعة للكشف
        self.common_technologies = [
            {'name': 'WordPress', 'pattern': ['wp-content', 'wp-includes', 'WordPress']},
            {'name': 'Joomla', 'pattern': ['joomla', 'Joomla!', '/administrator/']},
            {'name': 'Drupal', 'pattern': ['Drupal', 'drupal']},
            {'name': 'Magento', 'pattern': ['Magento', 'magento']},
            {'name': 'Shopify', 'pattern': ['Shopify', 'shopify']},
            {'name': 'WooCommerce', 'pattern': ['woocommerce', 'WooCommerce']},
            {'name': 'PrestaShop', 'pattern': ['PrestaShop', 'prestashop']},
            {'name': 'OpenCart', 'pattern': ['OpenCart', 'opencart']},
            {'name': 'Laravel', 'pattern': ['Laravel', 'laravel']},
            {'name': 'Django', 'pattern': ['Django', 'django']},
            {'name': 'Ruby on Rails', 'pattern': ['Ruby on Rails', 'rails']},
            {'name': 'ASP.NET', 'pattern': ['ASP.NET', 'asp.net']},
            {'name': 'PHP', 'pattern': ['PHP', 'php']},
            {'name': 'jQuery', 'pattern': ['jQuery', 'jquery']},
            {'name': 'Bootstrap', 'pattern': ['Bootstrap', 'bootstrap']},
            {'name': 'React', 'pattern': ['React', 'react']},
            {'name': 'Angular', 'pattern': ['Angular', 'angular']},
            {'name': 'Vue.js', 'pattern': ['Vue', 'vue']},
            {'name': 'Node.js', 'pattern': ['Node.js', 'node']},
            {'name': 'Express', 'pattern': ['Express', 'express']},
            {'name': 'Apache', 'pattern': ['Apache', 'apache']},
            {'name': 'Nginx', 'pattern': ['Nginx', 'nginx']},
            {'name': 'IIS', 'pattern': ['IIS', 'iis']},
            {'name': 'Cloudflare', 'pattern': ['Cloudflare', 'cloudflare']},
            {'name': 'Akamai', 'pattern': ['Akamai', 'akamai']},
            {'name': 'Fastly', 'pattern': ['Fastly', 'fastly']},
            {'name': 'Sucuri', 'pattern': ['Sucuri', 'sucuri']},
            {'name': 'Imperva', 'pattern': ['Imperva', 'imperva']},
            {'name': 'ModSecurity', 'pattern': ['ModSecurity', 'modsecurity']},
        ]
        
        # قائمة بالثغرات الشائعة للكشف
        self.common_vulnerabilities = [
            {
                'name': 'XSS (Cross-Site Scripting)',
                'pattern': ['<script>', 'alert(', 'onerror=', 'onload='],
                'severity': 'عالية',
                'description': 'ثغرة تسمح بحقن وتنفيذ أكواد JavaScript ضارة في صفحات الويب.'
            },
            {
                'name': 'SQL Injection',
                'pattern': ['SQL syntax', 'mysql_fetch_array', 'ORA-', 'Microsoft SQL Server'],
                'severity': 'عالية',
                'description': 'ثغرة تسمح بحقن استعلامات SQL ضارة في قاعدة البيانات.'
            },
            {
                'name': 'Directory Listing',
                'pattern': ['Index of /', 'Directory Listing'],
                'severity': 'متوسطة',
                'description': 'كشف محتويات المجلدات على الخادم، مما قد يؤدي إلى تسرب معلومات حساسة.'
            },
            {
                'name': 'Information Disclosure',
                'pattern': ['phpinfo()', 'PHP Version', 'Server at', 'Apache Version'],
                'severity': 'متوسطة',
                'description': 'كشف معلومات حساسة عن الخادم أو التطبيق.'
            },
            {
                'name': 'Insecure HTTP Headers',
                'pattern': [],  # سيتم التحقق من الرؤوس في دالة منفصلة
                'severity': 'منخفضة',
                'description': 'عدم وجود رؤوس HTTP أمنية مهمة مثل X-XSS-Protection و Content-Security-Policy.'
            },
            {
                'name': 'Outdated Software',
                'pattern': [],  # سيتم التحقق من الإصدارات في دالة منفصلة
                'severity': 'متوسطة',
                'description': 'استخدام إصدارات قديمة من البرامج قد تحتوي على ثغرات أمنية معروفة.'
            },
            {
                'name': 'Insecure Cookies',
                'pattern': [],  # سيتم التحقق من ملفات تعريف الارتباط في دالة منفصلة
                'severity': 'متوسطة',
                'description': 'عدم تعيين خصائص أمنية لملفات تعريف الارتباط مثل Secure و HttpOnly.'
            },
        ]
    
    def get_site_info(self):
        """الحصول على معلومات الموقع"""
        self.logger.info(f"جاري جمع معلومات الموقع: {self.url}")
        
        site_info = {}
        
        try:
            # إجراء طلب HTTP للحصول على معلومات الموقع
            response = safe_request(self.url, timeout=self.timeout)
            
            if response:
                # استخراج معلومات الموقع من الاستجابة
                site_info['عنوان URL'] = self.url
                site_info['النطاق'] = self.domain
                site_info['رمز الحالة'] = response.status_code
                site_info['نوع المحتوى'] = response.headers.get('Content-Type', 'غير معروف')
                site_info['الخادم'] = response.headers.get('Server', 'غير معروف')
                
                # استخراج العنوان من صفحة HTML
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    site_info['العنوان'] = soup.title.string.strip() if soup.title else 'بدون عنوان'
                    
                    # استخراج الوصف من الوسوم الوصفية
                    meta_description = soup.find('meta', attrs={'name': 'description'})
                    if meta_description:
                        site_info['الوصف'] = meta_description.get('content', 'بدون وصف')
                    
                    # استخراج الكلمات المفتاحية من الوسوم الوصفية
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    if meta_keywords:
                        site_info['الكلمات المفتاحية'] = meta_keywords.get('content', 'بدون كلمات مفتاحية')
                except Exception as e:
                    self.logger.error(f"خطأ في استخراج معلومات HTML: {str(e)}")
                
                # التحقق من وجود ملف robots.txt
                robots_url = f"{self.url.rstrip('/')}/robots.txt"
                robots_response = safe_request(robots_url, timeout=self.timeout)
                if robots_response and robots_response.status_code == 200:
                    site_info['robots.txt'] = 'موجود'
                else:
                    site_info['robots.txt'] = 'غير موجود'
                
                # التحقق من وجود ملف sitemap.xml
                sitemap_url = f"{self.url.rstrip('/')}/sitemap.xml"
                sitemap_response = safe_request(sitemap_url, timeout=self.timeout)
                if sitemap_response and sitemap_response.status_code == 200:
                    site_info['sitemap.xml'] = 'موجود'
                else:
                    site_info['sitemap.xml'] = 'غير موجود'
                
                # التحقق من وجود HTTPS
                if self.url.startswith('https'):
                    site_info['HTTPS'] = 'مفعل'
                else:
                    site_info['HTTPS'] = 'غير مفعل'
                
                # التحقق من رؤوس HTTP الأمنية
                security_headers = self._check_security_headers(response.headers)
                if security_headers:
                    site_info['رؤوس HTTP الأمنية'] = security_headers
            
            if self.verbose:
                self.logger.debug(f"تم جمع معلومات الموقع: {json.dumps(site_info, ensure_ascii=False)}")
            
            return site_info
        
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات الموقع: {str(e)}")
            return {'عنوان URL': self.url, 'النطاق': self.domain, 'خطأ': str(e)}
    
    def _check_security_headers(self, headers):
        """التحقق من رؤوس HTTP الأمنية"""
        security_headers = {}
        
        # قائمة برؤوس HTTP الأمنية المهمة
        important_headers = {
            'Strict-Transport-Security': 'يفرض استخدام HTTPS',
            'Content-Security-Policy': 'يحدد مصادر المحتوى المسموح بها',
            'X-Content-Type-Options': 'يمنع تخمين نوع MIME',
            'X-Frame-Options': 'يمنع تضمين الموقع في إطارات',
            'X-XSS-Protection': 'يوفر حماية من هجمات XSS',
            'Referrer-Policy': 'يتحكم في معلومات المرجع المرسلة',
            'Feature-Policy': 'يتحكم في ميزات المتصفح المتاحة',
            'Permissions-Policy': 'يتحكم في أذونات المتصفح',
        }
        
        for header, description in important_headers.items():
            if header in headers:
                security_headers[header] = 'موجود'
            else:
                security_headers[header] = 'غير موجود'
        
        return security_headers
    
    def detect_technologies(self):
        """تحديد التقنيات المستخدمة في الموقع"""
        self.logger.info(f"جاري تحديد التقنيات المستخدمة في الموقع: {self.url}")
        
        technologies = []
        
        try:
            # إجراء طلب HTTP للحصول على محتوى الصفحة
            response = safe_request(self.url, timeout=self.timeout)
            
            if response:
                # البحث عن التقنيات في محتوى الصفحة والرؤوس
                page_content = response.text
                headers = response.headers
                
                # التحقق من التقنيات الشائعة
                for tech in self.common_technologies:
                    # البحث في محتوى الصفحة
                    for pattern in tech['pattern']:
                        if pattern in page_content:
                            # محاولة تحديد الإصدار
                            version = self._detect_version(tech['name'], page_content, headers)
                            technologies.append({
                                'name': tech['name'],
                                'version': version if version else 'غير معروف',
                                'confidence': 'عالية' if version else 'متوسطة'
                            })
                            break
                
                # التحقق من التقنيات من خلال رؤوس HTTP
                if 'Server' in headers:
                    server = headers['Server']
                    if server not in [tech['name'] for tech in technologies]:
                        technologies.append({
                            'name': server,
                            'version': 'غير معروف',
                            'confidence': 'عالية'
                        })
                
                # التحقق من وجود لغات البرمجة الشائعة
                if 'X-Powered-By' in headers:
                    powered_by = headers['X-Powered-By']
                    if powered_by not in [tech['name'] for tech in technologies]:
                        technologies.append({
                            'name': powered_by,
                            'version': 'غير معروف',
                            'confidence': 'عالية'
                        })
            
            if self.verbose:
                self.logger.debug(f"تم تحديد {len(technologies)} تقنية")
            
            return technologies
        
        except Exception as e:
            self.logger.error(f"خطأ في تحديد التقنيات: {str(e)}")
            return []
    
    def _detect_version(self, technology, content, headers):
        """محاولة تحديد إصدار التقنية"""
        version = None
        
        # أنماط الإصدارات الشائعة
        version_patterns = {
            'WordPress': [r'WordPress ([\d.]+)', r'wp-content/themes/[^/]+/style\.css\?ver=([\d.]+)'],
            'Joomla': [r'Joomla!\s+([\d.]+)', r'<meta name="generator" content="Joomla! ([\d.]+)'],
            'Drupal': [r'Drupal ([\d.]+)', r'<meta name="generator" content="Drupal ([\d.]+)'],
            'PHP': [r'PHP/([\d.]+)', r'X-Powered-By: PHP/([\d.]+)'],
            'Apache': [r'Apache/([\d.]+)', r'Server: Apache/([\d.]+)'],
            'Nginx': [r'nginx/([\d.]+)', r'Server: nginx/([\d.]+)'],
        }
        
        # التحقق من أنماط الإصدارات
        if technology in version_patterns:
            for pattern in version_patterns[technology]:
                match = re.search(pattern, content)
                if match:
                    version = match.group(1)
                    break
        
        # التحقق من رؤوس HTTP للإصدارات
        if not version:
            if technology == 'PHP' and 'X-Powered-By' in headers:
                match = re.search(r'PHP/([\d.]+)', headers['X-Powered-By'])
                if match:
                    version = match.group(1)
            elif (technology == 'Apache' or technology == 'Nginx') and 'Server' in headers:
                match = re.search(f'{technology}/([\d.]+)', headers['Server'])
                if match:
                    version = match.group(1)
        
        return version
    
    def scan_vulnerabilities(self):
        """فحص الثغرات الأمنية في الموقع"""
        self.logger.info(f"جاري فحص الثغرات الأمنية في الموقع: {self.url}")
        
        vulnerabilities = []
        
        try:
            # إجراء طلب HTTP للحصول على محتوى الصفحة
            response = safe_request(self.url, timeout=self.timeout)
            
            if response:
                # البحث عن الثغرات في محتوى الصفحة والرؤوس
                page_content = response.text
                headers = response.headers
                
                # التحقق من الثغرات الشائعة
                for vuln in self.common_vulnerabilities:
                    # البحث في محتوى الصفحة
                    for pattern in vuln['pattern']:
                        if pattern and pattern in page_content:
                            vulnerabilities.append({
                                'name': vuln['name'],
                                'severity': vuln['severity'],
                                'description': vuln['description'],
                                'evidence': pattern
                            })
                            break
                
                # التحقق من رؤوس HTTP الأمنية المفقودة
                missing_security_headers = self._check_missing_security_headers(headers)
                if missing_security_headers:
                    vulnerabilities.append({
                        'name': 'رؤوس HTTP أمنية مفقودة',
                        'severity': 'منخفضة',
                        'description': 'عدم وجود رؤوس HTTP أمنية مهمة قد يؤدي إلى ضعف أمني.',
                        'evidence': ', '.join(missing_security_headers)
                    })
                
                # التحقق من ملفات تعريف الارتباط غير الآمنة
                insecure_cookies = self._check_insecure_cookies(response.cookies)
                if insecure_cookies:
                    vulnerabilities.append({
                        'name': 'ملفات تعريف ارتباط غير آمنة',
                        'severity': 'متوسطة',
                        'description': 'ملفات تعريف الارتباط لا تستخدم خصائص أمنية مثل Secure و HttpOnly.',
                        'evidence': ', '.join(insecure_cookies)
                    })
                
                # التحقق من وجود HTTPS
                if not self.url.startswith('https'):
                    vulnerabilities.append({
                        'name': 'عدم استخدام HTTPS',
                        'severity': 'عالية',
                        'description': 'الموقع لا يستخدم HTTPS، مما يعرض البيانات للاعتراض.',
                        'evidence': self.url
                    })
                
                # التحقق من وجود قائمة المجلدات
                if 'Index of /' in page_content or 'Directory Listing' in page_content:
                    vulnerabilities.append({
                        'name': 'قائمة المجلدات مفعلة',
                        'severity': 'متوسطة',
                        'description': 'قائمة المجلدات مفعلة، مما قد يؤدي إلى كشف ملفات حساسة.',
                        'evidence': 'Index of / أو Directory Listing'
                    })
            
            if self.verbose:
                self.logger.debug(f"تم اكتشاف {len(vulnerabilities)} ثغرة أمنية")
            
            return vulnerabilities
        
        except Exception as e:
            self.logger.error(f"خطأ في فحص الثغرات الأمنية: {str(e)}")
            return []
    
    def _check_missing_security_headers(self, headers):
        """التحقق من رؤوس HTTP الأمنية المفقودة"""
        missing_headers = []
        
        # قائمة برؤوس HTTP الأمنية المهمة
        important_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
        ]
        
        for header in important_headers:
            if header not in headers:
                missing_headers.append(header)
        
        return missing_headers
    
    def _check_insecure_cookies(self, cookies):
        """التحقق من ملفات تعريف الارتباط غير الآمنة"""
        insecure_cookies = []
        
        for cookie in cookies:
            if not cookie.secure:
                insecure_cookies.append(f"{cookie.name} (بدون Secure)")
            if not cookie.has_nonstandard_attr('HttpOnly'):
                insecure_cookies.append(f"{cookie.name} (بدون HttpOnly)")
        
        return insecure_cookies
    
    def scan_ports(self):
        """فحص المنافذ المفتوحة"""
        self.logger.info(f"جاري فحص المنافذ المفتوحة للنطاق: {self.domain}")
        
        open_ports = []
        
        try:
            # التحقق مما إذا كان النطاق عبارة عن عنوان IP
            if is_ip_address(self.domain):
                ip = self.domain
            else:
                # الحصول على عنوان IP للنطاق
                ip = socket.gethostbyname(self.domain)
            
            # فحص المنافذ باستخدام ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=10) as executor:
                # إنشاء قائمة بالمهام
                futures = [executor.submit(self._check_port, ip, port) for port in self.ports]
                
                # جمع النتائج
                for future in futures:
                    result = future.result()
                    if result:
                        open_ports.append(result)
            
            if self.verbose:
                self.logger.debug(f"تم اكتشاف {len(open_ports)} منفذ مفتوح")
            
            return open_ports
        
        except Exception as e:
            self.logger.error(f"خطأ في فحص المنافذ: {str(e)}")
            return []
    
    def _check_port(self, ip, port):
        """التحقق من حالة منفذ محدد"""
        try:
            # إنشاء مقبس TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # محاولة الاتصال بالمنفذ
            result = sock.connect_ex((ip, port))
            sock.close()
            
            # إذا كان المنفذ مفتوحًا
            if result == 0:
                # محاولة تحديد الخدمة
                service = self._get_service_name(port)
                
                return {
                    'port': port,
                    'state': 'open',
                    'service': service
                }
            
            return None
        
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من المنفذ {port}: {str(e)}")
            return None
    
    def _get_service_name(self, port):
        """الحصول على اسم الخدمة بناءً على رقم المنفذ"""
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            465: 'SMTPS',
            587: 'SMTP (Submission)',
            993: 'IMAPS',
            995: 'POP3S',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            8080: 'HTTP Proxy',
            8443: 'HTTPS Alternate',
        }
        
        return common_ports.get(port, 'غير معروف')