import datetime

def get_today_date_string():
    now = datetime.datetime.now()
    dt_string = now.strftime("%Y%m%d")
    return dt_string

def get_workdir():
    date = get_today_date_string()
    workdir = "/home/kushagra/spare/local/tradingbot/{}/".format(date)
    return workdir
