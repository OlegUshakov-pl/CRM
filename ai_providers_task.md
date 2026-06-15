# Техзадание: AI-провайдеры и страница Settings в CRM

## Контекст

В CRM уже есть модули AI Files и AI Chat. Нужно добавить полноценное управление AI-провайдерами и вынести Settings на отдельную страницу с вкладками.

---

## Задача 1 — Страница Settings

### Текущее состояние
Settings открывается как боковая панель (drawer) поверх контента.

### Что сделать
Вынести Settings на отдельную страницу по маршруту `/settings`. Убрать drawer. В сайдбаре пункт "Settings" (иконка шестерёнки) внизу навигации — ведёт на `/settings`.

### Структура страницы
Страница делится на вкладки:

| Вкладка | Содержимое |
|---|---|
| **General** | То, что есть сейчас: Project Storage Path, Subfolder Names |
| **AI** | Новый раздел (см. Задачу 2) |
| **Users** | Управление пользователями (если есть) |

---

## Задача 2 — AI-провайдеры (вкладка AI в Settings)

### 2.1 Выбор провайдера

Отображать провайдеров карточками в сетке (4 колонки). При выборе карточка выделяется. Выбор сохраняется в конфиг.

**Список провайдеров:**

| ID | Название | Тип | Префикс ключа | Ссылка на ключ |
|---|---|---|---|---|
| `anthropic` | Anthropic | Cloud | `sk-ant-` | https://console.anthropic.com/settings/keys |
| `openai` | OpenAI | Cloud | `sk-` | https://platform.openai.com/api-keys |
| `google` | Google AI | Cloud | `AIza` | https://aistudio.google.com/app/apikey |
| `mistral` | Mistral | Cloud | — | https://console.mistral.ai/api-keys |
| `groq` | Groq | Cloud | `gsk_` | https://console.groq.com/keys |
| `deepseek` | DeepSeek | Cloud | `sk-` | https://platform.deepseek.com/api_keys |
| `openrouter` | OpenRouter | Aggregator | `sk-or-` | https://openrouter.ai/keys |
| `ollama` | Ollama | Local | — (нет ключа) | — |

### 2.2 Поле API-ключа

- Показывается для всех провайдеров кроме Ollama
- Тип `password` по умолчанию, кнопка "показать/скрыть"
- `placeholder` — префикс ключа провайдера + `...`
- Под полем — подсказка со ссылкой: "Получить ключ: {ссылка}" (открывается в новой вкладке)
- Рядом с лейблом — цветная точка-индикатор статуса: серая (не проверен), зелёная (OK), красная (ошибка)
- Кнопка **"Проверить ключ"** — делает тестовый запрос к API (см. 2.4)

### 2.3 Для Ollama — поле Base URL

Вместо поля ключа показывать поле **Base URL** со значением по умолчанию `http://localhost:11434`. Подсказка: "Убедитесь, что Ollama запущена локально."

### 2.4 Загрузка моделей

**Алгоритм:**
1. Пользователь выбрал провайдера и ввёл ключ
2. При нажатии "Проверить ключ" — отправить запрос к API провайдера
3. Если ключ валидный — получить список моделей и отрисовать карточками
4. Если ошибка — показать индикатор ошибки и статичный список моделей по умолчанию

**Endpoints для получения моделей:**

| Провайдер | Метод | URL | Заголовок |
|---|---|---|---|
| Anthropic | GET | `https://api.anthropic.com/v1/models` | `x-api-key: {key}`, `anthropic-version: 2023-06-01` |
| OpenAI | GET | `https://api.openai.com/v1/models` | `Authorization: Bearer {key}` |
| Google | GET | `https://generativelanguage.googleapis.com/v1beta/models?key={key}` | — |
| Mistral | GET | `https://api.mistral.ai/v1/models` | `Authorization: Bearer {key}` |
| Groq | GET | `https://api.groq.com/openai/v1/models` | `Authorization: Bearer {key}` |
| DeepSeek | GET | `https://api.deepseek.com/models` | `Authorization: Bearer {key}` |
| OpenRouter | GET | `https://openrouter.ai/api/v1/models` | `Authorization: Bearer {key}` |
| Ollama | GET | `{baseUrl}/api/tags` | — |

