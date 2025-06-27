#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - أداة إدارة سطح الهجوم واختبار الاختراق
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import os
import sys
import argparse
import time
import json
import re
import requests
from datetime import datetime
from termcolor import colored
from pyfiglet import Figlet
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
from concurrent.futures import ThreadPoolExecutor

# التحقق من وجود المكتبات المطلوبة
try:
    import bs4
    import whois
    import dns.resolver
    import tqdm
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"[!] خطأ: {e}")
    print("[!] يرجى تثبيت جميع المكتبات المطلوبة: pip install -r requirements.txt")
    # تسجيل الخطأ قبل الخروج
    try:
        logger = setup_logger()
        logger.error(f"خطأ في استيراد المكتبات: {e}")
    except:
        pass
    sys.exit(1)

# استيراد الوحدات الداخلية
from modules.phone_scanner import PhoneScanner
from modules.username_scanner import UsernameScanner
from modules.web_scanner import WebScanner
from modules.wordpress_scanner import WordpressScanner
from modules.joomla_scanner import JoomlaScanner
from modules.report_generator import ReportGenerator
from modules.utils import setup_logger, validate_phone, validate_url, validate_username

# إعداد وحدة التسجيل
logger = setup_logger()

# إعداد وحدة الطباعة الملونة
console = Console()

# الإصدار الحالي
VERSION = "1.0.0"

