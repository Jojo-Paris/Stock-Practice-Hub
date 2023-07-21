<h1>Stock Practice Hub - Simulated Stock Trading Platform</h1>

<p>We make trading easy. Stock Practice Hub is a way to simulate stock trading using fake money and live stock market values.</p>

<p>Stock Practice Hub is a web application that allows users to simulate stock trading using virtual money. It provides a safe and educational environment for users to practice trading stocks without risking real capital. The application is built using Python and Flask framework, with yfinance library to fetch real-time stock data and SQLAlchemy for database operations.</p>

<h2>Key Features</h2>
<ul>
    <li><strong>Simulated Stock Trading:</strong> Users can buy and sell stocks using virtual money, providing a risk-free environment for learning and practicing trading strategies.</li>
    <li><strong>Real-Time Stock Data:</strong> The application utilizes the yfinance library to fetch live stock market values, ensuring users get up-to-date information on stock prices.</li>
    <li><strong>User Authentication and Security:</strong> User passwords are securely hashed using bcrypt encryption, and Flask-Login is implemented for user authentication and authorization.</li>
    <li><strong>User-Friendly Interface:</strong> The application offers a clean and intuitive user interface, making it easy for users to navigate and interact with the platform.</li>
    <li><strong>Stock Search Functionality:</strong> Users can search for specific stock symbols to view detailed stock information.</li>
    <li><strong>Portfolio Management:</strong> Users can view their current portfolio, including the quantity and current value of each stock they own.</li>
    <li><strong>Transaction History:</strong> The application maintains a record of all stock transactions, allowing users to review their trading history.</li>
</ul>

<h2>How to Run the Application</h2>
<ol>
    <li>Clone this repository to your local machine.</li>
    <li>Set up a virtual environment and install the required dependencies from <code>requirements.txt</code>.</li>
    <li>Create a SQLite database by running <code>python create_db.py</code>.</li>
    <li>Run the application using <code>python app.py</code> and navigate to <a href="http://localhost:5000">http://localhost:5000</a> in your web browser.</li>
</ol>

<h2>Technologies Used</h2>
<ul>
    <li>Python</li>
    <li>Flask</li>
    <li>yfinance</li>
    <li>SQLAlchemy</li>
    <li>SQLite</li>
    <li>HTML</li>
    <li>CSS</li>
    <li>Bootstrap</li>
</ul>

<h2>Screenshots</h2>
<!-- Include some screenshots of the application here -->

<h2>Contributions</h2>
<p>Contributions to Stock Practice Hub are welcome! If you find any bugs or have suggestions for improvements, feel free to create an issue or submit a pull request.</p>