> ⚠️ Запросы к API провайдеров делать через **backend-прокси** (не из браузера напрямую), чтобы не светить ключ в DevTools и обойти CORS.

**Статичный список моделей по умолчанию** (показывается если нет ключа или запрос не удался):

```json
{
  "anthropic": [
    { "id": "claude-opus-4-6", "name": "Claude Opus 4", "tags": ["smart"] },
    { "id": "claude-sonnet-4-6", "name": "Claude Sonnet 4", "tags": ["smart", "fast"] },
    { "id": "claude-haiku-4-5", "name": "Claude Haiku", "tags": ["fast", "cheap"] }
  ],
  "openai": [
    { "id": "gpt-4o", "name": "GPT-4o", "tags": ["smart", "vision"] },
    { "id": "gpt-4o-mini", "name": "GPT-4o mini", "tags": ["fast", "cheap"] },
    { "id": "o3", "name": "o3", "tags": ["smart"] },
    { "id": "o4-mini", "name": "o4-mini", "tags": ["smart", "fast"] }
  ],
  "google": [
    { "id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tags": ["smart", "vision"] },
    { "id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "tags": ["fast", "cheap"] }
  ],
  "mistral": [
    { "id": "mistral-large-latest", "name": "Mistral Large", "tags": ["smart"] },
    { "id": "mistral-small-latest", "name": "Mistral Small", "tags": ["cheap", "fast"] },
    { "id": "codestral-latest", "name": "Codestral", "tags": ["smart"] }
  ],
  "groq": [
    { "id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "tags": ["fast", "smart"] },
    { "id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B", "tags": ["fast", "cheap"] }
  ],
  "deepseek": [
    { "id": "deepseek-chat", "name": "DeepSeek V3", "tags": ["smart", "cheap"] },
    { "id": "deepseek-reasoner", "name": "DeepSeek R1", "tags": ["smart"] }
  ],
  "openrouter": [
    { "id": "meta-llama/llama-3.3-70b-instruct", "name": "Llama 3.3 70B", "tags": ["smart", "cheap"] },
    { "id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "tags": ["smart"] },
    { "id": "anthropic/claude-sonnet-4-6", "name": "Claude Sonnet 4", "tags": ["smart", "fast"] },
    { "id": "deepseek/deepseek-chat", "name": "DeepSeek V3", "tags": ["cheap"] }
  ],
  "ollama": [
    { "id": "llama3.2", "name": "Llama 3.2", "tags": ["local"] },
    { "id": "qwen2.5-coder", "name": "Qwen 2.5 Coder", "tags": ["local", "smart"] },
    { "id": "phi4", "name": "Phi-4", "tags": ["local"] },
    { "id": "mistral", "name": "Mistral 7B", "tags": ["local", "fast"] }
  ]
}
```

### 2.5 Обновление списка моделей с провайдера

Над сеткой моделей разместить строку с кнопкой **"Обновить список моделей"** (иконка обновления) и текстом последнего обновления: `Обновлено: 14 июня 2025, 18:42` (или `Никогда` если ещё не загружались).

**Поведение кнопки:**
1. Кнопка переходит в состояние загрузки (спиннер, текст "Загружаю...")
2. Отправляется запрос к endpoint провайдера (см. таблицу в 2.4)
3. Полученный список моделей нормализуется и **мерджится** с текущим:
   - Новые модели добавляются
   - Существующие обновляются (название, описание)
   - Модели добавленные вручную (см. 2.6) — **не удаляются**
4. Результат сохраняется в конфиг с меткой времени
5. Список перерисовывается, кнопка возвращается в нормальное состояние

**При ошибке** (нет ключа, нет сети, API недоступен): показать toast с текстом ошибки, список не меняется.

