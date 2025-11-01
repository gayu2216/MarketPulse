import pytest
import pandas as pd
from sales_forecaster import SalesForecaster


# --- Helper fixture to create a temporary CSV dataset for testing ---
@pytest.fixture
def sample_csv(tmp_path):
    """Creates a small valid CSV file for testing purposes."""
    data = {
        "Unnamed: 0": ["01/01", "01/02", "01/03"],
        "Food": ["$10.00", "$15.00", "$20.00"],
        "Drink": ["$5.00", "$8.00", "$10.00"],
        "Modifier": ["$1.00", "$2.00", "$1.00"],
        "Gross": ["$16.00", "$25.00", "$31.00"],
        "Tax": ["$1.60", "$2.50", "$3.10"],
        "Total": ["$17.60", "$27.50", "$34.10"]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "filename.csv"
    df.to_csv(file_path, index=False)
    return file_path


# ---------- TEST CASE 1 ----------
def test_valid_filename(sample_csv):
    """
    Test Case 1: Provide a valid CSV filename.
    Expected: The object is created successfully and load_and_clean_data() runs without error.
    """
    forecaster = SalesForecaster(str(sample_csv))
    forecaster.load_and_clean_data()
    assert not forecaster.df.empty
    assert "Total" in forecaster.df.columns
    print("test_valid_filename passed")


# ---------- TEST CASE 2 ----------
def test_invalid_file_extension(tmp_path):
    """
    Test Case 2: Provide a .txt filename instead of .csv.
    Expected: Object created, but loading data raises an error when trying to read.
    """
    file_path = tmp_path / "filename.txt"
    file_path.write_text("Some text data that is not CSV.")
    forecaster = SalesForecaster(str(file_path))
    with pytest.raises(Exception):
        forecaster.load_and_clean_data()
    print("test_invalid_file_extension passed")


# ---------- TEST CASE 3 ----------
def test_empty_filename():
    """
    Test Case 3: Provide an empty filename string.
    Expected: Raises FileNotFoundError or similar when trying to load data.
    """
    with pytest.raises((ValueError, FileNotFoundError, OSError)):
        forecaster = SalesForecaster("")
        forecaster.load_and_clean_data()
    print("test_empty_filename passed")


if __name__ == "__main__":
    try:
        # Run tests manually if not using pytest command
        test_valid_filename(sample_csv=None)
        test_invalid_file_extension(None)
        test_empty_filename()
        print("\nAll 3 test cases executed successfully.")
    except Exception as e:
        print("Exception occurred:", e)
