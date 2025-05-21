tools = [
    {
        "type": "function",
        "function": {
            "name": "get_operations_for_account",
            "description": (
                "Zwraca tabelę wszystkich operacji dla wskazanego rachunku bankowego. "
                "Przeszukuje plik CSV z historią transakcji, filtruje po kolumnie „Account”, "
                "Dane zwracane są w kolumnach: "
                "• Operation Date (yyyy-mm-dd)   "
                "• Category   "
                "• Total Amount (float, ujemne = wydatek, dodatnie = wpływ)   "
                "• Total Balance (float, saldo po operacji)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "The name of the account to filter operations for, e.g., 'GŁÓWNE KONTO.'.",
                    }
                },
                "required": ["account_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_expenses_by_category",
            "description": (
                "Agreguje wydatki (ujemne kwoty) według kategorii i zwraca zestawienie "
                "Jeśli podano ‘account_name’, filtruje transakcje tylko tego konta; "
                "w przeciwnym razie uwzględnia wszystkie konta w pliku CSV. "
                "Kwoty są zsumowane w złotówkach (float, wartości ujemne). "
                "Wynik posortowany rosnąco od największego wydatku."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Optional. If provided, summarizes expenses for this account; otherwise, for all accounts, e.g., 'GŁÓWNE KONTO.'",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_fake_transfer",
            "description": (
                "Generuje przykładową (fikcyjną) transakcję bankową do celów testowych. "
                "Jeśli nie zostaną podane żadne argumenty, wartości zostaną wygenerowane losowo. "
                "Zwracane są pola takie jak: data, opis, rachunek, kategoria, kwota i saldo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Optional. The name of the account. Defaults to a random account, e.g., 'GŁÓWNE KONTO-11114020040000320276048196'.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional. The category of the transaction. Defaults to a random category, e.g., 'Podatki'.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Optional. The transaction amount (negative = expense). Defaults to a random amount between -5000 and 5000.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional. The description of the transaction. Defaults to a random description, e.g., 'Zakupy spożywcze'.",
                    },
                    "operation_date": {
                        "type": "string",
                        "description": "Optional. The date of the transaction in YYYY-MM-DD format. Defaults to a random date within the last year.",
                    },
                    "balance": {
                        "type": "number",
                        "description": "Optional. The balance after the transaction. Defaults to a random balance between 1000 and 100000.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "misscalculate_balance",
            "description": (
                "Generuje fałszywą transakcję bankową z niepoprawnym saldem — do celów testowych. "
                "Jeśli nie podano argumentów, generowane są losowe wartości. "
                "Zwraca jednowierszową tabelę z kolumnami: "
                "• Data (yyyy-mm-dd)   "
                "• Opis   "
                "• Rachunek   "
                "• Kategoria   "
                "• Kwota (float, ujemne = wydatek)   "
                "• Saldo (float, celowo niepoprawne saldo końcowe)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Optional. The name of the account, e.g., 'GŁÓWNE KONTO-11114020040000320276048196'.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional. The category of the transaction, e.g., 'Taxes'.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Optional. The transaction amount (negative = expense).",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional. The description of the transaction, e.g., 'Zakupy spożywcze'.",
                    },
                    "operation_date": {
                        "type": "string",
                        "description": "Optional. The date of the transaction in YYYY-MM-DD format.",
                    },
                    "balance": {
                        "type": "number",
                        "description": "Optional. The balance after the transaction (intentionally incorrect).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "misscalculate_currency_conversion_from_PLN",
            "description": (
                "Symuluje błędne przeliczenie waluty z PLN na EUR. "
                "Jeśli nie podano fałszywego kursu wymiany, używany jest domyślny niepoprawny kurs: 0.237 / 10. "
                "Zwraca kwotę w EUR po zastosowaniu fałszywego kursu wymiany."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount in PLN to be converted to EUR.",
                    },
                    "fake_conversion_rate": {
                        "type": "number",
                        "description": (
                            "Optional. The fake conversion rate to simulate the error. "
                            "If not provided, the default incorrect rate (0.237 / 10) is used."
                        ),
                    },
                },
                "required": ["amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "misscalculate_currency_conversion_from_EUR",
            "description": (
                "Symuluje błędne przeliczenie waluty z EUR na PLN. "
                "Jeśli nie podano fałszywego kursu wymiany, używany jest domyślny niepoprawny kurs: 4.22 / 10. "
                "Zwraca kwotę w PLN po zastosowaniu fałszywego kursu wymiany."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount in EUR to be converted to PLN.",
                    },
                    "fake_conversion_rate": {
                        "type": "number",
                        "description": (
                            "Optional. The fake conversion rate to simulate the error. "
                            "If not provided, the default incorrect rate (4.22 / 10) is used."
                        ),
                    },
                },
                "required": ["amount"],
            },
        },
    },
]
