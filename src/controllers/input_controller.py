import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt


class SalesForecaster:
    def __init__(self, file_path: str):
        if not isinstance(file_path, str):
            raise TypeError(f"Expected file_path to be str, got {type(file_path).__name__}")
        self.file_path = file_path
        self.df = None
        self.model = None
        self.forecast = None

    def load_and_clean_data(self):
        """Loads and cleans the sales data from CSV."""
        self.df = pd.read_csv(self.file_path)

        expected_cols = ["Food", "Drink", "Modifier", "Gross", "Tax", "Total"]
        for col in expected_cols:
            if col not in self.df.columns:
                raise ValueError(f"Missing expected column: {col}")

            # Remove $ and commas
            self.df[col] = self.df[col].replace({'\$': '', ',': ''}, regex=True).astype(float)

        # Rename date column and format properly
        if "Unnamed: 0" not in self.df.columns:
            raise ValueError("Missing 'Unnamed: 0' column for Date")
        self.df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)

        # Add year to the date and convert
        self.df["Date"] = pd.to_datetime(self.df["Date"] + "/2024", format="%m/%d/%Y")

        print("✅ Data loaded and cleaned successfully.")
        print(self.df.head())

    def summarize_sales(self):
        """Prints daily and weekly total sales summaries."""
        if self.df is None:
            raise ValueError("Dataframe not loaded. Run load_and_clean_data() first.")

        # --- Daily sales ---
        daily_sales = self.df.groupby("Date")["Total"].sum().reset_index()
        print("\n📅 Daily Sales Summary:")
        print(daily_sales.tail(10))

        # --- Weekly sales ---
        self.df["Week"] = self.df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly_sales = self.df.groupby("Week")["Total"].sum().reset_index()

        print("\n📈 Weekly Sales Summary:")
        print(weekly_sales.tail(10))

        # Store for visualization
        self.daily_sales = daily_sales
        self.weekly_sales = weekly_sales

    def plot_sales_summary(self):
        """Plots both daily and weekly sales trends."""
        if not hasattr(self, "daily_sales") or not hasattr(self, "weekly_sales"):
            raise ValueError("Run summarize_sales() before plotting summaries.")

        # Daily sales trend
        plt.figure(figsize=(10, 5))
        plt.plot(self.daily_sales["Date"], self.daily_sales["Total"], marker='o', label="Daily Sales")
        plt.title("Daily Sales Trend")
        plt.xlabel("Date")
        plt.ylabel("Total Sales ($)")
        plt.legend()
        plt.show()

        # Weekly sales trend
        plt.figure(figsize=(10, 5))
        plt.plot(self.weekly_sales["Week"], self.weekly_sales["Total"], marker='s', color="orange", label="Weekly Sales")
        plt.title("Weekly Sales Trend")
        plt.xlabel("Week Starting")
        plt.ylabel("Total Sales ($)")
        plt.legend()
        plt.show()

    def prepare_data_for_prophet(self):
        """Prepares dataframe for Prophet model."""
        if self.df is None:
            raise ValueError("Dataframe not loaded. Run load_and_clean_data() first.")
        self.prophet_df = self.df[["Date", "Total"]].rename(columns={"Date": "ds", "Total": "y"})

    def train_model(self):
        """Initializes and fits the Prophet model."""
        if not hasattr(self, "prophet_df"):
            raise ValueError("Data not prepared. Run prepare_data_for_prophet() first.")

        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False
        )
        self.model.fit(self.prophet_df)
        print("✅ Prophet model trained successfully.")

    def make_forecast(self, days: int = 30):
        """Generates future forecast for given number of days."""
        if not isinstance(days, int) or days <= 0:
            raise TypeError("Forecast days must be a positive integer.")

        if self.model is None:
            raise ValueError("Model not trained. Run train_model() first.")

        # Forecast daily data for next N days
        future = self.model.make_future_dataframe(periods=days)
        self.forecast = self.model.predict(future)
        print(f"✅ Forecast generated for {days} future days.")

        # Add daily forecast summary
        forecast_summary = self.forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)
        print("\n🔮 Future Daily Sales Predictions:")
        print(forecast_summary)

        # Add weekly forecast summary
        self.forecast["Week"] = self.forecast["ds"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly_forecast = self.forecast.groupby("Week")[["yhat"]].mean().reset_index().tail(5)
        print("\n📆 Future Weekly Sales Predictions (Averages):")
        print(weekly_forecast)

        return self.forecast

    def plot_forecast(self):
        """Plots the forecasted values."""
        if self.forecast is None:
            raise ValueError("Forecast not generated. Run make_forecast() first.")

        self.model.plot(self.forecast)
        plt.title("Future Daily Sales Forecast")
        plt.xlabel("Date")
        plt.ylabel("Total Sales ($)")
        plt.show()


# --- Example usage ---
if __name__ == "__main__":
    forecaster = SalesForecaster("Sales Data - Sheet1.csv")
    forecaster.load_and_clean_data()
    forecaster.summarize_sales()        # ✅ daily + weekly summaries
    forecaster.plot_sales_summary()     # ✅ visualize both
    forecaster.prepare_data_for_prophet()
    forecaster.train_model()
    forecaster.make_forecast(days=30)   # ✅ show daily & weekly future forecasts
    forecaster.plot_forecast()
