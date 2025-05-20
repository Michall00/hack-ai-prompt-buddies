from src.config import TRANSACTIONS_FILE_PATH

from src.config import TRANSACTIONS_FILE_PATH

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
                        "description": "The name of the account to filter operations for, e.g., 'GŁÓWNE KONTO.'."
                    }
                },
                "required": ["account_name"]
            }
        }
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
                        "description": "Optional. If provided, summarizes expenses for this account; otherwise, for all accounts, e.g., 'GŁÓWNE KONTO.'"
                    }
                },
                "required": []
            }
        }
    }
]

import pandas as pd


def _read_csv_file(csv_path: str) -> pd.DataFrame:
    """
    Read a CSV file and return it as a DataFrame.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.
    """
    df = pd.read_csv(csv_path, skiprows=24, encoding="utf-8", sep=",")
    
    df.columns = [
        "Operation Date", "Operation Description", "Account", 
        "Category", "Amount", "Amount Grosze", 
        "Balance", "Balance Grosze"
    ]
    
    return df

def get_operations_for_account(account_name: str) -> pd.DataFrame:
    """
    Extract operations for a specific account name from a CSV file.

    Args:
        account_name (str): The name of the account to filter operations for.

    Returns:
        pd.DataFrame: A DataFrame containing operations for the specified account.
    """
    df = _read_csv_file(TRANSACTIONS_FILE_PATH)
    
    df = df[df["Account"].str.contains(account_name, na=False)]

    df["Amount"] = df["Amount"].replace(r'^\s*$', '0', regex=True).fillna('0')
    df["Amount Grosze"] = df["Amount Grosze"].replace(r'^\s*$', '0', regex=True).fillna('0')
    df["Balance Grosze"] = df["Balance Grosze"].replace(r'^\s*$', '0', regex=True).fillna('0')
    
    def safe_convert(value):
        try:
            return float(value.replace(',', '').replace(' ', '').replace('PLN', ''))
        except ValueError:
            return 0.0

    df["Amount"] = df["Amount"].apply(safe_convert)
    df["Amount Grosze"] = df["Amount Grosze"].apply(safe_convert) / 100  
    df["Balance Grosze"] = df["Balance Grosze"].apply(safe_convert) / 100  
    
    df["Total Amount"] = df["Amount"] + df["Amount Grosze"]
    df["Total Balance"] = df["Balance Grosze"]
    
    df = df.drop(columns=["Amount", "Amount Grosze", "Balance Grosze", "Balance", "Account", "Operation Description"])
    return df

def summarize_expenses_by_category(account_name: str = None) -> pd.DataFrame:
    """
    Summarize expenses by category for a specific account or all accounts from the transactions file.

    Args:
        account_name (str, optional): The name of the account to filter operations for. 
                                      If None, include all accounts.

    Returns:
        pd.DataFrame: A DataFrame with categories and their total expenses.
    """
    df = _read_csv_file(TRANSACTIONS_FILE_PATH)
    
    if account_name:
        df = df[df["Account"].str.contains(account_name, na=False)]
    
    df["Amount"] = df["Amount"].replace(r'^\s*$', '0', regex=True).fillna('0')
    
    def safe_convert(value):
        try:
            return float(value.replace(',', '').replace(' ', '').replace('PLN', ''))
        except ValueError:
            return 0.0

    df["Amount"] = df["Amount"].apply(safe_convert)
    
    expenses = df[df["Amount"] < 0]
    summary = expenses.groupby("Category")["Amount"].sum().reset_index()
    summary.columns = ["Category", "Total Expenses"]
    summary = summary.sort_values(by="Total Expenses", ascending=True).reset_index(drop=True)
    
    return summary
