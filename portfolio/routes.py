from portfolio import app
from flask import render_template, redirect, url_for, flash
from portfolio.models import StocksPortfolio, User
from portfolio.forms import RegisterForm, LoginForm
from portfolio import db
from flask_login import login_user, logout_user, login_required
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns; sns.set()
matplotlib.use("agg")
import os

@app.route("/")
@app.route("/home")
def home_page():
    tickers = ['AAPL', 'GOOGL', 'OPK']
    createPicture(tickers)
    return render_template('home.html', tickers=tickers)

@app.route("/register", methods=['POST', 'GET'])
def register_page():

    form = RegisterForm()
    if form.validate_on_submit():
        print('inside')

        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

def get_closing_prices(symbol, period):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period)
    return data["Close"]

def createPicture(tickerList):
    period = "5y"
    for ticker in tickerList:
        prices_data = get_closing_prices(ticker, period)

        sns.set_theme(style="darkgrid")
        plt.figure(figsize=(10, 6))

        sns.lineplot(data=prices_data, linewidth=2, color="blue")
        plt.xticks(rotation=30)
        plt.title(f"Closing Stock Prices for {ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, f'static/{ticker}.png')
        plt.savefig(file_path)