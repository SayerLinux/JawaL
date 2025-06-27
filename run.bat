@echo off
REM JawaL - أداة إدارة سطح الهجوم والاستخبارات
REM المطور: Saudi Linux
REM البريد الإلكتروني: SaudiLinux7@gmail.com

echo JawaL - أداة إدارة سطح الهجوم والاستخبارات
echo =========================================

REM التحقق من وجود بيئة افتراضية
if not exist venv (
    echo إنشاء بيئة افتراضية جديدة...
    python -m venv venv
    if errorlevel 1 (
        echo فشل في إنشاء البيئة الافتراضية. تأكد من تثبيت Python 3.8 أو أحدث.
        exit /b 1
    )
)

REM تنشيط البيئة الافتراضية
echo تنشيط البيئة الافتراضية...
call venv\Scripts\activate.bat

REM تثبيت المتطلبات
if not exist venv\installed.txt (
    echo تثبيت المتطلبات...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo فشل في تثبيت المتطلبات.
        exit /b 1
    )
    echo تم التثبيت بنجاح > venv\installed.txt
)

REM تشغيل الأداة
echo تشغيل JawaL...
echo.
python main.py %*

REM إلغاء تنشيط البيئة الافتراضية
call venv\Scripts\deactivate.bat