#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة الأدوات المساعدة
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import os
import re
import logging
import random
import string
import requests
from datetime import datetime
from urllib.parse import urlparse

def setup_logger():
    """إعداد وحدة التسجيل"""
    # إنشاء مجلد للسجلات إذا لم يكن موجودًا
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # إنشاء اسم ملف السجل بناءً على التاريخ والوقت الحالي
    log_filename = os.path.join(logs_dir, f"jawal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # إعداد وحدة التسجيل
    logger = logging.getLogger('jawal')
    logger.setLevel(logging.DEBUG)
    
    # إعداد معالج الملف
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    
    # إعداد معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # إعداد تنسيق السجل
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # إضافة المعالجات إلى وحدة التسجيل
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف"""
    try:
        if not phone:
            return False
            
        # إزالة المسافات والرموز غير المطلوبة
        phone = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # إضافة + إذا لم يكن موجودًا وكان الرقم يبدأ بـ 00
        if phone.startswith('00'):
            phone = '+' + phone[2:]
        elif not phone.startswith('+'):
            phone = '+' + phone
        
        # التحقق من أن رقم الهاتف يبدأ بـ + ويتكون من أرقام فقط
        pattern = r'^\+[0-9]{10,15}$'
        return bool(re.match(pattern, phone))
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في التحقق من صحة رقم الهاتف: {e}")
        return False

def validate_url(url):
    """التحقق من صحة عنوان URL"""
    try:
        if not url:
            return False
            
        # إضافة بروتوكول http إذا لم يكن موجودًا
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في التحقق من صحة URL: {e}")
        return False

def validate_username(username):
    """التحقق من صحة اسم المستخدم"""
    try:
        if not username:
            return False
            
        # إزالة المسافات في البداية والنهاية
        username = username.strip()
        
        # التحقق من أن اسم المستخدم يتكون من أحرف وأرقام وشرطة سفلية ونقطة فقط ويتراوح طوله بين 3 و 30 حرفًا
        pattern = r'^[a-zA-Z0-9_\.]{3,30}$'
        return bool(re.match(pattern, username))
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في التحقق من صحة اسم المستخدم: {e}")
        return False

def generate_random_string(length=10):
    """إنشاء سلسلة عشوائية"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_user_agent():
    """الحصول على عميل مستخدم عشوائي"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    ]
    return random.choice(user_agents)

def safe_request(url, method='GET', headers=None, params=None, data=None, timeout=30, verify=True, allow_redirects=True, max_retries=3):
    """إجراء طلب HTTP آمن مع معالجة الأخطاء"""
    if headers is None:
        headers = {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
    
    # التحقق من صحة URL
    if not url or not validate_url(url):
        logger = logging.getLogger('jawal')
        logger.error(f"عنوان URL غير صالح: {url}")
        return None
    
    # محاولة إجراء الطلب مع إعادة المحاولة
    for attempt in range(max_retries):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                timeout=timeout,
                verify=verify,
                allow_redirects=allow_redirects
            )
            return response
        except requests.exceptions.Timeout:
            logger = logging.getLogger('jawal')
            logger.warning(f"انتهت مهلة الطلب: {url} - المحاولة {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                logger.error(f"فشلت جميع محاولات الاتصال: {url}")
                return None
        except requests.exceptions.ConnectionError:
            logger = logging.getLogger('jawal')
            logger.warning(f"خطأ في الاتصال: {url} - المحاولة {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                logger.error(f"فشلت جميع محاولات الاتصال: {url}")
                return None
        except requests.exceptions.RequestException as e:
            logger = logging.getLogger('jawal')
            logger.error(f"خطأ في الطلب: {url} - {str(e)}")
            return None

def extract_domain(url):
    """استخراج اسم النطاق من عنوان URL"""
    try:
        if not url:
            return ""
            
        # إضافة بروتوكول إذا لم يكن موجودًا
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # إزالة www. إذا كانت موجودة
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في استخراج النطاق: {url} - {str(e)}")
        return url

def is_ip_address(address):
    """التحقق مما إذا كان العنوان عبارة عن عنوان IP"""
    try:
        if not address:
            return False
            
        # إزالة المسافات في البداية والنهاية
        address = address.strip()
        
        # التحقق من صحة عنوان IP
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        if re.match(ip_pattern, address):
            # التحقق من صحة القيم
            octets = address.split('.')
            for octet in octets:
                if int(octet) > 255:
                    return False
            return True
        return False
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في التحقق من عنوان IP: {address} - {str(e)}")
        return False

def format_timestamp(timestamp):
    """تنسيق الطابع الزمني إلى تنسيق قابل للقراءة"""
    try:
        if not timestamp:
            return ""
            
        # التحقق من نوع البيانات
        if isinstance(timestamp, str):
            try:
                timestamp = float(timestamp)
            except ValueError:
                return timestamp
                
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في تنسيق الطابع الزمني: {timestamp} - {str(e)}")
        return str(timestamp)

def sanitize_filename(filename):
    """تنظيف اسم الملف من الأحرف غير المسموح بها"""
    try:
        if not filename:
            return "report"
            
        # استبدال الأحرف غير المسموح بها في اسم الملف بشرطة سفلية
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # إزالة المسافات المتعددة والمسافات في البداية والنهاية
        filename = ' '.join(filename.split())
        
        # التأكد من أن اسم الملف لا يتجاوز 255 حرفًا
        if len(filename) > 255:
            filename = filename[:255]
            
        return filename
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في تنظيف اسم الملف: {e}")
        return "report"

def get_file_extension(content_type):
    """الحصول على امتداد الملف بناءً على نوع المحتوى"""
    try:
        if not content_type:
            return 'txt'
            
        # تنظيف نوع المحتوى وتحويله إلى حروف صغيرة
        content_type = content_type.strip().lower()
        
        # إزالة أي معلمات إضافية (مثل charset)
        if ';' in content_type:
            content_type = content_type.split(';')[0].strip()
            
        extensions = {
            'text/html': 'html',
            'text/plain': 'txt',
            'application/json': 'json',
            'application/xml': 'xml',
            'application/pdf': 'pdf',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'application/javascript': 'js',
            'text/css': 'css',
            'application/zip': 'zip',
            'application/x-tar': 'tar',
            'application/x-gzip': 'gz',
            'application/octet-stream': 'bin'
        }
        return extensions.get(content_type, 'txt')
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في الحصول على امتداد الملف: {e}")
        return 'txt'

def parse_port_range(port_range):
    """تحليل نطاق المنافذ"""
    ports = []
    if not port_range:
        return ports
    
    try:
        for part in port_range.split(','):
            part = part.strip()
            if not part:
                continue
                
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                if start > end:
                    start, end = end, start
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        
        # إزالة المنافذ المكررة
        ports = list(set(ports))
        # التأكد من أن المنافذ ضمن النطاق الصحيح
        ports = [p for p in ports if 1 <= p <= 65535]
        
        return ports
    except ValueError as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في تحليل نطاق المنافذ: {e}")
        return [80, 443]  # القيم الافتراضية في حالة الخطأ

def get_severity_color(severity):
    """الحصول على لون بناءً على مستوى الخطورة"""
    try:
        if not severity:
            return 'blue'
            
        # تحويل إلى حروف صغيرة وإزالة المسافات
        severity = str(severity).lower().strip()
        
        if severity in ['critical', 'high', 'حرج', 'عالي']:
            return 'red'
        elif severity in ['medium', 'متوسط']:
            return 'yellow'
        elif severity in ['low', 'info', 'منخفض', 'معلومات']:
            return 'green'
        else:
            return 'blue'
    except Exception as e:
        logger = logging.getLogger('jawal')
        logger.error(f"خطأ في الحصول على لون الخطورة: {e}")
        return 'blue'