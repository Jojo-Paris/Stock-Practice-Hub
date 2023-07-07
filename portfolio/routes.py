from portfolio import app
from flask import render_template, redirect, url_for, flash, request
from portfolio.models import StocksPortfolio, User
from portfolio.forms import RegisterForm, LoginForm, AddMoney
from portfolio import db
from flask_login import login_user, logout_user, login_required, current_user
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns; sns.set()
import numpy as np
import pandas as pd
matplotlib.use("agg")
import os
import plotly.graph_objs as go


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
        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('logged_in_page'))
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
            return redirect(url_for('logged_in_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/logged-in-home')
def logged_in_page():
    return render_template('logged_in.html')

@app.route('/add-money', methods=['GET', 'POST'])
def add_money():
    form = AddMoney()
    if form.validate_on_submit():
        current_user.budget += form.amount.data
        db.session.commit()
        
        print(current_user.budget)
        flash(f'Success! You are have added {form.amount.data}', category='success')
        return redirect(url_for('logged_in_page'))
    else:
        flash('Amount not valid. Please try again.', category='danger')

    return render_template('add_money.html', form=form)

def get_closing_prices(symbol, periodIn, intervalIn):
    return yf.download(tickers=f'{symbol}', period=f'{periodIn}', interval=f'{intervalIn}')

def createPicture(tickerList):

    period = '1d'
    interval = '1m'
    for ticker in tickerList:
        fig = fig = go.Figure()
        prices_data = get_closing_prices(ticker, period, interval)

        fig.add_trace(go.Candlestick(x=prices_data.index,
                open=prices_data['Open'],
                high=prices_data['High'],
                low=prices_data['Low'],
                close=prices_data['Close'], name = 'market data'))
        
        company_name = yf.Ticker(ticker)
        company_name = company_name.info['longName']

        fig.update_layout(
        title=f'{company_name} live share price evolution',
        yaxis_title='Stock Price (USD per Shares)')

        
        
        fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="HTD", step="hour", stepmode="todate"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(step="all")
                ])
            )
        )
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(f'{dir_path}/static'):
            os.mkdir("static")
        
        file_path = os.path.join(dir_path, f'static/{ticker}.png')

        if os.path.exists(file_path):
            continue
        else:
            fig.write_image(file_path)
            



    
