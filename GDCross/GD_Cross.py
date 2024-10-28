from flask import Flask, request, render_template, jsonify
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

app = Flask(__name__)

# Replace with your actual Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = "your key here"

def get_alpha_vantage_data(function, symbol, interval, time_period, series_type):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def plot_moving_average(symbol, ma_5_data, ma_20_data, ma_type):
    # Use a custom style for a dark theme
    plt.style.use('dark_background')

    # Get today's date and date 6 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6*30)  # Approximate 6 months

    # Filter data for the last 6 months
    dates_5 = [datetime.strptime(date, '%Y-%m-%d') for date in ma_5_data.keys() if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date]
    dates_20 = [datetime.strptime(date, '%Y-%m-%d') for date in ma_20_data.keys() if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date]

    common_dates = sorted(set(dates_5) & set(dates_20))

    ma_5 = [float(ma_5_data[date.strftime('%Y-%m-%d')][ma_type]) for date in common_dates]
    ma_20 = [float(ma_20_data[date.strftime('%Y-%m-%d')][ma_type]) for date in common_dates]

    # Detect golden crosses and death crosses
    crosses = []
    for i in range(1, len(common_dates)):
        if ma_5[i] > ma_20[i] and ma_5[i-1] <= ma_20[i-1]:
            crosses.append((common_dates[i], 'Golden Cross', ma_5[i], ma_20[i]))
        elif ma_5[i] < ma_20[i] and ma_5[i-1] >= ma_20[i-1]:
            crosses.append((common_dates[i], 'Death Cross', ma_5[i], ma_20[i]))

    # Sort crosses by date
    crosses.sort()

    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot the moving averages
    ax.plot(common_dates, ma_5, label='5-day ' + ma_type, color='#00bfff', linewidth=2)
    ax.plot(common_dates, ma_20, label='20-day ' + ma_type, color='#ff6347', linewidth=2)

    # Add markers for crosses
    for date, cross_type, ma_5_value, ma_20_value in crosses:
        if cross_type == 'Golden Cross':
            ax.scatter(date, ma_5_value, color='gold', edgecolor='black', linewidth=1.5, s=100, zorder=5, label='Golden Cross')
        else:
            ax.scatter(date, ma_5_value, color='red', edgecolor='black', linewidth=1.5, s=100, zorder=5, label='Death Cross')

    # Customize the legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize='large')

    # Customize the grid and background
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='#666666')
    ax.set_facecolor('#121212')

    # Customize the labels and title
    ax.set_xlabel('Date', fontsize=14, color='#00bfff')
    ax.set_ylabel(ma_type + ' Value', fontsize=14, color='#00bfff')
    plt.xticks(rotation=45, color='#00bfff')
    plt.yticks(color='#00bfff')

    # Set X-axis to display only monthly labels
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Add glowing effect to title
    glow_color = '#00bfff'
    title_text = f'5-day vs 20-day {ma_type} for {symbol}'
    for offset in range(1, 6):
        ax.text(0.5, 1.05, title_text, transform=ax.transAxes, ha='center', va='top', fontsize=18, weight='bold', color=glow_color, alpha=0.2/offset)
    ax.text(0.5, 1.05, title_text, transform=ax.transAxes, ha='center', va='top', fontsize=18, weight='bold', color='white')

    # Tighten layout
    plt.tight_layout()

    # Save plot as an image
    image_path = f'static/images/{symbol}_{ma_type.lower()}.png'
    plt.savefig(image_path, dpi=300)
    plt.close()
    return image_path, crosses

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/resource')
def resource():
    return render_template('resource.html')

@app.route('/try-model')
def try_model():
    return render_template('try-model.html')

@app.route('/run-model', methods=['POST'])
def run_model():
    ticker = request.form.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    ticker = ticker.upper()

    sma_data_5 = get_alpha_vantage_data("SMA", ticker, "daily", "5", "close")
    sma_data_20 = get_alpha_vantage_data("SMA", ticker, "daily", "20", "close")
    tema_data_5 = get_alpha_vantage_data("TEMA", ticker, "daily", "5", "close")
    tema_data_20 = get_alpha_vantage_data("TEMA", ticker, "daily", "20", "close")
    ema_data_5 = get_alpha_vantage_data("EMA", ticker, "daily", "5", "close")
    ema_data_20 = get_alpha_vantage_data("EMA", ticker, "daily", "20", "close")
    wma_data_5 = get_alpha_vantage_data("WMA", ticker, "daily", "5", "close")
    wma_data_20 = get_alpha_vantage_data("WMA", ticker, "daily", "20", "close")
    dema_data_5 = get_alpha_vantage_data("DEMA", ticker, "daily", "5", "close")
    dema_data_20 = get_alpha_vantage_data("DEMA", ticker, "daily", "20", "close")

    if "Technical Analysis: SMA" not in sma_data_5 or "Technical Analysis: SMA" not in sma_data_20:
        return jsonify({"error": "Failed to retrieve SMA data"}), 500

    if "Technical Analysis: TEMA" not in tema_data_5 or "Technical Analysis: TEMA" not in tema_data_20:
        return jsonify({"error": "Failed to retrieve TEMA data"}), 500

    if "Technical Analysis: EMA" not in ema_data_5 or "Technical Analysis: EMA" not in ema_data_20:
        return jsonify({"error": "Failed to retrieve EMA data"}), 500

    if "Technical Analysis: WMA" not in wma_data_5 or "Technical Analysis: WMA" not in wma_data_20:
        return jsonify({"error": "Failed to retrieve WMA data"}), 500

    if "Technical Analysis: DEMA" not in dema_data_5 or "Technical Analysis: DEMA" not in dema_data_20:
        return jsonify({"error": "Failed to retrieve DEMA data"}), 500

    sma_5_data = sma_data_5["Technical Analysis: SMA"]
    sma_20_data = sma_data_20["Technical Analysis: SMA"]
    tema_5_data = tema_data_5["Technical Analysis: TEMA"]
    tema_20_data = tema_data_20["Technical Analysis: TEMA"]
    ema_5_data = ema_data_5["Technical Analysis: EMA"]
    ema_20_data = ema_data_20["Technical Analysis: EMA"]
    wma_5_data = wma_data_5["Technical Analysis: WMA"]
    wma_20_data = wma_data_20["Technical Analysis: WMA"]
    dema_5_data = dema_data_5["Technical Analysis: DEMA"]
    dema_20_data = dema_data_20["Technical Analysis: DEMA"]

    sma_image_path, sma_crosses = plot_moving_average(ticker, sma_5_data, sma_20_data, 'SMA')
    tema_image_path, tema_crosses = plot_moving_average(ticker, tema_5_data, tema_20_data, 'TEMA')
    ema_image_path, ema_crosses = plot_moving_average(ticker, ema_5_data, ema_20_data, 'EMA')
    wma_image_path, wma_crosses = plot_moving_average(ticker, wma_5_data, wma_20_data, 'WMA')
    dema_image_path, dema_crosses = plot_moving_average(ticker, dema_5_data, dema_20_data, 'DEMA')

    return render_template('run-model.html', ticker=ticker, sma_image_path=sma_image_path, sma_crosses=sma_crosses, tema_image_path=tema_image_path, tema_crosses=tema_crosses, ema_image_path=ema_image_path, ema_crosses=ema_crosses, wma_image_path=wma_image_path, wma_crosses=wma_crosses, dema_image_path=dema_image_path, dema_crosses=dema_crosses)

if __name__ == '__main__':
    if not os.path.exists('static/images'):
        os.makedirs('static/images')
    app.run(debug=True)









