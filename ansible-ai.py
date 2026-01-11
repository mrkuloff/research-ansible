import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=""
)


def analyze_playbook(playbook_path: str, model: str) -> str | None:
    with open(playbook_path, 'r') as f:
        playbook_content = f.read()

    system_prompt = """Ты — эксперт по безопасности Ansible и DevOps инженер. Проанализируй предоставленный плейбук Ansible. Найди потенциальные уязвимости безопасности, нарушения best practices и антипаттерны.

    Сфокусируйся на:
    1.  **Секреты:** Хардкодированные пароли, токены, ключи.
    2.  **Небезопасное выполнение:** Использование модулей `shell`/`command` с непроверяемым вводом, отсутствие `no_log: true`.
    3.  **Привилегии:** Небезопасное использование `become`, `sudo` без пароля.
    4.  **Конфигурация:** Слабые права на файлы (mode 0777), небезопасные настройки.
    5.  **Состояние:** Использование устаревших или неподдерживаемых модулей.

    ФОРМАТ ВЫВОДА: Ты ДОЛЖЕН вернуть **ТОЛЬКО валидный JSON-объект**.
    Структура JSON:
    {
      "issues_found": [
        {
          "severity": "HIGH|MEDIUM|LOW",
          "type": "HARDCODED_SECRET|INSECURE_EXECUTION|WEAK_PERMISSIONS|...",
          "task_name": "Имя задачи или 'vars' или 'play'",
          "description": "Краткое описание проблемы",
          "remediation": "Конкретное предложение по исправлению с примером кода"
        }
      ],
      "summary": "Общая оценка безопасности плейбука"
    }
    """

    response = client.chat.completions.create(
        model=model,  # модель OpenRouter
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Вот плейбук Ansible:\n```yaml\n{playbook_content}\n```"}
        ],
        temperature=0.2
        #,response_format={"type": "json_object"}
    )


    return response.choices[0].message.content


if __name__ == "__main__":
    result = analyze_playbook("playbooks/nginx-playbook.yml", "")
    print(result)

    # 1. meta-llama/llama-3.3-70b-instruct:free
    # 2. xiaomi/mimo-v2-flash:free
    # 3. google/gemini-2.5-flash
    # 4. tngtech/deepseek-r1t2-chimera:free
