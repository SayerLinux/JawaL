#!/bin/bash
# JawaL - أداة إدارة سطح الهجوم والاستخبارات
# المطور: Saudi Linux
# البريد الإلكتروني: SaudiLinux7@gmail.com

echo "JawaL - أداة إدارة سطح الهجوم والاستخبارات"
echo "=========================================="

# التحقق من وجود بيئة افتراضية
if [ ! -d "venv" ]; then
    echo "إنشاء بيئة افتراضية جديدة..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "فشل في إنشاء البيئة الافتراضية. تأكد من تثبيت Python 3.8 أو أحدث."
        exit 1
    fi
fi

# تنشيط البيئة الافتراضية
echo "تنشيط البيئة الافتراضية..."
source venv/bin/activate

# تثبيت المتطلبات
if [ ! -f "venv/installed.txt" ]; then
    echo "تثبيت المتطلبات..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "فشل في تثبيت المتطلبات."
        exit 1
    fi
    echo "تم التثبيت بنجاح" > venv/installed.txt
fi

# جعل الملف قابل للتنفيذ
if [ ! -x "main.py" ]; then
    chmod +x main.py
fi

# تشغيل الأداة
echo "تشغيل JawaL..."
echo 
python main.py "$@"

# إلغاء تنشيط البيئة الافتراضية
deactivate