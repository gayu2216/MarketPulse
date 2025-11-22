import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Dict, Any
from werkzeug.utils import secure_filename

from src.controllers.input_controller import SalesForecaster

# Set seaborn style
sns.set_style("whitegrid")
sns.set_palette("husl")


class SalesDataController:
    """Controller for handling sales data uploads and processing."""

    def __init__(self, upload_folder: Optional[str] = None, graphs_folder: Optional[str] = None):
        if upload_folder:
            self.upload_folder = Path(upload_folder)
        else:
            self.upload_folder = Path(os.getcwd()) / "src" / "data" / "uploads"
        
        if graphs_folder:
            self.graphs_folder = Path(graphs_folder)
        else:
            self.graphs_folder = Path(os.getcwd()) / "src" / "data" / "graphs"
        
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        self.graphs_folder.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {'csv'}

    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_uploaded_file(self, file, username: str) -> Optional[str]:
        """
        Save uploaded file to the uploads directory.
        Returns the file path if successful, None otherwise.
        """
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        if not self._is_allowed_file(file.filename):
            raise ValueError("Only CSV files are allowed")
        
        # Create secure filename
        filename = secure_filename(file.filename)
        # Add username prefix to avoid conflicts
        safe_username = secure_filename(username)
        user_folder = self.upload_folder / safe_username
        user_folder.mkdir(parents=True, exist_ok=True)
        
        file_path = user_folder / filename
        file.save(str(file_path))
        
        return str(file_path)

    def generate_graphs(self, forecaster: SalesForecaster, username: str) -> Dict[str, str]:
        """
        Generate seaborn graphs for sales data and save them as images.
        Returns a dictionary with graph file paths.
        """
        safe_username = secure_filename(username)
        user_graphs_folder = self.graphs_folder / safe_username
        user_graphs_folder.mkdir(parents=True, exist_ok=True)
        
        graph_paths = {}
        
        # Daily Sales Trend Graph
        plt.figure(figsize=(12, 6))
        daily_df = forecaster.daily_sales.copy()
        daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        sns.lineplot(data=daily_df, x='Date', y='Total', marker='o', linewidth=2, markersize=6)
        plt.title('Daily Sales Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Total Sales ($)', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        daily_graph_path = user_graphs_folder / 'daily_sales.png'
        plt.savefig(daily_graph_path, dpi=100, bbox_inches='tight')
        plt.close()
        graph_paths['daily_sales'] = f"{safe_username}/daily_sales.png"
        
        # Weekly Sales Trend Graph
        plt.figure(figsize=(12, 6))
        weekly_df = forecaster.weekly_sales.copy()
        weekly_df['Week'] = pd.to_datetime(weekly_df['Week'])
        sns.lineplot(data=weekly_df, x='Week', y='Total', marker='s', linewidth=2, markersize=8, color='#ff6b6b')
        plt.title('Weekly Sales Trend', fontsize=16, fontweight='bold')
        plt.xlabel('Week Starting', fontsize=12)
        plt.ylabel('Total Sales ($)', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        weekly_graph_path = user_graphs_folder / 'weekly_sales.png'
        plt.savefig(weekly_graph_path, dpi=100, bbox_inches='tight')
        plt.close()
        graph_paths['weekly_sales'] = f"{safe_username}/weekly_sales.png"
        
        # Forecast Graph
        if hasattr(forecaster, 'forecast') and forecaster.forecast is not None:
            plt.figure(figsize=(14, 7))
            forecast_df = forecaster.forecast.copy()
            forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
            
            # Plot historical data
            historical = forecast_df[forecast_df['ds'] <= forecast_df['ds'].max() - pd.Timedelta(days=30)]
            sns.lineplot(data=historical, x='ds', y='yhat', label='Historical', linewidth=2, color='#4ecdc4')
            
            # Plot forecast
            future = forecast_df[forecast_df['ds'] > forecast_df['ds'].max() - pd.Timedelta(days=30)]
            sns.lineplot(data=future, x='ds', y='yhat', label='Forecast', linewidth=2, color='#ff6b6b', linestyle='--')
            
            # Plot confidence intervals
            plt.fill_between(future['ds'], future['yhat_lower'], future['yhat_upper'], 
                           alpha=0.3, color='#ff6b6b', label='Confidence Interval')
            
            plt.title('Sales Forecast with Confidence Intervals', fontsize=16, fontweight='bold')
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Total Sales ($)', fontsize=12)
            plt.legend(fontsize=10)
            plt.xticks(rotation=45)
            plt.tight_layout()
            forecast_graph_path = user_graphs_folder / 'forecast.png'
            plt.savefig(forecast_graph_path, dpi=100, bbox_inches='tight')
            plt.close()
            graph_paths['forecast'] = f"{safe_username}/forecast.png"
        
        # Sales Distribution Graph
        plt.figure(figsize=(10, 6))
        daily_df = forecaster.daily_sales.copy()
        sns.histplot(data=daily_df, x='Total', bins=20, kde=True, color='#95e1d3')
        plt.title('Daily Sales Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Total Sales ($)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        distribution_graph_path = user_graphs_folder / 'distribution.png'
        plt.savefig(distribution_graph_path, dpi=100, bbox_inches='tight')
        plt.close()
        graph_paths['distribution'] = f"{safe_username}/distribution.png"
        
        return graph_paths

    def process_sales_data(self, file_path: str, username: str = None) -> Dict[str, Any]:
        """
        Process sales data from CSV file and return summaries.
        Returns a dictionary with daily sales, weekly sales, forecast data, and graph paths.
        """
        try:
            forecaster = SalesForecaster(file_path)
            forecaster.load_and_clean_data()
            forecaster.summarize_sales()
            forecaster.prepare_data_for_prophet()
            forecaster.train_model()
            forecast = forecaster.make_forecast(days=30)
            
            # Generate graphs if username is provided
            graph_paths = {}
            if username:
                graph_paths = self.generate_graphs(forecaster, username)
            
            # Convert to JSON-serializable format
            daily_sales = forecaster.daily_sales.copy()
            daily_sales['Date'] = daily_sales['Date'].dt.strftime('%Y-%m-%d')
            
            weekly_sales = forecaster.weekly_sales.copy()
            weekly_sales['Week'] = weekly_sales['Week'].dt.strftime('%Y-%m-%d')
            
            # Get forecast summary (last 30 days)
            forecast_summary = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30).copy()
            forecast_summary['ds'] = forecast_summary['ds'].dt.strftime('%Y-%m-%d')
            
            # Calculate statistics
            total_sales = daily_sales['Total'].sum()
            avg_daily_sales = daily_sales['Total'].mean()
            max_daily_sales = daily_sales['Total'].max()
            min_daily_sales = daily_sales['Total'].min()
            
            return {
                'success': True,
                'daily_sales': daily_sales.to_dict('records'),
                'weekly_sales': weekly_sales.to_dict('records'),
                'forecast': forecast_summary.to_dict('records'),
                'graph_paths': graph_paths,
                'statistics': {
                    'total_sales': float(total_sales),
                    'avg_daily_sales': float(avg_daily_sales),
                    'max_daily_sales': float(max_daily_sales),
                    'min_daily_sales': float(min_daily_sales),
                    'total_days': len(daily_sales)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_uploaded_files(self, username: str) -> list:
        """Get list of files uploaded by a user."""
        safe_username = secure_filename(username)
        user_folder = self.upload_folder / safe_username
        
        if not user_folder.exists():
            return []
        
        files = []
        for file_path in user_folder.glob('*.csv'):
            files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size
            })
        
        return files

