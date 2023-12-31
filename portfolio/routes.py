from portfolio import app
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request, Blueprint
from portfolio.models import StocksPortfolio, User
from portfolio.forms import RegisterForm, LoginForm, AddMoney, StockPurchase
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
    total_portfolio_value = sum(stock.value for stock in current_user.portfolioItems)
    return render_template('logged_in.html', total_portfolio_value=total_portfolio_value)

@app.route('/stocks')
@app.route('/stocks/<int:page>')
def stocks_page(page=1):
    stocks_per_page = 10
    start_index = (page - 1) * stocks_per_page
    end_index = start_index + stocks_per_page
    all_stocks = get_all_stocks(start_index, end_index)

    return render_template('stocks.html', stocks=all_stocks, current_page=page)

@app.route('/buy_stock/<ticker>', methods=['GET', 'POST'])
def buy_stock(ticker):
    form = StockPurchase()
    form.ticker.data = ticker
    stock_data = yf.Ticker(ticker)
    singlePicture(ticker)
    stock_price = stock_data.info.get('regularMarketPrice', stock_data.info.get('currentPrice')) or 'N/A'
    name = stock_data.info['longName']

    if form.validate_on_submit():
        quantity = form.quantity.data

        total_cost = quantity * stock_price

        if total_cost > current_user.budget:
            flash('Insufficient funds for this stock purchase. Please try again.', 'error')
        else:
            ticker_exists = False

            for stock in current_user.portfolioItems:
                if stock.stock_symbol == ticker:
                    ticker_exists = True
                    break

            if ticker_exists:
                print('ticker in')
                changePortfolio(stock_data, quantity, stock_price, total_cost)
            else:
                print('ticker out')
                addToPortfolio(stock_data, quantity, stock_price, total_cost)

            flash(f'{name} purchased successfully!', 'success')
            return redirect(url_for('logged_in_page'))
    
    return render_template('buy_stock.html', form=form, data=stock_data)

@app.route('/search', methods=['GET'])
def search_stock():
    query = request.args.get('q', '')
    search_results = yf.Tickers(query).tickers
    filtered_results = [stock for stock in search_results if isinstance(stock, yf.Ticker) and stock.info.get('name') != 'N/A' and stock.info.get('symbol') != 'N/A' and stock.info.get('regularMarketPrice') != 'N/A']
    
    return render_template('search_results.html', query=query, results=filtered_results)

@app.route('/add-money', methods=['GET', 'POST'])
def add_money():
    form = AddMoney()
    if form.validate_on_submit():
        current_user.budget += form.amount.data
        db.session.commit()
        
        flash(f'Success! You have added {form.amount.data}$', category='success')
        return redirect(url_for('logged_in_page'))

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

        fig.write_image(file_path)
            
def get_all_stocks(start, end):
    with open('all_tickers.txt', 'r', encoding='utf-8') as f:
        ticker_symbols = [line.strip() for line in f]
        
    selected_tickers = ticker_symbols[start:end]
    
    all_stocks = []
    
    for ticker in selected_tickers:
        stock_data = yf.Ticker(ticker)
        
        stock_name = stock_data.info.get('longName', 'N/A')
        stock_symbol = stock_data.info.get('symbol', 'N/A')
        stock_price = stock_data.info.get('regularMarketPrice', stock_data.info.get('currentPrice')) or 'N/A'

        if stock_name == 'N/A' or stock_price =='N/A': continue 
        
        stock = {
            'name': stock_name,
            'symbol': stock_symbol,
            'price': stock_price
        }
        
        all_stocks.append(stock)
    
    return all_stocks

def singlePicture(ticker):
    period = '1d'
    interval = '1m'
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
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not os.path.exists(f'{dir_path}/static'):
        os.mkdir("static")
        
    file_path = os.path.join(dir_path, f'static/{ticker}.png')
    
    fig.write_image(file_path)

def addToPortfolio(stock_data, quantityToAdd, currPriceToAdd, valToAdd):
    symbol = stock_data.info.get('symbol')

    portfolio_to_add = StocksPortfolio(stock_symbol=symbol,
                                quantity=quantityToAdd,
                                current_price=currPriceToAdd,
                                value=valToAdd,
                                owner=current_user.id)
    
    current_user.budget = current_user.budget - Decimal(valToAdd)
    db.session.add(portfolio_to_add)
    db.session.commit()

def changePortfolio(stock_data, quantityToAdd, currPriceToAdd, valToAdd):

    symbol = stock_data.info.get('symbol')
    
    portfolio = StocksPortfolio.query.filter_by(stock_symbol=symbol, owner=current_user.id).first()


    portfolio.quantity += quantityToAdd
    portfolio.current_price = currPriceToAdd
    portfolio.value += Decimal(valToAdd)
    db.session.commit()

