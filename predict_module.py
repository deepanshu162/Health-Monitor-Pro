import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import math

class PredictModule:
    def __init__(self, db_conn):
        self.conn = db_conn
        
    def prepare_bp_data(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, time, systolic, diastolic 
            FROM bp_readings 
            WHERE user_id = ?
            ORDER BY date, time
        ''', (user_id,))
        
        data = cursor.fetchall()
        if not data:
            return None
            
        df = pd.DataFrame(data, columns=['date', 'time', 'systolic', 'diastolic'])
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df['days_since_first'] = (df['datetime'] - df['datetime'].min()).dt.days
        
        return df[['days_since_first', 'systolic', 'diastolic', 'datetime']]
        
    def prepare_bs_data(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, time, glucose_level 
            FROM bs_readings 
            WHERE user_id = ?
            ORDER BY date, time
        ''', (user_id,))
        
        data = cursor.fetchall()
        if not data:
            return None
            
        df = pd.DataFrame(data, columns=['date', 'time', 'glucose'])
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df['days_since_first'] = (df['datetime'] - df['datetime'].min()).dt.days
        
        return df[['days_since_first', 'glucose', 'datetime']]
        
    def evaluate_model(self, X, y, model_name=""):
        """Evaluate model performance using train-test split"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = math.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'model': model_name,
            'mae': round(mae, 2),
            'rmse': round(rmse, 2),
            'r2': round(r2, 2),
            'model_object': model
        }
        
    def predict_bp(self, user_id, days_ahead=7, include_visualization=False, evaluate=False):
        data = self.prepare_bp_data(user_id)
        if data is None or len(data) < 3:
            return None
            
        X = data[['days_since_first']]
        y_sys = data['systolic']
        y_dia = data['diastolic']
        
        evaluation_results = {}
        if evaluate:
            evaluation_results['systolic'] = self.evaluate_model(X, y_sys, "Systolic BP")
            evaluation_results['diastolic'] = self.evaluate_model(X, y_dia, "Diastolic BP")
            model_sys = evaluation_results['systolic']['model_object']
            model_dia = evaluation_results['diastolic']['model_object']
        else:
            model_sys = LinearRegression()
            model_dia = LinearRegression()
            model_sys.fit(X, y_sys)
            model_dia.fit(X, y_dia)
        
        # Predict for future dates
        last_day = data['days_since_first'].max()
        future_days = pd.DataFrame(range(last_day + 1, last_day + days_ahead + 1), 
                                 columns=['days_since_first'])
        
        sys_pred = model_sys.predict(future_days)
        dia_pred = model_dia.predict(future_days)
        
        # Create prediction results
        last_date = datetime.now()
        predictions = []
        for i in range(days_ahead):
            pred_date = last_date + timedelta(days=i+1)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'systolic': round(sys_pred[i]),
                'diastolic': round(dia_pred[i])
            })
        
        if include_visualization:
            visualization = self._generate_bp_visualization(data, future_days, sys_pred, dia_pred)
            if evaluate:
                return predictions, visualization, evaluation_results
            return predictions, visualization
            
        if evaluate:
            return predictions, evaluation_results
        return predictions
        
    def predict_bs(self, user_id, days_ahead=7, include_visualization=False, evaluate=False):
        data = self.prepare_bs_data(user_id)
        if data is None or len(data) < 3:
            return None
            
        X = data[['days_since_first']]
        y = data['glucose']
        
        evaluation_results = {}
        if evaluate:
            evaluation_results = self.evaluate_model(X, y, "Blood Sugar")
            model = evaluation_results['model_object']
        else:
            model = LinearRegression()
            model.fit(X, y)
        
        # Predict for future dates
        last_day = data['days_since_first'].max()
        future_days = pd.DataFrame(range(last_day + 1, last_day + days_ahead + 1), 
                                  columns=['days_since_first'])
        
        pred = model.predict(future_days)
        
        # Create prediction results
        last_date = datetime.now()
        predictions = []
        for i in range(days_ahead):
            pred_date = last_date + timedelta(days=i+1)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'glucose': round(pred[i])
            })
        
        if include_visualization:
            visualization = self._generate_bs_visualization(data, future_days, pred)
            if evaluate:
                return predictions, visualization, evaluation_results
            return predictions, visualization
            
        if evaluate:
            return predictions, evaluation_results
        return predictions
    
    def _generate_bp_visualization(self, historical_data, future_days, sys_pred, dia_pred):
        plt.figure(figsize=(12, 6))
        
        # Prepare future dates
        last_date = historical_data['datetime'].max()
        future_dates = [last_date + timedelta(days=int(days-historical_data['days_since_first'].max())) 
                       for days in future_days['days_since_first']]
        
        # Plot only predictions (no historical data)
        plt.plot(future_dates, sys_pred, 'b-o', label='Predicted Systolic')
        plt.plot(future_dates, dia_pred, 'g-o', label='Predicted Diastolic')
        
        # Formatting
        plt.title('Blood Pressure Prediction')
        plt.xlabel('Date')
        plt.ylabel('Blood Pressure (mmHg)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _generate_bs_visualization(self, historical_data, future_days, pred):
        plt.figure(figsize=(12, 6))
        
        # Prepare future dates
        last_date = historical_data['datetime'].max()
        future_dates = [last_date + timedelta(days=int(days-historical_data['days_since_first'].max())) 
                       for days in future_days['days_since_first']]
        
        # Plot only predictions (no historical data)
        plt.plot(future_dates, pred, 'r-o', label='Predicted Glucose')
        
        # Formatting
        plt.title('Blood Sugar Prediction')
        plt.xlabel('Date')
        plt.ylabel('Glucose Level (mg/dL)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _fig_to_base64(self):
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return base64.b64encode(img.getvalue()).decode('utf-8')
    
