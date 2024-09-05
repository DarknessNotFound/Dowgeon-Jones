import time

MONTH_NAMES = {
    1: "Joales",
    2: "Brasalt",
    3: "Stonuary",
    4: "Dremuary",
    5: "Solany",
    6: "Stribolk",
    7: "Gravent",
    8: "Hills",
    9: "Lunaray",
    10: "Octember",
    11: "Kerrack"
}

DAY_OF_WEEK_NAMES = {
    1: "Fanarday",
    2: "Fezurday",
    3: "Fiestday",
    4: "Folorday",
    5: "Fugoday",
}

WEEKS_PER_MONTH = {
    1: 6,
    2: 6,
    3: 4,
    4: 8,
    5: 11,
    6: 4,
    7: 6,
    8: 8,
    9: 6,
    10: 7,
    11: 7
}

SECONDS_PER_IN_GAME_DAY = 17280 # (60*60*24) / 5
STARTING_YEAR = 1000
NUM_MONTHS_IN_YEAR = 11
NUM_DAYS_IN_WEEK = 5

def WeekOfYear(epoch: float) -> int:
    return DayOfYear(epoch) // 5

def DayOfYear(epoch: float) -> int:
    return int(epoch // SECONDS_PER_IN_GAME_DAY) % 365

def DayOfWeek(epoch: float) -> int:
    return (DayOfYear(epoch) % NUM_DAYS_IN_WEEK) + 1

def DayOfMonth(epoch: float) -> int:
    day_of_month = 1
    month = 1
    month_day_max = WEEKS_PER_MONTH[month] * NUM_DAYS_IN_WEEK
    day_of_year = DayOfYear(epoch)

    for i in range(1, day_of_year+1):
        if day_of_month == month_day_max:
            day_of_month = 0
            month += 1
            month_day_max = WEEKS_PER_MONTH[month] * NUM_DAYS_IN_WEEK

        day_of_month += 1
    return day_of_month

def CurrentYear(epoch: float) -> int:
    return STARTING_YEAR + (int(epoch // SECONDS_PER_IN_GAME_DAY) // 365)

def CurrentHour(epoch: float) -> int:
    return int(((epoch / SECONDS_PER_IN_GAME_DAY) - int(epoch // SECONDS_PER_IN_GAME_DAY)) * 24)

def CurrentMinute(epoch: float) -> int:
    return int(((epoch / SECONDS_PER_IN_GAME_DAY) - int(epoch // SECONDS_PER_IN_GAME_DAY)) * 24 * 60 % 60)

def CurrentSecond(epoch: float) -> int:
    return int(((epoch / SECONDS_PER_IN_GAME_DAY) - int(epoch // SECONDS_PER_IN_GAME_DAY)) * 24 * 60 * 60 % 60)

def MonthFromWeekOfYear(week_num: int) -> int:
    week_count = 0
    for month in range(1, NUM_MONTHS_IN_YEAR + 1):
        num_weeks = WEEKS_PER_MONTH[month]
        week_count  += num_weeks
        if week_num <= week_count:
            return month
    return -1

def CurrentMonth(epoch: float) -> int:
    return MonthFromWeekOfYear(WeekOfYear(epoch))

def DayPostScript(x: int) -> int:
    if x % 10 == 1:
        result = "st"
        if x == 11:
            result = "th"
    elif x % 10 == 2:
        result = "nd"
        if x == 12:
            result = "th"
    elif x % 10 == 3:
        result = "rd"
        if x == 1:
            result = "th"
    else:
        result = "th"

    return result

def PrettyPrintDate(epoch: float, text: bool = True) -> str:
    day_of_week = DayOfWeek(epoch)
    day_of_month = DayOfMonth(epoch)
    month = CurrentMonth(epoch)
    year = CurrentYear(epoch)

    if text:
        return f"{DAY_OF_WEEK_NAMES[day_of_week]}, {day_of_month}{DayPostScript(day_of_month)} of {MONTH_NAMES[month]}, {year}"
    else:
        hour = CurrentHour(epoch)
        minute = CurrentMinute(epoch)
        second = CurrentSecond(epoch)
        return f"{year}/{month}/{day_of_month} -- {hour:02d}:{minute:02d}:{second:02d}"

if __name__=="__main__":
    epoch_time = time.time()
    print(f"Day of Year: {DayOfYear(epoch_time)}")
    print(f"Week of Year: {WeekOfYear(epoch_time)}")
    print(f"Current Year: {CurrentYear(epoch_time)}")
    print(f"Current Month: {MonthFromWeekOfYear(WeekOfYear(epoch_time))}")
    print(f"Current Day of Week: {DayOfWeek(epoch_time)}")
    print(f"Pretty Print: {PrettyPrintDate(epoch_time)}")