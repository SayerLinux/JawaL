#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - اختبارات وحدة الأدوات المساعدة
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import unittest
import sys
import os

# إضافة المجلد الرئيسي إلى مسار البحث
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.utils import (
    validate_phone_number,
    validate_url,
    validate_username,
    generate_random_string,
    extract_domain,
    is_ip_address,
    sanitize_filename,
    parse_port_range
)

class TestUtils(unittest.TestCase):
    """اختبارات لوحدة الأدوات المساعدة"""
    
    def test_validate_phone_number(self):
        """اختبار التحقق من صحة رقم الهاتف"""
        # أرقام صحيحة
        self.assertTrue(validate_phone_number('+966501234567'))
        self.assertTrue(validate_phone_number('00966501234567'))
        self.assertTrue(validate_phone_number('0501234567'))
        
        # أرقام غير صحيحة
        self.assertFalse(validate_phone_number('123'))
        self.assertFalse(validate_phone_number('abc'))
        self.assertFalse(validate_phone_number(''))
    
    def test_validate_url(self):
        """اختبار التحقق من صحة عنوان URL"""
        # عناوين صحيحة
        self.assertTrue(validate_url('http://example.com'))
        self.assertTrue(validate_url('https://example.com'))
        self.assertTrue(validate_url('http://sub.example.com/path'))
        
        # عناوين غير صحيحة
        self.assertFalse(validate_url('example.com'))
        self.assertFalse(validate_url('ftp://example.com'))
        self.assertFalse(validate_url(''))
    
    def test_validate_username(self):
        """اختبار التحقق من صحة اسم المستخدم"""
        # أسماء صحيحة
        self.assertTrue(validate_username('user123'))
        self.assertTrue(validate_username('user_123'))
        self.assertTrue(validate_username('user.123'))
        
        # أسماء غير صحيحة
        self.assertFalse(validate_username('us'))
        self.assertFalse(validate_username('user@123'))
        self.assertFalse(validate_username(''))
    
    def test_generate_random_string(self):
        """اختبار توليد سلسلة عشوائية"""
        # اختبار الطول
        self.assertEqual(len(generate_random_string(10)), 10)
        self.assertEqual(len(generate_random_string(5)), 5)
        
        # اختبار الفريد
        self.assertNotEqual(generate_random_string(10), generate_random_string(10))
    
    def test_extract_domain(self):
        """اختبار استخراج اسم النطاق"""
        self.assertEqual(extract_domain('http://example.com'), 'example.com')
        self.assertEqual(extract_domain('https://sub.example.com/path'), 'sub.example.com')
        self.assertEqual(extract_domain('https://www.example.co.uk'), 'example.co.uk')
    
    def test_is_ip_address(self):
        """اختبار التحقق من عنوان IP"""
        # عناوين صحيحة
        self.assertTrue(is_ip_address('192.168.1.1'))
        self.assertTrue(is_ip_address('10.0.0.1'))
        self.assertTrue(is_ip_address('8.8.8.8'))
        
        # عناوين غير صحيحة
        self.assertFalse(is_ip_address('256.256.256.256'))
        self.assertFalse(is_ip_address('example.com'))
        self.assertFalse(is_ip_address(''))
    
    def test_sanitize_filename(self):
        """اختبار تنظيف اسم الملف"""
        self.assertEqual(sanitize_filename('file name'), 'file_name')
        self.assertEqual(sanitize_filename('file/name'), 'file_name')
        self.assertEqual(sanitize_filename('file\\name'), 'file_name')
        self.assertEqual(sanitize_filename('file:*?"<>|name'), 'file_name')
    
    def test_parse_port_range(self):
        """اختبار تحليل نطاق المنافذ"""
        # منافذ فردية
        self.assertEqual(parse_port_range('80'), [80])
        self.assertEqual(parse_port_range('80,443'), [80, 443])
        
        # نطاق المنافذ
        self.assertEqual(parse_port_range('80-82'), [80, 81, 82])
        self.assertEqual(parse_port_range('80,90-92'), [80, 90, 91, 92])
        
        # قيم غير صالحة
        self.assertEqual(parse_port_range(''), [])
        self.assertEqual(parse_port_range('abc'), [])

if __name__ == '__main__':
    unittest.main()