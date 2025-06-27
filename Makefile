.PHONY: help setup test lint format clean docker docker-run

# المتغيرات
PYTHON = python
PIP = pip
VENV = venv
TEST = pytest
LINT = flake8
FORMAT = black
ISORTCMD = isort
MYPY = mypy

help: ## عرض هذه المساعدة
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## إعداد بيئة التطوير
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/$(PIP) install -r requirements.txt
	if [ -f dev-requirements.txt ]; then $(VENV)/bin/$(PIP) install -r dev-requirements.txt; fi
	$(VENV)/bin/$(PIP) install -e .

test: ## تشغيل الاختبارات
	$(VENV)/bin/$(TEST) tests/

test-cov: ## تشغيل الاختبارات مع تقرير التغطية
	$(VENV)/bin/$(TEST) tests/ --cov=modules --cov-report=html

lint: ## تشغيل أدوات التحقق من جودة الكود
	$(VENV)/bin/$(LINT) modules/ tests/
	if command -v $(MYPY) >/dev/null 2>&1; then $(VENV)/bin/$(MYPY) modules/; fi

format: ## تنسيق الكود باستخدام black وisort
	$(VENV)/bin/$(FORMAT) modules/ tests/
	$(VENV)/bin/$(ISORTCMD) modules/ tests/

clean: ## تنظيف الملفات المؤقتة
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# أوامر Docker
docker-build: ## بناء صورة Docker
	docker build -t jawal .

docker-run: ## تشغيل JawaL في حاوية Docker
	docker run --rm -it jawal $(ARGS)

docker-compose: ## تشغيل JawaL باستخدام Docker Compose
	docker-compose up --build

# أوامر التشغيل
run: ## تشغيل JawaL
	$(PYTHON) main.py $(ARGS)

# أوامر النشر
dist: clean ## إنشاء حزمة للتوزيع
	$(PYTHON) setup.py sdist bdist_wheel

release: dist ## نشر الحزمة على PyPI
	twine upload dist/*