import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table
from datetime import datetime
import csv


# start_date = '2023-10-01T00:00'
# end_date = '2023-11-01T00:00'


# oilConversionRate = 10 #1L == 10kWh
# oilAmount = 10000 # In L
# oilPrice = 12700
# oilPriceLtr = oilAmount/oilPrice # DKK pr. L

#Anders variables moved form MixedBrændselwTrafi sheet Variables to here:
start_date = '2023-10-01T00:00'
end_date = '2023-11-01T00:00'
minimumRunTime = 2 # 1-24 hr - NULL INDEX!
minimumPriceDifference = 0.1 # DKK 10 øre
efficiencyElectricity = 1 # 0-1
efficiencyGas = 0.95 # 0-1
efficiencyOil = 1 # 0-1
efficiencyDamp = 0.80 #Damp på tårn 2. 

#El afgifter
elAfgiftPerkWh = 0.69 #DKK pr. kWh
lavLastEL = 0.022 #DKK pr. kWh
højLastEL = 0.067 #DKK pr. kWh
spidsLastEL = 0.135 #DKK pr. kWh
systemTarif = 0.054 #DKK pr. kWh
transmisstionEl = 0.058  #DKK pr. kWh

elAfgiftLavLast = elAfgiftPerkWh + lavLastEL + systemTarif + transmisstionEl
elAfgiftHøjLast = elAfgiftPerkWh + højLastEL + systemTarif + transmisstionEl
elAfgiftSpidsLast = elAfgiftPerkWh + spidsLastEL + systemTarif + transmisstionEl

#Gas afgifter
gasPrisGennemsnit = 5.41 #pr. m3
co2afgift = 0.41 #DKK pr. m3
noxafgift = 0.09 #DKK pr. m3
disturbutionGas = 0.35 #DKK pr. m3
naturGasAfgift = 2.431 #DKK pr. m3
kapacitetsTillæg = 0.069 #DKK pr. m3
nødForsyningsTarif = 0.016 #DKK pr. m3

gasafgift = co2afgift + noxafgift + disturbutionGas + naturGasAfgift + kapacitetsTillæg + nødForsyningsTarif

lavLast = 0.0652
højLast = 0.1957
spidsLast = 0.587



# Gas spot prices API request
GasSpotPrices = requests.get(f'https://api.energidataservice.dk/dataset/GasDailyBalancingPrice?offset=0&start={start_date}&end={end_date}&sort=GasDay%20DESC').json().get('records', [])

# Electricity spot prices API request
ElSpotPrices = requests.get(f'https://api.energidataservice.dk/dataset/Elspotprices?offset=0&start={start_date}&end={end_date}&sort=HourDK&filter={{"PriceArea":["DK1"]}}').json().get('records', [])


# 1L Oil == 10 kWh --> devide by 10 since you get 10 kWh pr purchased ltr oil.
# effective_oil_price = (oilPriceLtr / 10) / efficiencyOil

matrix = []

header_row = ['']
mixedUsagePriceTotal = []


elSpot = []

dayCounter = 0
# Avg el price
#print(sum(elSpot) / len(elSpot))

#print("El afgift lav last: " + str(ElSpotPrices))
for gas_entry in GasSpotPrices:
    gas_entry_date = datetime.strptime(gas_entry['GasDay'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

    filtered_electricity_entries = [electricity_entry for electricity_entry in ElSpotPrices if electricity_entry['HourDK'].startswith(gas_entry_date)]
    #print(filtered_electricity_entries)
    #print(gas_entry_date)
    
    matrix_row = [gas_entry_date]
    minimumRunTimeCounter = 0
    ElectricitySpotPriceList = []
    startEndTimeList = []
    mixedUsagePriceDay = []
    
    fixedGasPrice = 0.5086

    print("shift")
    
    for electricity_entry in filtered_electricity_entries:
        tarif = 0
        electricity_entry_time = datetime.strptime(electricity_entry['HourDK'][-8:], "%H:%M:%S").strftime("%H:%M")

        #print(electricity_entry['HourDK'][-8:], "%H:%M:%S")
        #print(datetime.strptime(electricity_entry['HourDK'][-8:], "%H:%M:%S").strftime("%H:%M"))         
            
            
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
        calculatePricesWhenHour = ['02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00', '23:59']
        if electricity_entry_time in calculatePricesWhenHour:
            ElectricitySpotPriceAverage = round(sum(ElectricitySpotPriceList) / len(ElectricitySpotPriceList), 4)
            if ElectricitySpotPriceAverage < fixedGasPrice:
                valueprint = f"Electricity ({ElectricitySpotPriceAverage})"
                mixedUsagePriceDay.append(ElectricitySpotPriceAverage)
            else:
                valueprint = f"Gas ({fixedGasPrice})"
                mixedUsagePriceDay.append(fixedGasPrice)
            matrix_row.append(valueprint)        


    mixedUsagePriceDayAvg = round(sum(mixedUsagePriceDay) / len(mixedUsagePriceDay), 4)
    matrix_row.append(fixedGasPrice)
    matrix_row.append(mixedUsagePriceDayAvg)
    matrix_row.append(round(((fixedGasPrice - mixedUsagePriceDayAvg)/fixedGasPrice)*100,2))
        
        
    matrix.append(matrix_row)

existing_header = ['00:00-02:00', '02:00-04:00', '04:00-06:00', '06:00-08:00', '08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00', '18:00-20:00', '20:00-22:00', '22:00-23:59', 'Only on Gas', 'Mixed usage', 'procentage saved']
#print("header_row: " + str(header_row))
header_row.extend(["Only on Gas", "Mixed usage", "procentage saved"])
matrix = [list(dict.fromkeys(existing_header))] + matrix


# Output CSV file
csv_file_path = 'Table.csv'

# Write matrix to CSV file
with open(csv_file_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(matrix)
    