**Автообновление**: при первом вводе валидного ключа — автоматически запустить загрузку моделей без ручного нажатия.

**Нормализация ответа провайдера** — каждый провайдер возвращает разную структуру, нужно привести к единому формату `{ id, name }`:

| Провайдер | Поле ID | Поле названия |
|---|---|---|
| Anthropic | `id` | `display_name` |
| OpenAI | `id` | `id` (названия нет) |
| Google | `name` (вида `models/gemini-2.5-pro`) → обрезать префикс `models/` | `displayName` |
| Mistral | `id` | `name` |
| Groq | `id` | `id` |
| DeepSeek | `id` | `id` |
| OpenRouter | `id` | `name` |
| Ollama | `model` (из `models[].model`) | `name` |

---

### 2.6 Ручное добавление моделей

Под сеткой моделей — кнопка **"+ Добавить модель вручную"**. По клику появляется инлайн-форма (не модалка) с двумя полями:

```
Model ID:    [ gpt-4-turbo-preview        ]
Название:    [ GPT-4 Turbo Preview        ]  (необязательно)
             [Добавить]  [Отмена]
```

**Поведение:**
- Model ID обязателен, название — опционально (если не заполнено, используется ID)
- После добавления модель появляется в сетке с бейджем `Custom`
- Кастомные модели помечаются флагом `"custom": true` в конфиге
- На карточке кастомной модели — иконка удаления (крестик), по клику — удалить с подтверждением

**Хранение кастомных моделей в конфиге:**

```json
{
  "ai": {
    "provider": "openai",
    "apiKey": "sk-...",
    "model": "gpt-4-turbo-preview",
    "modelsCache": {
      "openai": {
        "updatedAt": "2025-06-14T15:42:00Z",
        "models": [
          { "id": "gpt-4o", "name": "GPT-4o", "custom": false },
          { "id": "gpt-4-turbo-preview", "name": "GPT-4 Turbo Preview", "custom": true }
        ]
      }
    }
  }
}
```

---

### 2.7 Карточки моделей

Сетка 3 колонки. Каждая карточка содержит:
- Название модели
- ID модели (мелким шрифтом под названием)
- Бейдж `Custom` для добавленных вручную + иконка удаления
- Бейджи из статичного списка (для известных моделей): `Быстро` / `Умно` / `Дёшево` / `Локально` / `Vision`

При клике на карточку — модель выбирается (выделение рамкой). Выбор сохраняется в конфиг.

### 2.8 Хранение конфига

Сохранять в файл настроек приложения (например `config.json` или аналог, который уже используется в проекте):

```json
{
  "ai": {
    "provider": "anthropic",
    "apiKey": "sk-ant-...",
    "baseUrl": "",
    "model": "claude-sonnet-4-6"
  }
}
```

> ⚠️ API-ключ хранить в зашифрованном виде или через системное хранилище (electron `safeStorage` если это Electron-приложение). Не хранить в открытом тексте в файле конфига.

### 2.9 Использование конфига в AI Chat и AI Files

После сохранения настроек модули AI Chat и AI Files должны подхватывать:
- Выбранного провайдера и модель
- API-ключ для запросов

Если ключ не задан — показывать в AI Chat/AI Files предупреждение: "Настройте AI-провайдера в Settings → AI".

---

## Кнопка "Сохранить"

По клику:
1. Валидировать заполненность обязательных полей (провайдер + ключ для cloud-провайдеров, baseUrl для Ollama)
2. Сохранить конфиг
3. Показать toast-уведомление "Настройки сохранены"

---

## Приоритет реализации


1. Страница Settings с вкладками (Задача 1)
2. Статичный список провайдеров и моделей (Задача 2, без динамической загрузки)
3. Сохранение и чтение конфига (включая `modelsCache`)
4. Ручное добавление моделей (секция 2.6)
5. Динамическая загрузка моделей через кнопку "Обновить" (секция 2.5)
6. Автообновление при первом вводе ключа
