#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
JawaL - أداة إدارة سطح الهجوم والاستخبارات
المطور: Saudi Linux
البريد الإلكتروني: SaudiLinux7@gmail.com
'''

import os
import sys
import argparse
import logging
import colorama
from pyfiglet import Figlet
from termcolor import colored

from modules import (
    setup_logging,
    validate_phone_number,
    validate_url,
    validate_username,
    PhoneScanner,
    UsernameScanner,
    WebScanner,
    WordpressScanner,
    JoomlaScanner,
    ReportGenerator
)

# تهيئة الألوان
colorama.init(autoreset=True)

def print_banner():
    """طباعة شعار الأداة"""
    fig = Figlet(font='slant')
    banner = fig.renderText('JawaL')
    print(colored(banner, 'green'))
    print(colored('=' * 50, 'green'))
    print(colored('JawaL - أداة إدارة سطح الهجوم والاستخبارات', 'yellow'))
    print(colored('المطور: Saudi Linux', 'yellow'))
    print(colored('البريد الإلكتروني: SaudiLinux7@gmail.com', 'yellow'))
    print(colored('=' * 50, 'green'))
    print()

def parse_arguments():
    """تحليل المعطيات من سطر الأوامر"""
    parser = argparse.ArgumentParser(
        description='JawaL - أداة إدارة سطح الهجوم والاستخبارات',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # إضافة مجموعات المعطيات
    scan_group = parser.add_argument_group('خيارات الفحص')
    output_group = parser.add_argument_group('خيارات الإخراج')
    
    # خيارات الفحص
    scan_group.add_argument('-p', '--phone', metavar='PHONE_NUMBER', help='فحص رقم هاتف')
    scan_group.add_argument('-u', '--username', metavar='USERNAME', help='فحص اسم مستخدم')
    scan_group.add_argument('-w', '--web', metavar='URL', help='فحص موقع ويب')
    scan_group.add_argument('--wordpress', metavar='URL', help='فحص موقع ووردبريس')
    scan_group.add_argument('--joomla', metavar='URL', help='فحص موقع جوملا')
    scan_group.add_argument('--ports', metavar='PORTS', help='تحديد المنافذ للفحص (مثال: 80,443 أو 80-1000)')
    
    # خيارات الإخراج
    output_group.add_argument('-o', '--output-dir', metavar='DIR', help='مجلد حفظ التقارير')
    output_group.add_argument('-f', '--format', choices=['text', 'json', 'html', 'markdown'],
                            default='text', help='تنسيق التقرير (الافتراضي: text)')
    output_group.add_argument('-v', '--verbose', action='store_true', help='عرض معلومات تفصيلية')
    output_group.add_argument('-q', '--quiet', action='store_true', help='عدم عرض معلومات إضافية')
    
    return parser.parse_args()

def main():
    """الدالة الرئيسية للأداة"""
    # طباعة الشعار
    print_banner()
    
    # تحليل المعطيات
    args = parse_arguments()
    
    # إعداد التسجيل
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.quiet:
        log_level = logging.WARNING
    logger = setup_logging(log_level)
    
    # التحقق من وجود معطيات للفحص
    if not any([args.phone, args.username, args.web, args.wordpress, args.joomla]):
        print(colored("خطأ: يجب تحديد نوع الفحص (هاتف، اسم مستخدم، موقع ويب)", 'red'))
        print(colored("استخدم -h أو --help للحصول على المساعدة", 'yellow'))
        sys.exit(1)
    
    # إنشاء مولد التقارير
    report_generator = ReportGenerator(
        output_dir=args.output_dir,
        report_format=args.format,
        verbose=args.verbose
    )
    
    # تحديد المنافذ للفحص
    ports = None
    if args.ports:
        from modules import parse_port_range
        ports = parse_port_range(args.ports)
    
    # تنفيذ الفحص المطلوب
    if args.phone:
        # التحقق من صحة رقم الهاتف
        if not validate_phone_number(args.phone):
            print(colored(f"خطأ: رقم الهاتف غير صالح: {args.phone}", 'red'))
            sys.exit(1)
        
        print(colored(f"جاري فحص رقم الهاتف: {args.phone}", 'cyan'))
        scanner = PhoneScanner(verbose=args.verbose)
        results = scanner.scan(args.phone)
        
        # إنشاء التقرير
        report_file = report_generator.generate_phone_report(args.phone, results)
        print(colored(f"تم إنشاء التقرير: {report_file}", 'green'))
    
    elif args.username:
        # التحقق من صحة اسم المستخدم
        if not validate_username(args.username):
            print(colored(f"خطأ: اسم المستخدم غير صالح: {args.username}", 'red'))
            sys.exit(1)
        
        print(colored(f"جاري فحص اسم المستخدم: {args.username}", 'cyan'))
        scanner = UsernameScanner(verbose=args.verbose)
        results = scanner.scan(args.username)
        
        # إنشاء التقرير
        report_file = report_generator.generate_username_report(args.username, results)
        print(colored(f"تم إنشاء التقرير: {report_file}", 'green'))
    
    elif args.web or args.wordpress or args.joomla:
        url = args.web or args.wordpress or args.joomla
        
        # التحقق من صحة عنوان URL
        if not validate_url(url):
            print(colored(f"خطأ: عنوان URL غير صالح: {url}", 'red'))
            sys.exit(1)
        
        results = {}
        
        # فحص موقع ويب عام
        if args.web:
            print(colored(f"جاري فحص موقع الويب: {url}", 'cyan'))
            scanner = WebScanner(ports=ports, verbose=args.verbose)
            results = scanner.scan(url)
        
        # فحص موقع ووردبريس
        elif args.wordpress:
            print(colored(f"جاري فحص موقع ووردبريس: {url}", 'cyan'))
            scanner = WordpressScanner(verbose=args.verbose)
            results = scanner.scan(url)
        
        # فحص موقع جوملا
        elif args.joomla:
            print(colored(f"جاري فحص موقع جوملا: {url}", 'cyan'))
            scanner = JoomlaScanner(verbose=args.verbose)
            results = scanner.scan(url)
        
        # إنشاء التقرير
        report_file = report_generator.generate_web_report(url, results)
        print(colored(f"تم إنشاء التقرير: {report_file}", 'green'))
    
    print(colored("\nتم الانتهاء من الفحص بنجاح!", 'green'))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\nتم إيقاف الفحص بواسطة المستخدم", 'yellow'))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\nحدث خطأ غير متوقع: {str(e)}", 'red'))
        sys.exit(1)