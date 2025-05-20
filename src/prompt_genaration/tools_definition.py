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
]
