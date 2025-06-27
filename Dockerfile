# استخدام صورة Python الرسمية كصورة أساسية
FROM python:3.9-slim

# تعيين متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# تعيين دليل العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . /app/

# تثبيت التبعيات
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت الحزمة في وضع التطوير
RUN pip install -e .

# تعريض المنفذ (إذا كان هناك خدمة ويب)
# EXPOSE 8000

# تعيين المستخدم غير الجذر
RUN groupadd -r jawal && \
    useradd -r -g jawal jawal && \
    chown -R jawal:jawal /app
USER jawal

# تعيين أمر التشغيل الافتراضي
ENTRYPOINT ["python", "main.py"]

# الأمر الافتراضي (يمكن تجاوزه)
CMD ["--help"]