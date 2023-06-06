import pandas as pd
import numpy as np
from scipy.optimize import least_squares

def train_data(s, country, start_pred_date, last_date, g1, g2):
    def get_country_data(s, country):
        return s.loc[f'{country}'].set_index('ds', drop=True).iloc[:, 0]
    s = get_country_data(s, country)

    end_pred_date = last_date
    last_actual_value = s[last_date]

    def general_logistic_shift(x, L, x0, k, v, s):
        return (L - s) / ((1 + np.exp(-k * (x - x0))) ** (1 / v)) + s

    def optimize_func(params, x, y, model):
        y_pred = model(x, *params)
        error = y - y_pred
        return error

    def get_L_limits(s, n1, n2):
        last_val = s[-1]
        last_pct = s.pct_change()[-1] + 1
        L_min = last_val * last_pct ** n1
        L_max = last_val * last_pct ** n2 + 1
        L0 = (L_max - L_min) / 2 + L_min
        if np.isnan(L_min):
            L_min, L_max, L0 = 0, 1, 0
        return L_min, L_max, L0

    def get_bounds_p0(s, n1=5, n2=60):
        L_min, L_max, L0 = get_L_limits(s, n1, n2)
        x0_min, x0_max = -50, 50
        k_min, k_max = 0.01, 0.1
        v_min, v_max = 0.01, 2
        s_min, s_max = 0, s.iloc[-1] + 0.01
        s0 = s_max / 2
        lower = L_min, x0_min, k_min, v_min, s_min
        upper = L_max, x0_max, k_max, v_max, s_max
        bounds = lower, upper
        p0 = L0, 0, 0.1, 0.1, s0
        return bounds, p0

    bounds, p0 = get_bounds_p0(s)

    def train_model(s, last_date, model, bounds, p0, **kwargs):  # creates params
        y = s.loc[start_pred_date:last_date]
        n_train = len(y)
        x = np.arange(n_train)
        res = least_squares(optimize_func, p0, args=(x, y, model), bounds=bounds, **kwargs)
        return res.x

    params = train_model(s, last_date, general_logistic_shift, bounds, p0)


    def get_daily_pred(model, params, n_train, n_pred):
        x_pred = np.arange(n_train - 1, n_train + n_pred)
        y_pred = model(x_pred, *params)
        y_pred_daily = np.diff(y_pred)
        return y_pred_daily

    n_train = len(s.loc[start_pred_date:last_date])
    y_pred_daily = get_daily_pred(general_logistic_shift, params, n_train, n_pred=100).round()

    def get_cumulative_pred(last_actual_value, y_pred_daily, last_date):
        first_pred_date = pd.Timestamp(last_date) + pd.Timedelta("1D")
        n_pred = len(y_pred_daily)
        index = pd.date_range(start=first_pred_date, periods=n_pred)
        return pd.Series(y_pred_daily.cumsum(), index=index) + last_actual_value

    def plot_pred_tail(start_pred_date, model, params, n_train1):
        """get_tail of predicted curve & training data"""
        last_actual_value = s[start_pred_date]
        x_pred = np.arange(n_train1 - 300, n_train1)
        y_pred = model(x_pred, *params)
        y_pred_daily = np.diff(y_pred)

        tail_period = len(y_pred_daily)
        tail_index = pd.date_range(start=pd.Timestamp(start_pred_date) - pd.Timedelta("300D"), periods=tail_period)
        y_adj = y_pred_daily.cumsum().max() - y_pred_daily.cumsum().min()
        y_pred_cum1=y_pred_daily.cumsum() + last_actual_value - y_adj
        return pd.Series(y_pred_cum1, index=tail_index)

    pred_curve = get_cumulative_pred(last_actual_value, y_pred_daily, last_date)
    tail = plot_pred_tail(end_pred_date, general_logistic_shift, params, len(s.loc[start_pred_date:last_date])).round()

    return pred_curve, tail
