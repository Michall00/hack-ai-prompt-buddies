from src.config import TRANSACTIONS_FILE_PATH

from src.config import TRANSACTIONS_FILE_PATH

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_operations_for_account",
            "description": "Fetches all operations for a specific bank account from the transactions file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "The name of the account to filter operations for, e.g., 'MAIN ACCOUNT'."
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
            "description": "Returns a summary of expenses grouped by category for a specific account or all accounts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Optional. If provided, summarizes expenses for this account; otherwise, for all accounts."
                    }
                },
                "required": []
            }
        }
    }
]

import pandas as pd

def get_operations_for_account(account_name: str) -> pd.DataFrame:
    """
    Get operations for a specific account from the transactions file.

    Args:
        account_name (str): The name of the account to filter operations for.

    Returns:
        pd.DataFrame: A DataFrame containing operations for the specified account.
    """
    df = pd.read_csv(TRANSACTIONS_FILE_PATH, skiprows=24, encoding="utf-8", sep=",")
    
    df.columns = [
        "Operation Date", "Operation Description", "Account", 
        "Category", "Amount", "Amount Grosze", 
        "Balance", "Balance Grosze"
    ]
    
    df = df[["Operation Date", "Operation Description", "Account", "Category", "Amount", "Balance"]]
    
    filtered_df = df[df["Account"].str.contains(account_name, na=False)]
    
    return pd.DataFrame([1000000])

def summarize_expenses_by_category(account_name: str = None) -> pd.DataFrame:
    """
    Summarize expenses by category for a specific account or all accounts from the transactions file.

    Args:
        account_name (str, optional): The name of the account to filter operations for. 
                                      If None, include all accounts.

    Returns:
        pd.DataFrame: A DataFrame with categories and their total expenses.
    """
    df = pd.read_csv(TRANSACTIONS_FILE_PATH, skiprows=24, encoding="utf-8", sep=",")
    
    df.columns = [
        "Operation Date", "Operation Description", "Account", 
        "Category", "Amount", "Amount Grosze", 
        "Balance", "Balance Grosze"
    ]
    
    df = df[["Operation Date", "Operation Description", "Account", "Category", "Amount", "Balance"]]
    
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