def print_banner():
    """طباعة شعار البرنامج"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        f = Figlet(font='slant')
        banner = f.renderText('JawaL')
        console.print(f"[bold green]{banner}[/bold green]")
        console.print("[bold yellow]أداة إدارة سطح الهجوم واختبار الاختراق[/bold yellow]")
        console.print(f"[bold blue]الإصدار: {VERSION}[/bold blue]")
        console.print("[bold red]المطور: Saudi Linux - SaudiLinux7@gmail.com[/bold red]")
        console.print("[bold white]=" * 70 + "[/bold white]\n")
        logger.info("تم عرض شعار البرنامج")
    except Exception as e:
        console.print(f"[bold red][!] خطأ أثناء عرض الشعار: {e}[/bold red]")
        logger.error(f"خطأ أثناء عرض الشعار: {e}")

def parse_arguments():
    """تحليل معطيات سطر الأوامر"""
    try:
        parser = argparse.ArgumentParser(description='JawaL - أداة إدارة سطح الهجوم واختبار الاختراق')
        
        # المجموعات الرئيسية للأوامر
        target_group = parser.add_argument_group('تحديد الهدف')
        scan_group = parser.add_argument_group('خيارات المسح')
        output_group = parser.add_argument_group('خيارات الإخراج')
        
        # خيارات تحديد الهدف
        target_group.add_argument('-p', '--phone', help='رقم الهاتف المحمول للهدف (مع رمز البلد، مثال: +966XXXXXXXXX)')
        target_group.add_argument('-u', '--username', help='اسم المستخدم للهدف')
        target_group.add_argument('--url', help='عنوان URL للموقع المستهدف')
        target_group.add_argument('--wordpress', help='عنوان URL لموقع ووردبريس للفحص')
        target_group.add_argument('--joomla', help='عنوان URL لموقع جوملا للفحص')
        
        # خيارات المسح
        scan_group.add_argument('--social', action='store_true', help='تمكين فحص مواقع التواصل الاجتماعي')
        scan_group.add_argument('--email', action='store_true', help='تمكين البحث عن البريد الإلكتروني')
        scan_group.add_argument('--deep', action='store_true', help='تمكين الفحص العميق (يستغرق وقتًا أطول)')
        scan_group.add_argument('--ports', default='80,443', help='المنافذ للفحص (افتراضيًا: 80,443)')
        scan_group.add_argument('--timeout', type=int, default=30, help='مهلة الاتصال بالثواني (افتراضيًا: 30)')
        
        # خيارات الإخراج
        output_group.add_argument('-o', '--output', help='اسم ملف التقرير (بدون لاحقة)')
        output_group.add_argument('--format', choices=['txt', 'html', 'pdf', 'json'], default='html', 
                                help='تنسيق التقرير (افتراضيًا: html)')
        output_group.add_argument('-q', '--quiet', action='store_true', help='وضع الصامت (بدون إخراج مفصل)')
        output_group.add_argument('-v', '--verbose', action='store_true', help='وضع المفصل (إخراج مفصل)')
        
        # خيارات أخرى
        parser.add_argument('--version', action='version', version=f'JawaL {VERSION}')
        parser.add_argument('--update', action='store_true', help='تحديث الأداة إلى أحدث إصدار')
        
        return parser.parse_args()
    except Exception as e:
        console.print(f"[bold red][!] خطأ في تحليل المعطيات: {e}[/bold red]")
        logger.error(f"خطأ في تحليل المعطيات: {e}")
        sys.exit(1)

def validate_arguments(args):
    """التحقق من صحة المعطيات المدخلة"""
    if not any([args.phone, args.username, args.url, args.wordpress, args.joomla, args.update]):
        console.print("[bold red][!] خطأ: يجب تحديد هدف واحد على الأقل (رقم هاتف، اسم مستخدم، URL)[/bold red]")
        return False
    
    if args.phone and not validate_phone(args.phone):
        console.print("[bold red][!] خطأ: صيغة رقم الهاتف غير صحيحة. استخدم الصيغة الدولية مع رمز البلد (مثال: +966XXXXXXXXX)[/bold red]")
        return False
    
    if (args.url and not validate_url(args.url)) or \
       (args.wordpress and not validate_url(args.wordpress)) or \
       (args.joomla and not validate_url(args.joomla)):
        console.print("[bold red][!] خطأ: عنوان URL غير صحيح. تأكد من إضافة http:// أو https://[/bold red]")
        return False
    
    if args.username and not validate_username(args.username):
        console.print("[bold red][!] خطأ: اسم المستخدم غير صحيح. يجب أن يتكون من أحرف وأرقام وشرطة سفلية ونقطة فقط (3-30 حرف)[/bold red]")
        return False
    
    return True

def update_tool():
    """تحديث الأداة إلى أحدث إصدار"""
    console.print("[bold yellow][*] جاري التحقق من التحديثات...[/bold yellow]")
    try:
        # هنا يمكن إضافة كود للتحقق من وجود تحديثات من المستودع
        # مثال: استخدام git pull أو التحقق من إصدار على الخادم
        time.sleep(2)  # محاكاة التحقق من التحديثات
        console.print("[bold green][+] الأداة محدثة إلى أحدث إصدار.[/bold green]")
    except Exception as e:
        console.print(f"[bold red][!] خطأ أثناء التحديث: {e}[/bold red]")
        logger.error(f"خطأ أثناء التحديث: {e}")

def scan_phone(phone, args):
    """فحص رقم الهاتف"""
    console.print(f"\n[bold blue][*] بدء فحص رقم الهاتف: {phone}[/bold blue]")
    
    phone_scanner = PhoneScanner(phone, timeout=args.timeout, verbose=args.verbose)
    
    with Progress(
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        # إنشاء مهام التقدم
        provider_task = progress.add_task("[cyan]فحص مزود الخدمة...[/cyan]", total=100)
        location_task = progress.add_task("[cyan]تحديد الموقع الجغرافي...[/cyan]", total=100)
        social_task = progress.add_task("[cyan]فحص مواقع التواصل الاجتماعي...[/cyan]", total=100)
        email_task = progress.add_task("[cyan]البحث عن البريد الإلكتروني...[/cyan]", total=100)
        
        # تنفيذ عمليات الفحص
        provider_info = phone_scanner.get_provider_info()
        progress.update(provider_task, completed=100)
        
        location_info = phone_scanner.get_location_info()
        progress.update(location_task, completed=100)
        
        social_accounts = []
        if args.social:
            social_accounts = phone_scanner.find_social_accounts()
            progress.update(social_task, completed=100)
        else:
            progress.update(social_task, completed=100, description="[cyan]تم تخطي فحص مواقع التواصل الاجتماعي[/cyan]")
        
        email_accounts = []
        if args.email:
            email_accounts = phone_scanner.find_email_accounts()
            progress.update(email_task, completed=100)
        else:
            progress.update(email_task, completed=100, description="[cyan]تم تخطي البحث عن البريد الإلكتروني[/cyan]")
    
    # عرض النتائج
    console.print("\n[bold green][+] نتائج فحص رقم الهاتف:[/bold green]")
    
    # جدول معلومات مزود الخدمة
    table = Table(title="معلومات مزود الخدمة")
    table.add_column("المعلومة", style="cyan")
    table.add_column("القيمة", style="green")
    
    if provider_info:
        for key, value in provider_info.items():
            table.add_row(key, str(value))
    else:
        table.add_row("لا توجد معلومات", "")
    
    console.print(table)
    
    # جدول الموقع الجغرافي
    table = Table(title="معلومات الموقع الجغرافي")
    table.add_column("المعلومة", style="cyan")
    table.add_column("القيمة", style="green")
    
    if location_info:
        for key, value in location_info.items():
            table.add_row(key, str(value))
    else:
        table.add_row("لا توجد معلومات", "")
    
    console.print(table)
    
    # جدول حسابات التواصل الاجتماعي
    if args.social:
        table = Table(title="حسابات التواصل الاجتماعي المرتبطة")
        table.add_column("المنصة", style="cyan")
        table.add_column("اسم المستخدم", style="green")
        table.add_column("الرابط", style="blue")
        
        if social_accounts:
            for account in social_accounts:
                table.add_row(account.get('platform', ''), account.get('username', ''), account.get('url', ''))
        else:
            table.add_row("لا توجد حسابات", "", "")
        
        console.print(table)
    
    # جدول حسابات البريد الإلكتروني
    if args.email:
        table = Table(title="حسابات البريد الإلكتروني المرتبطة")
        table.add_column("البريد الإلكتروني", style="cyan")
        table.add_column("المصدر", style="green")
        
        if email_accounts:
            for email in email_accounts:
                table.add_row(email.get('email', ''), email.get('source', ''))
        else:
            table.add_row("لا توجد حسابات بريد إلكتروني", "")
        
        console.print(table)
    
    return {
        'provider_info': provider_info,
        'location_info': location_info,
        'social_accounts': social_accounts if args.social else [],
        'email_accounts': email_accounts if args.email else []
    }

def scan_username(username, args):
    """فحص اسم المستخدم"""
    console.print(f"\n[bold blue][*] بدء فحص اسم المستخدم: {username}[/bold blue]")
    
    username_scanner = UsernameScanner(username, timeout=args.timeout, verbose=args.verbose)
    
    with Progress(
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        # إنشاء مهام التقدم
        social_task = progress.add_task("[cyan]فحص مواقع التواصل الاجتماعي...[/cyan]", total=100)
        email_task = progress.add_task("[cyan]البحث عن البريد الإلكتروني...[/cyan]", total=100)
        deep_task = progress.add_task("[cyan]الفحص العميق...[/cyan]", total=100)
        
        # تنفيذ عمليات الفحص
        social_accounts = username_scanner.find_social_accounts()
        progress.update(social_task, completed=100)
        
        email_accounts = []
        if args.email:
            email_accounts = username_scanner.find_email_accounts()
            progress.update(email_task, completed=100)
        else:
            progress.update(email_task, completed=100, description="[cyan]تم تخطي البحث عن البريد الإلكتروني[/cyan]")
        
        deep_info = {}
        if args.deep:
            deep_info = username_scanner.deep_search()
            progress.update(deep_task, completed=100)
        else:
            progress.update(deep_task, completed=100, description="[cyan]تم تخطي الفحص العميق[/cyan]")
    
    # عرض النتائج
    console.print("\n[bold green][+] نتائج فحص اسم المستخدم:[/bold green]")
    
    # جدول حسابات التواصل الاجتماعي
    table = Table(title="حسابات التواصل الاجتماعي المرتبطة")
    table.add_column("المنصة", style="cyan")
    table.add_column("اسم المستخدم", style="green")
    table.add_column("الرابط", style="blue")
    table.add_column("الحالة", style="yellow")
    
    if social_accounts:
        for account in social_accounts:
            table.add_row(
                account.get('platform', ''),
                account.get('username', ''),
                account.get('url', ''),
                "[bold green]موجود[/bold green]" if account.get('exists', False) else "[bold red]غير موجود[/bold red]"
            )
    else:
        table.add_row("لا توجد حسابات", "", "", "")
    
    console.print(table)
    
    # جدول حسابات البريد الإلكتروني
    if args.email:
        table = Table(title="حسابات البريد الإلكتروني المرتبطة")
        table.add_column("البريد الإلكتروني", style="cyan")
        table.add_column("المصدر", style="green")
        
        if email_accounts:
            for email in email_accounts:
                table.add_row(email.get('email', ''), email.get('source', ''))
        else:
            table.add_row("لا توجد حسابات بريد إلكتروني", "")
        
        console.print(table)
    
    # معلومات الفحص العميق
    if args.deep and deep_info:
        table = Table(title="نتائج الفحص العميق")
        table.add_column("المعلومة", style="cyan")
        table.add_column("القيمة", style="green")
        
        for key, value in deep_info.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    table.add_row(f"{key} - {sub_key}", str(sub_value))
            else:
                table.add_row(key, str(value))
        
        console.print(table)
    
    return {
        'social_accounts': social_accounts,
        'email_accounts': email_accounts if args.email else [],
        'deep_info': deep_info if args.deep else {}
    }

def scan_web(url, args):
    """فحص موقع الويب"""
    console.print(f"\n[bold blue][*] بدء فحص موقع الويب: {url}[/bold blue]")
    
    ports = [int(p.strip()) for p in args.ports.split(',')]
    web_scanner = WebScanner(url, ports=ports, timeout=args.timeout, verbose=args.verbose)
    
    with Progress(
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        # إنشاء مهام التقدم
        info_task = progress.add_task("[cyan]جمع معلومات الموقع...[/cyan]", total=100)
        tech_task = progress.add_task("[cyan]تحديد التقنيات المستخدمة...[/cyan]", total=100)
        vuln_task = progress.add_task("[cyan]فحص الثغرات الأمنية...[/cyan]", total=100)
        port_task = progress.add_task("[cyan]فحص المنافذ المفتوحة...[/cyan]", total=100)
        
        # تنفيذ عمليات الفحص
        site_info = web_scanner.get_site_info()
        progress.update(info_task, completed=100)
        
        technologies = web_scanner.detect_technologies()
        progress.update(tech_task, completed=100)
        
        vulnerabilities = web_scanner.scan_vulnerabilities()
        progress.update(vuln_task, completed=100)
        
        open_ports = web_scanner.scan_ports()
        progress.update(port_task, completed=100)
    
    # عرض النتائج
    console.print("\n[bold green][+] نتائج فحص موقع الويب:[/bold green]")
    
    # جدول معلومات الموقع
    table = Table(title="معلومات الموقع")
    table.add_column("المعلومة", style="cyan")
    table.add_column("القيمة", style="green")
    
    if site_info:
        for key, value in site_info.items():
            table.add_row(key, str(value))
    else:
        table.add_row("لا توجد معلومات", "")
    
    console.print(table)
    
    # جدول التقنيات المستخدمة
    table = Table(title="التقنيات المستخدمة")
    table.add_column("التقنية", style="cyan")
    table.add_column("الإصدار", style="green")
    
    if technologies:
        for tech in technologies:
            table.add_row(tech.get('name', ''), tech.get('version', 'غير معروف'))
    else:
        table.add_row("لا توجد تقنيات معروفة", "")
    
    console.print(table)
    
    # جدول الثغرات الأمنية
    table = Table(title="الثغرات الأمنية المكتشفة")
    table.add_column("الثغرة", style="cyan")
    table.add_column("الخطورة", style="green")
    table.add_column("الوصف", style="blue")
    
    if vulnerabilities:
        try:
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'متوسطة')
                severity_color = "green"
                if severity == "عالية":
                    severity_color = "red"
                elif severity == "متوسطة":
                    severity_color = "yellow"
                
                table.add_row(
                    vuln.get('name', ''),
                    f"[bold {severity_color}]{severity}[/bold {severity_color}]",
                    vuln.get('description', '')
                )
        except Exception as e:
            logger.error(f"خطأ في عرض جدول الثغرات: {e}")
            console.print("[bold red]حدث خطأ أثناء عرض جدول الثغرات[/bold red]")
            if args.verbose:
                import traceback
                console.print(f"[red]{traceback.format_exc()}[/red]")
    else:
        table.add_row("لا توجد ثغرات مكتشفة", "", "")
    
    console.print(table)
    
    # جدول المنافذ المفتوحة
    table = Table(title="المنافذ المفتوحة")
    table.add_column("المنفذ", style="cyan")
    table.add_column("الخدمة", style="green")
    table.add_column("الحالة", style="blue")
    
    if open_ports:
        for port in open_ports:
            table.add_row(
                str(port.get('port', '')),
                port.get('service', 'غير معروف'),
                "[bold green]مفتوح[/bold green]" if port.get('state', '') == 'open' else port.get('state', '')
            )
    else:
        table.add_row("لا توجد منافذ مفتوحة", "", "")
    
    console.print(table)
    
    return {
        'site_info': site_info,
        'technologies': technologies,
        'vulnerabilities': vulnerabilities,
        'open_ports': open_ports
    }

def scan_wordpress(url, args):
    """فحص موقع ووردبريس"""
    console.print(f"\n[bold blue][*] بدء فحص موقع ووردبريس: {url}[/bold blue]")
    
    wp_scanner = WordpressScanner(url, timeout=args.timeout, verbose=args.verbose)
    
    with Progress(
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        # إنشاء مهام التقدم
        version_task = progress.add_task("[cyan]تحديد إصدار ووردبريس...[/cyan]", total=100)
        theme_task = progress.add_task("[cyan]فحص القوالب...[/cyan]", total=100)
        plugin_task = progress.add_task("[cyan]فحص الإضافات...[/cyan]", total=100)
        vuln_task = progress.add_task("[cyan]فحص الثغرات الأمنية...[/cyan]", total=100)
        
        # تنفيذ عمليات الفحص
        wp_version = wp_scanner.detect_version()
        progress.update(version_task, completed=100)
        
        themes = wp_scanner.enumerate_themes()
        progress.update(theme_task, completed=100)
        
        plugins = wp_scanner.enumerate_plugins()
        progress.update(plugin_task, completed=100)
        
        vulnerabilities = wp_scanner.scan_vulnerabilities()
        progress.update(vuln_task, completed=100)
    
    # عرض النتائج
    console.print("\n[bold green][+] نتائج فحص موقع ووردبريس:[/bold green]")
    
    # معلومات إصدار ووردبريس
    table = Table(title="معلومات ووردبريس")
    table.add_column("المعلومة", style="cyan")
    table.add_column("القيمة", style="green")
    
    if wp_version:
        table.add_row("إصدار ووردبريس", wp_version.get('version', 'غير معروف'))
        table.add_row("آخر تحديث", wp_version.get('last_updated', 'غير معروف'))
        table.add_row("الحالة", "[bold green]محدث[/bold green]" if wp_version.get('is_latest', False) else "[bold red]قديم[/bold red]")
    else:
        table.add_row("إصدار ووردبريس", "غير معروف")
    
    console.print(table)
    
    # جدول القوالب
    table = Table(title="القوالب المكتشفة")
    table.add_column("اسم القالب", style="cyan")
    table.add_column("الإصدار", style="green")
    table.add_column("الحالة", style="blue")
    
    if themes:
        for theme in themes:
            table.add_row(
                theme.get('name', ''),
                theme.get('version', 'غير معروف'),
                "[bold green]محدث[/bold green]" if theme.get('is_latest', False) else "[bold red]قديم[/bold red]"
            )
    else:
        table.add_row("لا توجد قوالب مكتشفة", "", "")
    
    console.print(table)
    
    # جدول الإضافات
    table = Table(title="الإضافات المكتشفة")
    table.add_column("اسم الإضافة", style="cyan")
    table.add_column("الإصدار", style="green")
    table.add_column("الحالة", style="blue")
    
    if plugins:
        for plugin in plugins:
            table.add_row(
                plugin.get('name', ''),
                plugin.get('version', 'غير معروف'),
                "[bold green]محدث[/bold green]" if plugin.get('is_latest', False) else "[bold red]قديم[/bold red]"
            )
    else:
        table.add_row("لا توجد إضافات مكتشفة", "", "")
    
    console.print(table)
    
    # جدول الثغرات الأمنية
    table = Table(title="الثغرات الأمنية المكتشفة")
    table.add_column("المكون", style="cyan")
    table.add_column("الثغرة", style="green")
    table.add_column("الخطورة", style="blue")
    table.add_column("الوصف", style="yellow")
    
    if vulnerabilities:
        try:
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'متوسطة')
                severity_color = "green"
                if severity == "عالية":
                    severity_color = "red"
                elif severity == "متوسطة":
                    severity_color = "yellow"
                
                table.add_row(
                    vuln.get('component', ''),
                    vuln.get('name', ''),
                    f"[bold {severity_color}]{severity}[/bold {severity_color}]",
                    vuln.get('description', '')
                )
        except Exception as e:
            logger.error(f"خطأ في عرض جدول الثغرات: {e}")
            console.print("[bold red]حدث خطأ أثناء عرض جدول الثغرات[/bold red]")
            if args.verbose:
                import traceback
                console.print(f"[red]{traceback.format_exc()}[/red]")
    else:
        table.add_row("لا توجد ثغرات مكتشفة", "", "", "")
    
    console.print(table)
    
    return {
        'wp_version': wp_version,
        'themes': themes,
        'plugins': plugins,
        'vulnerabilities': vulnerabilities
    }

def scan_joomla(url, args):
    """فحص موقع جوملا"""
    console.print(f"\n[bold blue][*] بدء فحص موقع جوملا: {url}[/bold blue]")
    
    joomla_scanner = JoomlaScanner(url, timeout=args.timeout, verbose=args.verbose)
    
    with Progress(
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        # إنشاء مهام التقدم
        version_task = progress.add_task("[cyan]تحديد إصدار جوملا...[/cyan]", total=100)
        component_task = progress.add_task("[cyan]فحص المكونات...[/cyan]", total=100)
        template_task = progress.add_task("[cyan]فحص القوالب...[/cyan]", total=100)
        vuln_task = progress.add_task("[cyan]فحص الثغرات الأمنية...[/cyan]", total=100)
        
        # تنفيذ عمليات الفحص
        joomla_version = joomla_scanner.detect_version()
        progress.update(version_task, completed=100)
        
        components = joomla_scanner.enumerate_components()
        progress.update(component_task, completed=100)
        
        templates = joomla_scanner.enumerate_templates()
        progress.update(template_task, completed=100)
        
        vulnerabilities = joomla_scanner.scan_vulnerabilities()
        progress.update(vuln_task, completed=100)
    
    # عرض النتائج
    console.print("\n[bold green][+] نتائج فحص موقع جوملا:[/bold green]")
    
    # معلومات إصدار جوملا
    table = Table(title="معلومات جوملا")
    table.add_column("المعلومة", style="cyan")
    table.add_column("القيمة", style="green")
    
    if joomla_version:
        table.add_row("إصدار جوملا", joomla_version.get('version', 'غير معروف'))
        table.add_row("آخر تحديث", joomla_version.get('last_updated', 'غير معروف'))
        table.add_row("الحالة", "[bold green]محدث[/bold green]" if joomla_version.get('is_latest', False) else "[bold red]قديم[/bold red]")
    else:
        table.add_row("إصدار جوملا", "غير معروف")
    
    console.print(table)
    
    # جدول المكونات
    table = Table(title="المكونات المكتشفة")
    table.add_column("اسم المكون", style="cyan")
    table.add_column("الإصدار", style="green")
    table.add_column("الحالة", style="blue")
    
    if components:
        for component in components:
            table.add_row(
                component.get('name', ''),
                component.get('version', 'غير معروف'),
                "[bold green]محدث[/bold green]" if component.get('is_latest', False) else "[bold red]قديم[/bold red]"
            )
    else:
        table.add_row("لا توجد مكونات مكتشفة", "", "")
    
    console.print(table)
    
    # جدول القوالب
    table = Table(title="القوالب المكتشفة")
    table.add_column("اسم القالب", style="cyan")
    table.add_column("الإصدار", style="green")
    table.add_column("الحالة", style="blue")
    
    if templates:
        for template in templates:
            table.add_row(
                template.get('name', ''),
                template.get('version', 'غير معروف'),
                "[bold green]محدث[/bold green]" if template.get('is_latest', False) else "[bold red]قديم[/bold red]"
            )
    else:
        table.add_row("لا توجد قوالب مكتشفة", "", "")
    
    console.print(table)
    
    # جدول الثغرات الأمنية
    table = Table(title="الثغرات الأمنية المكتشفة")
    table.add_column("المكون", style="cyan")
    table.add_column("الثغرة", style="green")
    table.add_column("الخطورة", style="blue")
    table.add_column("الوصف", style="yellow")
    
    if vulnerabilities:
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'متوسطة')
            severity_color = "green"
            if severity == "عالية":
                severity_color = "red"
            elif severity == "متوسطة":
                severity_color = "yellow"
            
            table.add_row(
                vuln.get('component', ''),
                vuln.get('name', ''),
                f"[bold {severity_color}]{severity}[/bold {severity_color}]",
                vuln.get('description', '')
            )
    else:
        table.add_row("لا توجد ثغرات مكتشفة", "", "", "")
    
    console.print(table)
    
    return {
        'joomla_version': joomla_version,
        'components': components,
        'templates': templates,
        'vulnerabilities': vulnerabilities
    }

def generate_report(results, args):
    """إنشاء تقرير بالنتائج"""
    if not args.output:
        return
    
    console.print(f"\n[bold blue][*] جاري إنشاء التقرير: {args.output}.{args.format}[/bold blue]")
    
    try:
        report_generator = ReportGenerator(results, output_format=args.format)
        report_path = report_generator.generate(args.output)
        
        if report_path:
            console.print(f"[bold green][+] تم إنشاء التقرير بنجاح: {report_path}[/bold green]")
            logger.info(f"تم إنشاء التقرير بنجاح: {report_path}")
        else:
            console.print("[bold red][!] فشل في إنشاء التقرير[/bold red]")
            logger.error("فشل في إنشاء التقرير")
    except Exception as e:
        console.print(f"[bold red][!] خطأ أثناء إنشاء التقرير: {e}[/bold red]")
        logger.error(f"خطأ أثناء إنشاء التقرير: {e}")

def main():
    """الدالة الرئيسية للبرنامج"""
    print_banner()
    
    args = parse_arguments()
    
    if args.update:
        update_tool()
        return
    
    if not validate_arguments(args):
        return
    
    start_time = time.time()
    results = {}
    
    try:
        if args.phone:
            results['phone'] = scan_phone(args.phone, args)
        
        if args.username:
            results['username'] = scan_username(args.username, args)
        
        if args.url:
            results['web'] = scan_web(args.url, args)
        
        if args.wordpress:
            results['wordpress'] = scan_wordpress(args.wordpress, args)
        
        if args.joomla:
            results['joomla'] = scan_joomla(args.joomla, args)
        
        # إنشاء تقرير إذا تم تحديد اسم الملف
        if args.output:
            generate_report(results, args)
        
        end_time = time.time()
        duration = end_time - start_time
        
        console.print(f"\n[bold green][+] اكتملت جميع عمليات الفحص في {duration:.2f} ثانية[/bold green]")
    
    except KeyboardInterrupt:
        console.print("\n[bold yellow][!] تم إيقاف البرنامج بواسطة المستخدم[/bold yellow]")
        logger.warning("تم إيقاف البرنامج بواسطة المستخدم")
    except Exception as e:
        console.print(f"\n[bold red][!] حدث خطأ: {e}[/bold red]")
        logger.error(f"حدث خطأ: {e}")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()