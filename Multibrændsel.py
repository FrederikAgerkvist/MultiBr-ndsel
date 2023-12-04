import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table
from datetime import datetime
import csv


# start_date = '2023-10-01T00:00'
# end_date = '2023-11-01T00:00'

start_date = '2023-10-15T00:00'
end_date = '2023-11-01T00:00'

minimumRunTime = 2 # 1-24 hr
efficiencyElectricity = 1 # 0-1
efficiencyGas = 0.8 # 0-1
efficiencyOil = 1 # 0-1


# oilConversionRate = 10 #1L == 10kWh
# oilAmount = 10000 # In L
# oilPrice = 12700
# oilPriceLtr = oilAmount/oilPrice # DKK pr. L

# Gas spot prices API request
GasSpotPrices = requests.get(f'https://api.energidataservice.dk/dataset/GasDailyBalancingPrice?offset=0&start={start_date}&end={end_date}&sort=GasDay%20DESC').json().get('records', [])

# Electricity spot prices API request
ElSpotPrices = requests.get(f'https://api.energidataservice.dk/dataset/Elspotprices?offset=0&start={start_date}&end={end_date}&sort=HourDK&filter={{"PriceArea":["DK1"]}}').json().get('records', [])

lavLast = 0.0652
højLast = 0.1957
spidsLast = 0.587

# 1L Oil == 10 kWh --> devide by 10 since you get 10 kWh pr purchased ltr oil.
# effective_oil_price = (oilPriceLtr / 10) / efficiencyOil

matrix = []

header_row = ['']
mixedUsagePriceTotal = []


elSpot = []

dayCounter = 0

for electricity_entry in ElSpotPrices:
    elSpot.append(electricity_entry['SpotPriceDKK'] / 1000)
    
    

print(sum(elSpot) / len(elSpot))

"""
for gas_entry in GasSpotPrices:
    gas_entry_date = datetime.strptime(gas_entry['GasDay'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

    filtered_electricity_entries = [electricity_entry for electricity_entry in ElSpotPrices if electricity_entry['HourDK'].startswith(gas_entry_date)]

    matrix_row = [gas_entry_date]
    minimumRunTimeCounter = 0
    ElectricitySpotPriceList = []
    startEndTimeList = []
    mixedUsagePriceDay = []
    
    fixedGasPrice = 0.5086

    for electricity_entry in filtered_electricity_entries:
        tarif = 0
        electricity_entry_time = datetime.strptime(electricity_entry['HourDK'][-8:], "%H:%M:%S").strftime("%H:%M")

        if electricity_entry_time == '23:00':
            electricity_entry_time = '23:59'
            
        if '00:00' <= electricity_entry_time <= '05:00':
            tarif = lavLast
        elif '06:00' <= electricity_entry_time <= '16:00':
            tarif = højLast
        elif '21:00' <= electricity_entry_time <= '23:59':
            tarif = højLast
        else:
            tarif = spidsLast

        ElectricitySpotPriceList.append((electricity_entry['SpotPriceDKK'] / 1000) + tarif)

        if minimumRunTimeCounter == 0 or minimumRunTimeCounter == minimumRunTime or electricity_entry_time == '23:59':
            startEndTimeList.append(electricity_entry_time)

            if minimumRunTimeCounter == minimumRunTime or electricity_entry_time == '23:59':
                minimumRunTimeCounter = 0
                ElectricitySpotPriceAverage = round(sum(ElectricitySpotPriceList) / len(ElectricitySpotPriceList), 4)

                # Compare ElectricitySpotPriceAverage with gas_entry['THEPriceDKK_kWh']
                if ElectricitySpotPriceAverage < fixedGasPrice:
                    valueprint = f"Electricity ({ElectricitySpotPriceAverage})"
                    mixedUsagePriceDay.append(ElectricitySpotPriceAverage)
                else:
                    valueprint = f"Gas ({fixedGasPrice})"
                    mixedUsagePriceDay.append(fixedGasPrice)

                column_label = f"{startEndTimeList[len(startEndTimeList) - 2]}-{startEndTimeList[-1]}"
             
                header_row.append(column_label)
                
                matrix_row.append(valueprint)
                
        minimumRunTimeCounter += 1
    

    mixedUsagePriceDayAvg = round(sum(mixedUsagePriceDay) / len(mixedUsagePriceDay), 4)
    matrix_row.append(fixedGasPrice)
    matrix_row.append(mixedUsagePriceDayAvg)
    matrix_row.append(round(((fixedGasPrice - mixedUsagePriceDayAvg)/fixedGasPrice)*100,2))
        
        
    matrix.append(matrix_row)
    
    
header_row.extend(["Only on Gas", "Mixed usage", "procentage saved"])
matrix = [list(dict.fromkeys(header_row))] + matrix


# Output CSV file
csv_file_path = '/home/fa/Scripts/Lactosan/MultiBrændsel/Table.csv'

# Write matrix to CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(matrix)
"""
# # Function to set cell colors based on content
# def set_cell_color(value):
    
#     if isinstance(value, float):
#         return 'white'
#     elif 'Electricity (' in value:
#         return 'blue'
#     elif 'Gas (' in value:
#         return 'red'
#     else:
#         return 'white'

# # Create a figure and axis
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.set_axis_off()

# # Create a table and set cell colors
# table = Table(ax, bbox=[0, 0, 1, 1])

# for i, row in enumerate(matrix):
#     for j, value in enumerate(row):
#         cell_color = set_cell_color(value)
#         table.add_cell(i, j, 1/len(matrix[0]), 1/len(matrix), text=value, loc='center', facecolor=cell_color)

# # Add the table to the plot
# ax.add_table(table)

# plt.show()