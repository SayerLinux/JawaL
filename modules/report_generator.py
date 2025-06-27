#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - وحدة إنشاء التقارير
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import os
import json
import logging
import datetime
from pathlib import Path
from jinja2 import Template
from .utils import format_timestamp, sanitize_filename

class ReportGenerator:
    """فئة لإنشاء تقارير مفصلة عن نتائج الفحص"""
    
    def __init__(self, output_dir=None, report_format='text', verbose=False):
        """تهيئة منشئ التقارير"""
        self.logger = logging.getLogger('jawal')
        self.verbose = verbose
        
        # تحديد مجلد الإخراج
        if output_dir:
            self.output_dir = output_dir
        else:
            # استخدام مجلد التقارير الافتراضي
            self.output_dir = os.path.join(os.getcwd(), 'reports')
        
        # التأكد من وجود مجلد الإخراج
        os.makedirs(self.output_dir, exist_ok=True)
        
        # تحديد تنسيق التقرير
        self.report_format = report_format.lower()
        if self.report_format not in ['text', 'json', 'html', 'markdown']:
            self.logger.warning(f"تنسيق التقرير غير معروف: {report_format}، سيتم استخدام التنسيق النصي")
            self.report_format = 'text'
    
    def generate_phone_report(self, phone_number, scan_results):
        """إنشاء تقرير عن نتائج فحص رقم الهاتف"""
        self.logger.info(f"جاري إنشاء تقرير لرقم الهاتف: {phone_number}")
        
        # إنشاء اسم ملف آمن
        timestamp = format_timestamp(datetime.datetime.now())
        filename = sanitize_filename(f"phone_{phone_number}_{timestamp}")
        
        # إنشاء التقرير بالتنسيق المطلوب
        if self.report_format == 'json':
            return self._generate_json_report(filename, scan_results)
        elif self.report_format == 'html':
            return self._generate_html_report(filename, 'phone', phone_number, scan_results)
        elif self.report_format == 'markdown':
            return self._generate_markdown_report(filename, 'phone', phone_number, scan_results)
        else:  # text
            return self._generate_text_report(filename, 'phone', phone_number, scan_results)
    
    def generate_username_report(self, username, scan_results):
        """إنشاء تقرير عن نتائج فحص اسم المستخدم"""
        self.logger.info(f"جاري إنشاء تقرير لاسم المستخدم: {username}")
        
        # إنشاء اسم ملف آمن
        timestamp = format_timestamp(datetime.datetime.now())
        filename = sanitize_filename(f"username_{username}_{timestamp}")
        
        # إنشاء التقرير بالتنسيق المطلوب
        if self.report_format == 'json':
            return self._generate_json_report(filename, scan_results)
        elif self.report_format == 'html':
            return self._generate_html_report(filename, 'username', username, scan_results)
        elif self.report_format == 'markdown':
            return self._generate_markdown_report(filename, 'username', username, scan_results)
        else:  # text
            return self._generate_text_report(filename, 'username', username, scan_results)
    
    def generate_web_report(self, url, scan_results):
        """إنشاء تقرير عن نتائج فحص موقع الويب"""
        self.logger.info(f"جاري إنشاء تقرير لموقع الويب: {url}")
        
        # إنشاء اسم ملف آمن
        timestamp = format_timestamp(datetime.datetime.now())
        filename = sanitize_filename(f"web_{url.replace('://', '_').replace('/', '_')}_{timestamp}")
        
        # إنشاء التقرير بالتنسيق المطلوب
        if self.report_format == 'json':
            return self._generate_json_report(filename, scan_results)
        elif self.report_format == 'html':
            return self._generate_html_report(filename, 'web', url, scan_results)
        elif self.report_format == 'markdown':
            return self._generate_markdown_report(filename, 'web', url, scan_results)
        else:  # text
            return self._generate_text_report(filename, 'web', url, scan_results)
    
    def _generate_json_report(self, filename, scan_results):
        """إنشاء تقرير بتنسيق JSON"""
        try:
            # إضافة معلومات التقرير
            report_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'tool': 'JawaL',
                'version': '1.0.0',
                'results': scan_results
            }
            
            # كتابة التقرير إلى ملف
            output_file = os.path.join(self.output_dir, f"{filename}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"تم إنشاء تقرير JSON: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير JSON: {str(e)}")
            return None
    
    def _generate_text_report(self, filename, target_type, target, scan_results):
        """إنشاء تقرير بتنسيق نصي"""
        try:
            # إنشاء محتوى التقرير
            report_content = []
            report_content.append("="*50)
            report_content.append("تقرير فحص JawaL")
            report_content.append("="*50)
            report_content.append(f"التاريخ والوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if target_type == 'phone':
                report_content.append(f"رقم الهاتف: {target}")
                
                # معلومات الهاتف
                if 'phone_info' in scan_results:
                    report_content.append("\nمعلومات الهاتف:")
                    report_content.append("-"*30)
                    for key, value in scan_results['phone_info'].items():
                        report_content.append(f"{key}: {value}")
                
                # معلومات مزود الخدمة
                if 'provider_info' in scan_results:
                    report_content.append("\nمعلومات مزود الخدمة:")
                    report_content.append("-"*30)
                    for key, value in scan_results['provider_info'].items():
                        report_content.append(f"{key}: {value}")
                
                # حسابات وسائل التواصل الاجتماعي
                if 'social_accounts' in scan_results and scan_results['social_accounts']:
                    report_content.append("\nحسابات وسائل التواصل الاجتماعي:")
                    report_content.append("-"*30)
                    for account in scan_results['social_accounts']:
                        report_content.append(f"المنصة: {account['platform']}")
                        report_content.append(f"اسم المستخدم: {account['username']}")
                        report_content.append(f"الرابط: {account['url']}")
                        report_content.append("-"*20)
                
                # حسابات البريد الإلكتروني
                if 'email_accounts' in scan_results and scan_results['email_accounts']:
                    report_content.append("\nحسابات البريد الإلكتروني:")
                    report_content.append("-"*30)
                    for email in scan_results['email_accounts']:
                        report_content.append(f"البريد الإلكتروني: {email}")
                
                # تسريبات البيانات
                if 'data_leaks' in scan_results and scan_results['data_leaks']:
                    report_content.append("\nتسريبات البيانات:")
                    report_content.append("-"*30)
                    for leak in scan_results['data_leaks']:
                        report_content.append(f"المصدر: {leak['source']}")
                        report_content.append(f"التاريخ: {leak['date']}")
                        report_content.append(f"نوع البيانات: {leak['data_type']}")
                        report_content.append("-"*20)
            
            elif target_type == 'username':
                report_content.append(f"اسم المستخدم: {target}")
                
                # حسابات وسائل التواصل الاجتماعي
                if 'social_accounts' in scan_results and scan_results['social_accounts']:
                    report_content.append("\nحسابات وسائل التواصل الاجتماعي:")
                    report_content.append("-"*30)
                    for platform, accounts in scan_results['social_accounts'].items():
                        for account in accounts:
                            report_content.append(f"المنصة: {platform}")
                            if 'url' in account:
                                report_content.append(f"الرابط: {account['url']}")
                            if 'found' in account:
                                report_content.append(f"تم العثور: {account['found']}")
                            report_content.append("-"*20)
                
                # حسابات البريد الإلكتروني
                if 'email_accounts' in scan_results and scan_results['email_accounts']:
                    report_content.append("\nحسابات البريد الإلكتروني:")
                    report_content.append("-"*30)
                    for email in scan_results['email_accounts']:
                        report_content.append(f"البريد الإلكتروني: {email}")
                
                # نتائج البحث العميق
                if 'deep_search' in scan_results and scan_results['deep_search']:
                    report_content.append("\nنتائج البحث العميق:")
                    report_content.append("-"*30)
                    for result in scan_results['deep_search']:
                        report_content.append(f"المصدر: {result['source']}")
                        report_content.append(f"الرابط: {result['url']}")
                        report_content.append(f"الوصف: {result['description']}")
                        report_content.append("-"*20)
            
            elif target_type == 'web':
                report_content.append(f"عنوان URL: {target}")
                
                # معلومات الموقع
                if 'site_info' in scan_results:
                    report_content.append("\nمعلومات الموقع:")
                    report_content.append("-"*30)
                    for key, value in scan_results['site_info'].items():
                        if isinstance(value, dict):
                            report_content.append(f"{key}:")
                            for subkey, subvalue in value.items():
                                report_content.append(f"  {subkey}: {subvalue}")
                        else:
                            report_content.append(f"{key}: {value}")
                
                # التقنيات المستخدمة
                if 'technologies' in scan_results and scan_results['technologies']:
                    report_content.append("\nالتقنيات المستخدمة:")
                    report_content.append("-"*30)
                    for tech in scan_results['technologies']:
                        report_content.append(f"الاسم: {tech['name']}")
                        report_content.append(f"الإصدار: {tech['version']}")
                        report_content.append(f"الثقة: {tech['confidence']}")
                        report_content.append("-"*20)
                
                # الثغرات الأمنية
                if 'vulnerabilities' in scan_results and scan_results['vulnerabilities']:
                    report_content.append("\nالثغرات الأمنية:")
                    report_content.append("-"*30)
                    for vuln in scan_results['vulnerabilities']:
                        report_content.append(f"الاسم: {vuln['name']}")
                        report_content.append(f"الخطورة: {vuln['severity']}")
                        report_content.append(f"الوصف: {vuln['description']}")
                        if 'evidence' in vuln:
                            report_content.append(f"الدليل: {vuln['evidence']}")
                        report_content.append("-"*20)
                
                # المنافذ المفتوحة
                if 'open_ports' in scan_results and scan_results['open_ports']:
                    report_content.append("\nالمنافذ المفتوحة:")
                    report_content.append("-"*30)
                    for port in scan_results['open_ports']:
                        report_content.append(f"المنفذ: {port['port']}")
                        report_content.append(f"الحالة: {port['state']}")
                        report_content.append(f"الخدمة: {port['service']}")
                        report_content.append("-"*20)
                
                # معلومات ووردبريس
                if 'wordpress_info' in scan_results:
                    report_content.append("\nمعلومات ووردبريس:")
                    report_content.append("-"*30)
                    for key, value in scan_results['wordpress_info'].items():
                        if isinstance(value, list):
                            report_content.append(f"{key}:")
                            for item in value:
                                if isinstance(item, dict):
                                    for subkey, subvalue in item.items():
                                        report_content.append(f"  {subkey}: {subvalue}")
                                    report_content.append("  " + "-"*10)
                                else:
                                    report_content.append(f"  {item}")
                        elif isinstance(value, dict):
                            report_content.append(f"{key}:")
                            for subkey, subvalue in value.items():
                                report_content.append(f"  {subkey}: {subvalue}")
                        else:
                            report_content.append(f"{key}: {value}")
                
                # معلومات جوملا
                if 'joomla_info' in scan_results:
                    report_content.append("\nمعلومات جوملا:")
                    report_content.append("-"*30)
                    for key, value in scan_results['joomla_info'].items():
                        if isinstance(value, list):
                            report_content.append(f"{key}:")
                            for item in value:
                                if isinstance(item, dict):
                                    for subkey, subvalue in item.items():
                                        report_content.append(f"  {subkey}: {subvalue}")
                                    report_content.append("  " + "-"*10)
                                else:
                                    report_content.append(f"  {item}")
                        elif isinstance(value, dict):
                            report_content.append(f"{key}:")
                            for subkey, subvalue in value.items():
                                report_content.append(f"  {subkey}: {subvalue}")
                        else:
                            report_content.append(f"{key}: {value}")
            
            # إضافة معلومات الأداة
            report_content.append("\n" + "="*50)
            report_content.append("تم إنشاء هذا التقرير بواسطة أداة JawaL")
            report_content.append("المطور: Saudi Linux")
            report_content.append("البريد الإلكتروني: SaudiLinux7@gmail.com")
            report_content.append("="*50)
            
            # كتابة التقرير إلى ملف
            output_file = os.path.join(self.output_dir, f"{filename}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_content))
            
            self.logger.info(f"تم إنشاء تقرير نصي: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير نصي: {str(e)}")
            return None
    
    def _generate_html_report(self, filename, target_type, target, scan_results):
        """إنشاء تقرير بتنسيق HTML"""
        try:
            # قالب HTML
            html_template = '''
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>تقرير فحص JawaL</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 20px;
                        color: #333;
                        direction: rtl;
                    }
                    h1, h2, h3 {
                        color: #2c3e50;
                    }
                    .container {
                        max-width: 1000px;
                        margin: 0 auto;
                        background: #fff;
                        padding: 20px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                    .header {
                        background: #3498db;
                        color: #fff;
                        padding: 10px 20px;
                        margin-bottom: 20px;
                        border-radius: 5px;
                    }
                    .section {
                        margin-bottom: 20px;
                        padding: 15px;
                        background: #f9f9f9;
                        border-radius: 5px;
                    }
                    .item {
                        margin-bottom: 10px;
                        padding: 10px;
                        background: #fff;
                        border-left: 3px solid #3498db;
                    }
                    .footer {
                        text-align: center;
                        margin-top: 20px;
                        padding: 10px;
                        background: #2c3e50;
                        color: #fff;
                        border-radius: 5px;
                    }
                    .severity-high {
                        border-left: 3px solid #e74c3c;
                    }
                    .severity-medium {
                        border-left: 3px solid #f39c12;
                    }
                    .severity-low {
                        border-left: 3px solid #2ecc71;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 10px;
                    }
                    th, td {
                        padding: 8px;
                        text-align: right;
                        border-bottom: 1px solid #ddd;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>تقرير فحص JawaL</h1>
                        <p>التاريخ والوقت: {{ timestamp }}</p>
                    </div>
                    
                    <div class="section">
                        <h2>معلومات الهدف</h2>
                        {% if target_type == 'phone' %}
                            <p><strong>رقم الهاتف:</strong> {{ target }}</p>
                        {% elif target_type == 'username' %}
                            <p><strong>اسم المستخدم:</strong> {{ target }}</p>
                        {% elif target_type == 'web' %}
                            <p><strong>عنوان URL:</strong> {{ target }}</p>
                        {% endif %}
                    </div>
                    
                    {% if target_type == 'phone' %}
                        {% if results.phone_info %}
                            <div class="section">
                                <h2>معلومات الهاتف</h2>
                                <table>
                                    {% for key, value in results.phone_info.items() %}
                                        <tr>
                                            <th>{{ key }}</th>
                                            <td>{{ value }}</td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            </div>
                        {% endif %}
                        
                        {% if results.provider_info %}
                            <div class="section">
                                <h2>معلومات مزود الخدمة</h2>
                                <table>
                                    {% for key, value in results.provider_info.items() %}
                                        <tr>
                                            <th>{{ key }}</th>
                                            <td>{{ value }}</td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            </div>
                        {% endif %}
                        
                        {% if results.social_accounts %}
                            <div class="section">
                                <h2>حسابات وسائل التواصل الاجتماعي</h2>
                                {% for account in results.social_accounts %}
                                    <div class="item">
                                        <p><strong>المنصة:</strong> {{ account.platform }}</p>
                                        <p><strong>اسم المستخدم:</strong> {{ account.username }}</p>
                                        <p><strong>الرابط:</strong> <a href="{{ account.url }}" target="_blank">{{ account.url }}</a></p>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.email_accounts %}
                            <div class="section">
                                <h2>حسابات البريد الإلكتروني</h2>
                                <ul>
                                    {% for email in results.email_accounts %}
                                        <li>{{ email }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}
                        
                        {% if results.data_leaks %}
                            <div class="section">
                                <h2>تسريبات البيانات</h2>
                                {% for leak in results.data_leaks %}
                                    <div class="item">
                                        <p><strong>المصدر:</strong> {{ leak.source }}</p>
                                        <p><strong>التاريخ:</strong> {{ leak.date }}</p>
                                        <p><strong>نوع البيانات:</strong> {{ leak.data_type }}</p>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                    
                    {% elif target_type == 'username' %}
                        {% if results.social_accounts %}
                            <div class="section">
                                <h2>حسابات وسائل التواصل الاجتماعي</h2>
                                {% for platform, accounts in results.social_accounts.items() %}
                                    {% for account in accounts %}
                                        <div class="item">
                                            <p><strong>المنصة:</strong> {{ platform }}</p>
                                            {% if account.url %}
                                                <p><strong>الرابط:</strong> <a href="{{ account.url }}" target="_blank">{{ account.url }}</a></p>
                                            {% endif %}
                                            {% if account.found %}
                                                <p><strong>تم العثور:</strong> {{ account.found }}</p>
                                            {% endif %}
                                        </div>
                                    {% endfor %}
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.email_accounts %}
                            <div class="section">
                                <h2>حسابات البريد الإلكتروني</h2>
                                <ul>
                                    {% for email in results.email_accounts %}
                                        <li>{{ email }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        {% endif %}
                        
                        {% if results.deep_search %}
                            <div class="section">
                                <h2>نتائج البحث العميق</h2>
                                {% for result in results.deep_search %}
                                    <div class="item">
                                        <p><strong>المصدر:</strong> {{ result.source }}</p>
                                        <p><strong>الرابط:</strong> <a href="{{ result.url }}" target="_blank">{{ result.url }}</a></p>
                                        <p><strong>الوصف:</strong> {{ result.description }}</p>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                    
                    {% elif target_type == 'web' %}
                        {% if results.site_info %}
                            <div class="section">
                                <h2>معلومات الموقع</h2>
                                <table>
                                    {% for key, value in results.site_info.items() %}
                                        <tr>
                                            <th>{{ key }}</th>
                                            <td>
                                                {% if value is mapping %}
                                                    <table>
                                                        {% for subkey, subvalue in value.items() %}
                                                            <tr>
                                                                <th>{{ subkey }}</th>
                                                                <td>{{ subvalue }}</td>
                                                            </tr>
                                                        {% endfor %}
                                                    </table>
                                                {% else %}
                                                    {{ value }}
                                                {% endif %}
                                            </td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            </div>
                        {% endif %}
                        
                        {% if results.technologies %}
                            <div class="section">
                                <h2>التقنيات المستخدمة</h2>
                                {% for tech in results.technologies %}
                                    <div class="item">
                                        <p><strong>الاسم:</strong> {{ tech.name }}</p>
                                        <p><strong>الإصدار:</strong> {{ tech.version }}</p>
                                        <p><strong>الثقة:</strong> {{ tech.confidence }}</p>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.vulnerabilities %}
                            <div class="section">
                                <h2>الثغرات الأمنية</h2>
                                {% for vuln in results.vulnerabilities %}
                                    <div class="item {% if vuln.severity == 'عالية' %}severity-high{% elif vuln.severity == 'متوسطة' %}severity-medium{% else %}severity-low{% endif %}">
                                        <p><strong>الاسم:</strong> {{ vuln.name }}</p>
                                        <p><strong>الخطورة:</strong> {{ vuln.severity }}</p>
                                        <p><strong>الوصف:</strong> {{ vuln.description }}</p>
                                        {% if vuln.evidence %}
                                            <p><strong>الدليل:</strong> {{ vuln.evidence }}</p>
                                        {% endif %}
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.open_ports %}
                            <div class="section">
                                <h2>المنافذ المفتوحة</h2>
                                {% for port in results.open_ports %}
                                    <div class="item">
                                        <p><strong>المنفذ:</strong> {{ port.port }}</p>
                                        <p><strong>الحالة:</strong> {{ port.state }}</p>
                                        <p><strong>الخدمة:</strong> {{ port.service }}</p>
                                    </div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.wordpress_info %}
                            <div class="section">
                                <h2>معلومات ووردبريس</h2>
                                {% for key, value in results.wordpress_info.items() %}
                                    {% if value is iterable and value is not string %}
                                        <h3>{{ key }}</h3>
                                        {% for item in value %}
                                            <div class="item">
                                                {% if item is mapping %}
                                                    {% for subkey, subvalue in item.items() %}
                                                        <p><strong>{{ subkey }}:</strong> {{ subvalue }}</p>
                                                    {% endfor %}
                                                {% else %}
                                                    <p>{{ item }}</p>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    {% elif value is mapping %}
                                        <h3>{{ key }}</h3>
                                        <div class="item">
                                            {% for subkey, subvalue in value.items() %}
                                                <p><strong>{{ subkey }}:</strong> {{ subvalue }}</p>
                                            {% endfor %}
                                        </div>
                                    {% else %}
                                        <p><strong>{{ key }}:</strong> {{ value }}</p>
                                    {% endif %}
                                {% endfor %}
                            </div>
                        {% endif %}
                        
                        {% if results.joomla_info %}
                            <div class="section">
                                <h2>معلومات جوملا</h2>
                                {% for key, value in results.joomla_info.items() %}
                                    {% if value is iterable and value is not string %}
                                        <h3>{{ key }}</h3>
                                        {% for item in value %}
                                            <div class="item">
                                                {% if item is mapping %}
                                                    {% for subkey, subvalue in item.items() %}
                                                        <p><strong>{{ subkey }}:</strong> {{ subvalue }}</p>
                                                    {% endfor %}
                                                {% else %}
                                                    <p>{{ item }}</p>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    {% elif value is mapping %}
                                        <h3>{{ key }}</h3>
                                        <div class="item">
                                            {% for subkey, subvalue in value.items() %}
                                                <p><strong>{{ subkey }}:</strong> {{ subvalue }}</p>
                                            {% endfor %}
                                        </div>
                                    {% else %}
                                        <p><strong>{{ key }}:</strong> {{ value }}</p>
                                    {% endif %}
                                {% endfor %}
                            </div>
                        {% endif %}
                    {% endif %}
                    
                    <div class="footer">
                        <p>تم إنشاء هذا التقرير بواسطة أداة JawaL</p>
                        <p>المطور: Saudi Linux</p>
                        <p>البريد الإلكتروني: SaudiLinux7@gmail.com</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            # إنشاء قالب Jinja2
            template = Template(html_template)
            
            # تحضير البيانات للقالب
            template_data = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'target_type': target_type,
                'target': target,
                'results': scan_results
            }
            
            # توليد محتوى HTML
            html_content = template.render(**template_data)
            
            # كتابة التقرير إلى ملف
            output_file = os.path.join(self.output_dir, f"{filename}.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"تم إنشاء تقرير HTML: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير HTML: {str(e)}")
            return None
    
    def _generate_markdown_report(self, filename, target_type, target, scan_results):
        """إنشاء تقرير بتنسيق Markdown"""
        try:
            # إنشاء محتوى التقرير
            report_content = []
            report_content.append("# تقرير فحص JawaL")
            report_content.append(f"**التاريخ والوقت:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if target_type == 'phone':
                report_content.append(f"**رقم الهاتف:** {target}")
                
                # معلومات الهاتف
                if 'phone_info' in scan_results:
                    report_content.append("\n## معلومات الهاتف")
                    for key, value in scan_results['phone_info'].items():
                        report_content.append(f"**{key}:** {value}")
                
                # معلومات مزود الخدمة
                if 'provider_info' in scan_results:
                    report_content.append("\n## معلومات مزود الخدمة")
                    for key, value in scan_results['provider_info'].items():
                        report_content.append(f"**{key}:** {value}")
                
                # حسابات وسائل التواصل الاجتماعي
                if 'social_accounts' in scan_results and scan_results['social_accounts']:
                    report_content.append("\n## حسابات وسائل التواصل الاجتماعي")
                    for account in scan_results['social_accounts']:
                        report_content.append(f"### {account['platform']}")
                        report_content.append(f"**اسم المستخدم:** {account['username']}")
                        report_content.append(f"**الرابط:** [{account['url']}]({account['url']})")
                
                # حسابات البريد الإلكتروني
                if 'email_accounts' in scan_results and scan_results['email_accounts']:
                    report_content.append("\n## حسابات البريد الإلكتروني")
                    for email in scan_results['email_accounts']:
                        report_content.append(f"- {email}")
                
                # تسريبات البيانات
                if 'data_leaks' in scan_results and scan_results['data_leaks']:
                    report_content.append("\n## تسريبات البيانات")
                    for leak in scan_results['data_leaks']:
                        report_content.append(f"### {leak['source']}")
                        report_content.append(f"**التاريخ:** {leak['date']}")
                        report_content.append(f"**نوع البيانات:** {leak['data_type']}")
            
            elif target_type == 'username':
                report_content.append(f"**اسم المستخدم:** {target}")
                
                # حسابات وسائل التواصل الاجتماعي
                if 'social_accounts' in scan_results and scan_results['social_accounts']:
                    report_content.append("\n## حسابات وسائل التواصل الاجتماعي")
                    for platform, accounts in scan_results['social_accounts'].items():
                        report_content.append(f"### {platform}")
                        for account in accounts:
                            if 'url' in account:
                                report_content.append(f"**الرابط:** [{account['url']}]({account['url']})")
                            if 'found' in account:
                                report_content.append(f"**تم العثور:** {account['found']}")
                
                # حسابات البريد الإلكتروني
                if 'email_accounts' in scan_results and scan_results['email_accounts']:
                    report_content.append("\n## حسابات البريد الإلكتروني")
                    for email in scan_results['email_accounts']:
                        report_content.append(f"- {email}")
                
                # نتائج البحث العميق
                if 'deep_search' in scan_results and scan_results['deep_search']:
                    report_content.append("\n## نتائج البحث العميق")
                    for result in scan_results['deep_search']:
                        report_content.append(f"### {result['source']}")
                        report_content.append(f"**الرابط:** [{result['url']}]({result['url']})")
                        report_content.append(f"**الوصف:** {result['description']}")
            
            elif target_type == 'web':
                report_content.append(f"**عنوان URL:** {target}")
                
                # معلومات الموقع
                if 'site_info' in scan_results:
                    report_content.append("\n## معلومات الموقع")
                    for key, value in scan_results['site_info'].items():
                        if isinstance(value, dict):
                            report_content.append(f"### {key}")
                            for subkey, subvalue in value.items():
                                report_content.append(f"**{subkey}:** {subvalue}")
                        else:
                            report_content.append(f"**{key}:** {value}")
                
                # التقنيات المستخدمة
                if 'technologies' in scan_results and scan_results['technologies']:
                    report_content.append("\n## التقنيات المستخدمة")
                    for tech in scan_results['technologies']:
                        report_content.append(f"### {tech['name']}")
                        report_content.append(f"**الإصدار:** {tech['version']}")
                        report_content.append(f"**الثقة:** {tech['confidence']}")
                
                # الثغرات الأمنية
                if 'vulnerabilities' in scan_results and scan_results['vulnerabilities']:
                    report_content.append("\n## الثغرات الأمنية")
                    for vuln in scan_results['vulnerabilities']:
                        report_content.append(f"### {vuln['name']}")
                        report_content.append(f"**الخطورة:** {vuln['severity']}")
                        report_content.append(f"**الوصف:** {vuln['description']}")
                        if 'evidence' in vuln:
                            report_content.append(f"**الدليل:** {vuln['evidence']}")
                
                # المنافذ المفتوحة
                if 'open_ports' in scan_results and scan_results['open_ports']:
                    report_content.append("\n## المنافذ المفتوحة")
                    for port in scan_results['open_ports']:
                        report_content.append(f"### المنفذ {port['port']}")
                        report_content.append(f"**الحالة:** {port['state']}")
                        report_content.append(f"**الخدمة:** {port['service']}")
                
                # معلومات ووردبريس
                if 'wordpress_info' in scan_results:
                    report_content.append("\n## معلومات ووردبريس")
                    for key, value in scan_results['wordpress_info'].items():
                        if isinstance(value, list):
                            report_content.append(f"### {key}")
                            for item in value:
                                if isinstance(item, dict):
                                    for subkey, subvalue in item.items():
                                        report_content.append(f"**{subkey}:** {subvalue}")
                                    report_content.append("---")
                                else:
                                    report_content.append(f"- {item}")
                        elif isinstance(value, dict):
                            report_content.append(f"### {key}")
                            for subkey, subvalue in value.items():
                                report_content.append(f"**{subkey}:** {subvalue}")
                        else:
                            report_content.append(f"**{key}:** {value}")
                
                # معلومات جوملا
                if 'joomla_info' in scan_results:
                    report_content.append("\n## معلومات جوملا")
                    for key, value in scan_results['joomla_info'].items():
                        if isinstance(value, list):
                            report_content.append(f"### {key}")
                            for item in value:
                                if isinstance(item, dict):
                                    for subkey, subvalue in item.items():
                                        report_content.append(f"**{subkey}:** {subvalue}")
                                    report_content.append("---")
                                else:
                                    report_content.append(f"- {item}")
                        elif isinstance(value, dict):
                            report_content.append(f"### {key}")
                            for subkey, subvalue in value.items():
                                report_content.append(f"**{subkey}:** {subvalue}")
                        else:
                            report_content.append(f"**{key}:** {value}")
            
            # إضافة معلومات الأداة
            report_content.append("\n---")
            report_content.append("*تم إنشاء هذا التقرير بواسطة أداة JawaL*")
            report_content.append("*المطور: Saudi Linux*")
            report_content.append("*البريد الإلكتروني: SaudiLinux7@gmail.com*")
            
            # كتابة التقرير إلى ملف
            output_file = os.path.join(self.output_dir, f"{filename}.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_content))
            
            self.logger.info(f"تم إنشاء تقرير Markdown: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء تقرير Markdown: {str(e)}")
            return None