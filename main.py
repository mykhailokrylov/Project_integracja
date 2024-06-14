import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie pliku Excel
support_data = pd.read_excel('Support_Ukraine.xlsx')

# Odczytanie nazw wszystkich arkuszy w pliku Excel
excel_file = pd.ExcelFile('Support_Ukraine.xlsx')
sheet_names = excel_file.sheet_names

# Wczytanie arkusza 'Bilateral Assistance, MAIN DATA'
main_data = pd.read_excel('Support_Ukraine.xlsx', sheet_name='Bilateral Assistance, MAIN DATA')

# Filtracja danych dotyczących pomocy wojskowej
military_aid = main_data[main_data['Type of Aid General'] == 'Military']

# Wybrane kolumny
military_aid = military_aid[['Announcement Date', 'Converted Value in EUR']]

# Oczyszczenie dat
def clean_date(date):
    if isinstance(date, str):
        date = date.split(',')[0].strip()
    return date

military_aid['Announcement Date'] = military_aid['Announcement Date'].apply(clean_date)

# Konwersja dat na datetime
military_aid['Announcement Date'] = pd.to_datetime(military_aid['Announcement Date'], errors='coerce')

# Usunięcie wierszy z błędnymi datami
military_aid = military_aid.dropna(subset=['Announcement Date'])

# Konwersja wartości na numeryczne
military_aid['Converted Value in EUR'] = pd.to_numeric(military_aid['Converted Value in EUR'], errors='coerce')

# Grupa po 'Announcement Date' i obliczenie sumy dziennej
daily_sum = military_aid.groupby('Announcement Date')['Converted Value in EUR'].sum().reset_index()

# Obliczenie skumulowanej sumy
daily_sum['Cumulative Value in EUR'] = daily_sum['Converted Value in EUR'].cumsum()

# Wczytanie danych o terytorium
territory_data = pd.read_csv('territory.csv')

# Konwersja dat na datetime
territory_data['date'] = pd.to_datetime(territory_data['date'])

# Połączenie danych
merged_data = pd.merge_asof(
    territory_data.sort_values('date'),
    daily_sum.sort_values('Announcement Date'),
    left_on='date',
    right_on='Announcement Date',
    direction='backward'
)

# Wprowadzenie opóźnienia (lag) dla skumulowanej wartości w EUR
lag_days = 7
merged_data['Lagged Cumulative Value in EUR'] = merged_data['Cumulative Value in EUR'].shift(lag_days)

# Usunięcie wierszy z brakującymi wartościami
merged_data = merged_data.dropna(subset=['Lagged Cumulative Value in EUR'])

# Wygładzenie danych o terytorium
merged_data['Smoothed Area'] = merged_data['area'].rolling(window=7).mean()

# Obliczenie korelacji
correlation = merged_data['Lagged Cumulative Value in EUR'].corr(merged_data['Smoothed Area'])
print(f"Correlation: {correlation}")

# Create a figure and a set of subplots
fig, ax1 = plt.subplots()

# Plot 'Smoothed Area' on the first y-axis
ax1.plot(merged_data['date'], merged_data['Smoothed Area'], color='blue')
ax1.set_xlabel('Date')
ax1.set_ylabel('Area (Smoothed)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create a second y-axis that shares the same x-axis
ax2 = ax1.twinx()

# Plot 'Lagged Cumulative Value in EUR' on the second y-axis with a solid line
ax2.plot(merged_data['date'], merged_data['Lagged Cumulative Value in EUR'], color='red', linestyle='-')
ax2.set_ylabel('Lagged Cumulative Value in EUR', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Show the plot
plt.show()
