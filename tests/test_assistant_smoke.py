# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from django.contrib.auth.models import User
from assistant.services import LLMService
from assistant.services import handlers as h

user, _ = User.objects.get_or_create(username='aitester', defaults={'is_staff': True, 'is_superuser': True})
llm = LLMService()

# Ensure there's a project for material/drawings/company commands
from projects.models import Project
project, _ = Project.objects.get_or_create(
    name='Test',
    defaults={'number': '001', 'status': 'planning', 'created_by': user},
)
from companies.models import Company
company, _ = Company.objects.get_or_create(name='TestCorp', defaults={'email': 'info@testcorp.local'})
project.company = company
project.save()

from contacts.models import Contact
Contact.objects.get_or_create(first_name='Иван', last_name='Петров', defaults={'phone': '+7-900-000-00-00', 'email': 'ivan@test.local'})

cases = [
    ("RU", "Сколько у меня активных задач?"),
    ("RU", "Создай проект 002, Demo на завтра"),
    ("RU", "Добавь задачу Позвонить клиенту на завтра"),
    ("RU", "Найди контакт Иван"),
    ("RU", "Добавь материал Болт 50 в проект Test"),
    ("RU", "Покажи все чертежи по проекту Test"),
    ("RU", "Какая компания у проекта Test"),
    ("RU", "Создай заметку Встреча к проекту Test"),
    ("RU", "Скачай картинку с https://www.python.org/static/img/python-logo.png"),
    ("RU", "Открой bbc.com"),
    ("EN", "How many active tasks?"),
    ("EN", "Create project 003, Demo2 on tomorrow"),
    ("EN", "Add task Call client on tomorrow"),
    ("EN", "Find contact Ivan"),
    ("EN", "Add material Bolt 50 to project Test"),
    ("EN", "Show all drawings of project Test"),
    ("EN", "What is the company of project Test"),
    ("EN", "Create note Meeting for project Test"),
    ("EN", "Open bbc.com"),
]

for lang, c in cases:
    r = llm.process(c, user)
    kind = r.get('kind', '?')
    intent = r.get('intent', '—')
    msg = (r.get('message') or r.get('error') or '')[:160]
    print(f'[{lang} | {kind:10} | {intent:18}] {c}')
    print(f'    -> {msg}')
    if r.get('needs_confirmation'):
        last = r.get('payload', {})
        intent_name = last.get('intent')
        if intent_name:
            res = h.perform_confirmed(intent_name, user, last)
            print(f'    CONFIRMED → ok={res.ok} msg={(res.message or res.error)[:140]}')
    print()
