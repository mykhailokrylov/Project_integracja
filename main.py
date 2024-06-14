import pandas as pd

# Wczytanie pliku Excel
support_data = pd.read_excel('Support_Ukraine.xlsx')

# Odczytanie nazw wszystkich arkuszy w pliku Excel
excel_file = pd.ExcelFile('Support_Ukraine.xlsx')
sheet_names = excel_file.sheet_names

# Wczytanie arkusza 'Bilateral Assistance, MAIN DATA'
main_data = pd.read_excel('Support_Ukraine.xlsx', sheet_name='Bilateral Assistance, MAIN DATA')

# Wyświetlenie pierwszych kilku wierszy
print(main_data.head())

# Filtracja danych dotyczących pomocy wojskowej
military_aid = main_data[main_data['Type of Aid General'] == 'Military']

# Wybrane kolumny
military_aid = military_aid[['Announcement Date', 'Converted Value in EUR']]

# Oczyszczenie dat
def clean_date(date):
    if isinstance(date, str):
        # Usunięcie tekstu z daty, np. "until 12/20/2022"
        date = date.split(',')[0].strip()
    return date

military_aid['Announcement Date'] = military_aid['Announcement Date'].apply(clean_date)

# Konwersja dat na datetime
military_aid['Announcement Date'] = pd.to_datetime(military_aid['Announcement Date'], errors='coerce')

# Usunięcie wierszy z błędnymi datami
military_aid = military_aid.dropna(subset=['Announcement Date'])

# Wyświetlenie pierwszych kilku wierszy po oczyszczeniu
print(military_aid.head())

# Wczytanie danych o terytorium
territory_data = pd.read_csv('territory.csv')
print(territory_data.head())

# Konwersja dat na datetime
territory_data['date'] = pd.to_datetime(territory_data['date'])

# Połączenie danych
merged_data = pd.merge_asof(
    territory_data.sort_values('date'),
    military_aid.sort_values('Announcement Date'),
    left_on='date',
    right_on='Announcement Date',
    direction='backward'
)

merged_data['Converted Value in EUR'] = pd.to_numeric(merged_data['Converted Value in EUR'], errors='coerce')

# Obliczenie korelacji
correlation = merged_data['Converted Value in EUR'].corr(merged_data['area'])
print(f"Correlation: {correlation}")


import matplotlib.pyplot as plt

# Create a figure and a set of subplots
fig, ax1 = plt.subplots()

# Plot 'area' on the first y-axis
ax1.plot(merged_data['date'], merged_data['area'], color='blue')
ax1.set_xlabel('Date')
ax1.set_ylabel('Area', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create a second y-axis that shares the same x-axis
ax2 = ax1.twinx()

# Plot 'Converted Value in EUR' on the second y-axis
ax2.plot(merged_data['date'], merged_data['Converted Value in EUR'], color='red')
ax2.set_ylabel('Converted Value in EUR', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Show the plot
plt.show()