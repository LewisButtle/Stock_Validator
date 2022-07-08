# based on: https://en.wikipedia.org/wiki/Ordinary_least_squares

import numpy as np
from scipy import stats
import pandas as pd
from .models import CurrencyValues, DerivativeTrades
import math
from datetime import date, timedelta

def error_check(possible_values, numpad):
    if numpad:
        key_miss = [[1, 2],
                    [0, 2, 4],
                    [0, 1, 3, 5],
                    [2, 6],
                    [1, 5, 7],
                    [2, 4, 6, 8],
                    [3, 5, 9],
                    [4, 8],
                    [5, 7, 9],
                    [6, 8]]
    else:
        key_miss = [[9],
                    [2],
                    [1, 3],
                    [2, 4],
                    [3, 5],
                    [4, 6],
                    [5, 7],
                    [6, 8],
                    [7, 9],
                    [8, 0]]

    value = possible_values[0]
    value_str = str(value)

    possible_values.append(float(value // 10.0))
    possible_values.append(value * 10.0)

    for i in range(len(value_str)):
        if value_str[i] != '.':
            for correction in key_miss[int(value_str[i])]:
                correction_str = value_str[:i] + str(correction) + value_str[i + 1:]
                if float(correction_str) not in possible_values:
                    possible_values.append(float(correction_str))

    for i in range(1, len(value_str)):
        if value_str[i-1:i] == value_str[i:i+1]:
            cut = float(value_str[:i] + value_str[i+1:])
            add = float(value_str[:i+1] + value_str[i:])
            if cut not in possible_values:
                possible_values.append(cut)
            if add not in possible_values:
                possible_values.append(add)


def generate_possible_values(value):
    possible_values = [float(value)]
    error_check(possible_values, False)
    return possible_values

# Storing 6 variables for OLS model:
# P - 2x2 matrix -> 4 variables
# q - vector of length 2 -> 2 variables

def generate_models(selling_party, product, trade_date):
    query_set = DerivativeTrades.objects.filter(product=product, sellingParty=selling_party,
                                                dateOfTrade__gte=(trade_date-timedelta(days=365)).date(),
                                                dateOfTrade__lte=trade_date.date())
    trade_values = query_set.values('dateOfTrade', 'notionalCurrency', 'strikePrice', 'quantity')
    trade_df = pd.DataFrame.from_records(trade_values)
    trade_df['dateOfTrade'] = trade_df['dateOfTrade'].apply(lambda x: (x.date() - date(2010, 1, 1)).days)
    currency_values = CurrencyValues.objects.filter(date__gte=(trade_date-timedelta(days=365)).date(),
                                                    date__lte=trade_date.date()) \
        .values('date', 'currency', 'valueInUSD')
    currency_df = pd.DataFrame.from_records(currency_values)
    currency_df['date'] = currency_df['date'].apply(lambda x: (x - date(2010, 1, 1)).days)
    df = trade_df.merge(currency_df, 'left', left_on=['dateOfTrade', 'notionalCurrency'],
                        right_on=['date', 'currency'])
    df['strikePriceInUSD'] = df['strikePrice'].apply(lambda x: float(x)) / df['valueInUSD'].apply(lambda x: float(x))
    dates = df['dateOfTrade'].to_numpy()
    strike_prices = df['strikePriceInUSD'].to_numpy()
    quantities = df['quantity'].to_numpy()

    pg, pi, _, _, _ = stats.linregress(dates[~np.isnan(strike_prices)], strike_prices[~np.isnan(strike_prices)])
    qg, qi, _, _, _ = stats.linregress(dates, quantities)

    expected_prices = df['dateOfTrade'].apply(lambda x: pi+(pg*x))
    expected_quantities = df['dateOfTrade'].apply(lambda x: qi+(qg*x))

    price_residuals = (expected_prices.subtract(strike_prices)).apply(lambda x: x**2)
    quantity_residuals = (expected_quantities.subtract(quantities)).apply(lambda x: x**2)

    psd = math.sqrt(np.sum(price_residuals) / (price_residuals.size-2))
    qsd = math.sqrt(np.sum(quantity_residuals) / (quantity_residuals.size-2))

    return pi, pg, psd, qi, qg, qsd

def check_data(selling_party, product, quantity, price, trade_date, notional_currency_value):
    pi, pg, psd, qi, qg, qsd = generate_models(selling_party, product, trade_date)
    # Days since 1 Jan 2010
    days = (trade_date.date() - date(2010, 1, 1)).days
    print("------------------------------------------------")
    # Calculate expected values from linear regression models
    expected_price = pi + (pg * days)
    print("Price: "+str(price))
    print("Expected Price: "+str(expected_price))
    print("    Price S.D.: "+str(psd))
    expected_quantity = qi + (qg * days) # Expected quantity
    print("Expected Quantity: "+str(int(expected_quantity)))
    print("    Quantity S.D.: "+str(int(qsd)))
    print("------------------------------------------------")
    # The values to be returned
    return_prices = []
    return_quantities = []

    possible_prices = []
    possible_quantities = []

    price_response_type = 0
    quantity_response_type = 0

    # If the price is outside of three standard deviations
    if price < expected_price - 3*psd or price > expected_price + 3*psd:
        price_response_type = 3  # At least 3 standard deviations from the expected value. Correct and notify
        # Run auto correction and notify user of changes
        possible_values = generate_possible_values(round(price/notional_currency_value,2))
        for value in possible_values:
            if expected_price - 2 * psd < (value*notional_currency_value) < expected_price + 2 * psd:
                possible_prices.append(value)
        if len(possible_prices) > 0:
            return_prices.append(min(possible_prices, key=lambda x: abs(x-expected_price)))

    # If the price is outside of two standard deviations
    elif price < expected_price - 2*psd or price > expected_price + 2*psd:
        price_response_type = 2  # Between 2 and 3 standard deviations from the expected value. Query and suggest
        # Ask the user to make sure the data is correct and give best suggestion
        possible_values = generate_possible_values(round(price/notional_currency_value,2))
        for value in possible_values:
            if expected_price - 2 * psd < (value*notional_currency_value) < expected_price + 2 * psd:
                return_prices.append(value)
        print(return_prices)
    # Else the price is within an acceptable range

    # If the quantity is outside of three standard deviations
    if quantity < expected_quantity - 3 * qsd or quantity > expected_quantity + 3 * qsd:
        quantity_response_type = 3  # At least 3 standard deviations from the expected value. Correct and notify
        # Run auto correction and notify user of changes
        possible_values = generate_possible_values(quantity)
        for value in possible_values:
            if expected_quantity - 2 * qsd < value < expected_quantity + 2 * qsd:
                possible_quantities.append(int(value))
        if len(possible_quantities) > 0:
            return_quantities.append(int(min(possible_quantities, key=lambda x: abs(x - expected_quantity))))

    # If the quantity is outside of two standard deviations
    elif quantity < expected_quantity - 2 * qsd or quantity > expected_quantity + 2 * qsd:
        quantity_response_type = 2  # Between 2 and 3 standard deviations from the expected value. Query and suggest
        # Ask the user to make sure the data is correct and give best suggestion
        possible_values = generate_possible_values(quantity)
        for value in possible_values:
            if expected_quantity - 2 * qsd < value < expected_quantity + 2 * qsd:
                return_quantities.append(int(value))

    # Else the quantity is within an acceptable range

    return return_prices, price_response_type, return_quantities, quantity_response_type

# P, q as defined in http://ee263.stanford.edu/lectures/recursive.pdf
def recursive_least_squares(P_old, q_old, a_new, y_new):
    P_new = np.add(P_old, np.outer(a_new, a_new))
    q_new = np.add(q_old, np.multiply(y_new, a_new))
    return P_new, q_new

# prediction function for a new observation a = (1, x)
# x is the explanatory variable
# we return y_pred the predicted value of the response variable y
def simple_linreg_predict(a, P, q):
    par = np.round(np.matmul(np.linalg.inv(P), q), 5)
    y_pred = np.dot(a, par)
    return y_pred

# Storing 2 variables for regression standard error:
# SSR - the sum of squared errors
# count - the number of available observations

# returns the new parameters for regression standard error for storage:
def new_s_error_param(SSR_old, old_n, y_real, y_pred):
    SSR_new = SSR_old + (y_real - y_pred)**2
    new_n = old_n + 1
    return SSR_new, new_n

def s_error(SSR, n):
    return math.sqrt(SSR/(n-2))

