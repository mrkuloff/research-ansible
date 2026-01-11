from google import genai
import json

client = genai.Client(api_key="")

def analyze_playbook(playbook_path: str) -> dict:
    """
    Анализирует Ansible-плейбук на предмет уязвимостей безопасности
    с использованием модели Gemini через Google AI Studio.
    """
    with open(playbook_path, 'r') as f:
        playbook_content = f.read()

    system_instruction = """Ты — эксперт по безопасности Ansible и DevOps инженер. Проанализируй предоставленный плейбук Ansible. Найди потенциальные уязвимости безопасности, нарушения best practices и антипаттерны.

    Сфокусируйся на:
    1.  **Секреты:** Хардкодированные пароли, токены, ключи.
    2.  **Небезопасное выполнение:** Использование модулей `shell`/`command` с непроверяемым вводом, отсутствие `no_log: true`.
    3.  **Привилегии:** Небезопасное использование `become`, `sudo` без пароля.
    4.  **Конфигурация:** Слабые права на файлы (mode 0777), небезопасные настройки.
    5.  **Состояние:** Использование устаревших или неподдерживаемых модулей.

    ФОРМАТ ВЫВОДА: Ты ДОЛЖЕН вернуть **ТОЛЬКО валидный JSON-объект** без каких-либо обратных кавычек, комментариев или поясняющего текста вокруг.
    Структура JSON должна быть следующей:
    {
      "issues_found": [
        {
          "severity": "HIGH|MEDIUM|LOW",
          "type": "HARDCODED_SECRET|INSECURE_EXECUTION|WEAK_PERMISSIONS|...",
          "task_name": "Имя задачи или 'vars' или 'play'",
          "description": "Краткое описание проблемы",
          "remediation": "Конкретное предложение по исправлению с примером кода, если возможно"
        }
      ],
      "summary": "Общая оценка безопасности плейбука"
    }
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            system_instruction,
            f"Вот плейбук Ansible для анализа:\n```yaml\n{playbook_content}\n```"
        ]
    )

    response_text = response.text.strip()

    try:
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])

        analysis_result = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON от модели: {e}")
        print(f"Полученный ответ:\n{response_text}")
        analysis_result = {"error": "Модель вернула невалидный JSON", "raw_response": response_text}

    return analysis_result

if __name__ == "__main__":
    result = analyze_playbook("playbooks/nginx-playbook.yml")
    print(json.dumps(result, indent=2, ensure_ascii=False))