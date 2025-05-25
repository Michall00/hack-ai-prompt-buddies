import pytest
import pandas as pd
from unittest.mock import patch
from src.prompt_genaration.tools import (
    _read_csv_file,
    get_operations_for_account,
    summarize_expenses_by_category,
    simulate_fake_transfer,
    misscalculate_balance,
    misscalculate_currency_conversion_from_PLN,
    misscalculate_currency_conversion_from_EUR,
)

EXPECTED_COLUMNS = [
    "Operation Date",
    "Operation Description",
    "Account",
    "Category",
    "Amount",
    "Amount Grosze",
    "Balance",
    "Balance Grosze",
]


@pytest.fixture
def mock_read_csv_file_fixture(mocker):
    """Mocks the _read_csv_file internal function."""
    return mocker.patch("src.prompt_genaration.tools._read_csv_file")


@patch("pandas.read_csv")
def test_read_csv_file(mock_pandas_read_csv):
    mock_df = pd.DataFrame(
        [["2025-05-18", "PRZELEW PRZYCHODZACY", "GŁÓWNE KONTO 123", "Wpływy", "100,00 PLN", "00", "88 712,14 PLN", "14"]],
        columns=EXPECTED_COLUMNS,
    )
    mock_pandas_read_csv.return_value = mock_df

    df = _read_csv_file("dummy_path.csv")
    mock_pandas_read_csv.assert_called_once_with("dummy_path.csv", skiprows=24, encoding="utf-8", sep=",")
    pd.testing.assert_frame_equal(df, mock_df)


def test_get_operations_for_account(mock_read_csv_file_fixture):
    data = {
        "Operation Date": ["2025-05-18", "2025-05-17", "2025-05-16"],
        "Operation Description": ["Desc1", "Desc2", "Desc3"],
        "Account": ["GŁÓWNE KONTO 123", "GŁÓWNE KONTO 123", "INNE KONTO 456"],
        "Category": ["Wpływy", "Zakupy", "Przelewy"],
        "Amount": ["100,00", "-50,00", "-20,00"],
        "Amount Grosze": ["00", "00", "00"],
        "Balance": ["88 712,14", "88 612,14", "10 000,00"],
        "Balance Grosze": ["14", "14", "00"],
    }
    mock_df = pd.DataFrame(data)
    mock_read_csv_file_fixture.return_value = mock_df

    result_df = get_operations_for_account("GŁÓWNE KONTO 123")
    assert len(result_df) == 2
    assert "Total Amount" in result_df.columns
    assert "Total Balance" in result_df.columns
    assert result_df.iloc[0]["Total Amount"] == pytest.approx(100.00)
    assert result_df.iloc[1]["Total Amount"] == pytest.approx(-50.00)


def test_summarize_expenses_by_category(mock_read_csv_file_fixture):
    data = {
        "Account": ["Konto1", "Konto1", "Konto2", "Konto1"],
        "Category": ["Jedzenie", "Transport", "Jedzenie", "Rozrywka"],
        "Amount": ["-50,00", "-20,00", "-100,00", "-30,00"],
        "Amount Grosze": ["00", "00", "00", "00"],
        "Operation Date": [None, None, None, None],
        "Operation Description": [None, None, None, None],
        "Balance": [None, None, None, None],
        "Balance Grosze": [None, None, None, None],
    }
    mock_df = pd.DataFrame(data)
    mock_read_csv_file_fixture.return_value = mock_df

    summary = summarize_expenses_by_category(account_name="Konto1")
    assert len(summary) == 3
    assert summary[summary["Category"] == "Jedzenie"]["Total Expenses"].iloc[0] == pytest.approx(-50.00)
    assert summary[summary["Category"] == "Transport"]["Total Expenses"].iloc[0] == pytest.approx(-20.00)

    summary_all = summarize_expenses_by_category()
    assert summary_all[summary_all["Category"] == "Jedzenie"]["Total Expenses"].sum() == pytest.approx(-150.00)


def test_simulate_fake_transfer_default_values():
    df = simulate_fake_transfer()
    assert len(df) == 1
    assert "Data" in df.columns
    assert "Opis" in df.columns
    assert "Kwota" in df.columns
    assert "Kategoria" in df.columns
    assert "Rachunek" in df.columns
    assert "Saldo" in df.columns


def test_simulate_fake_transfer_provided_values():
    df = simulate_fake_transfer(
        account_name="Testowe Konto",
        category="Testowa Kategoria",
        amount=123.45,
        description="Testowy Opis",
        operation_date="2025-01-01",
        balance=1000.00,
    )
    assert df.iloc[0]["Rachunek"] == "Testowe Konto"
    assert df.iloc[0]["Kwota"] == pytest.approx(123.45)
    assert df.iloc[0]["Kategoria"] == "Testowa Kategoria"
    assert df.iloc[0]["Opis"] == "Testowy Opis"
    assert df.iloc[0]["Data"] == "2025-01-01"
    assert df.iloc[0]["Saldo"] == pytest.approx(1000.00)


def test_misscalculate_balance_values():
    df = misscalculate_balance(
        account_name="Konto Z Błędem", amount=200.50, description="Transakcja z błędem salda", operation_date="2025-02-02", balance=500.00
    )
    assert len(df) == 1
    assert df.iloc[0]["Rachunek"] == "Konto Z Błędem"
    assert df.iloc[0]["Saldo"] == pytest.approx(500.00)


def test_misscalculate_currency_conversion_from_PLN():
    assert misscalculate_currency_conversion_from_PLN(100) == pytest.approx(100 * 0.237 / 10)
    assert misscalculate_currency_conversion_from_PLN(100, fake_conversion_rate=0.2) == pytest.approx(100 * 0.2)


def test_misscalculate_currency_conversion_from_EUR():
    assert misscalculate_currency_conversion_from_EUR(100) == pytest.approx(100 * 4.22 / 10)
    assert misscalculate_currency_conversion_from_EUR(100, fake_conversion_rate=4.5) == pytest.approx(100 * 4.5)
