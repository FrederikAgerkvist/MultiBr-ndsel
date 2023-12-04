import numpy as np
import matplotlib.pyplot as plt
from matplotlib.table import Table
from datetime import datetime
import pandas as pd
import csv



mixedBrændselCsv = pd.read_csv("/home/fa/Scripts/Lactosan/MultiBrændsel/Table.csv", sep=",")
batchesEnergyUsage = pd.read_csv("/home/fa/Scripts/Lactosan/LactosanEnergyAnalysis.csv", sep=",")


print(mixedBrændselCsv)

for energyRow in batchesEnergyUsage[1:]:
    
    for energyColumn in energyRow:
        
        batchStart = energyColumn[9]
        batchEnd = energyColumn[10]
        gasUsage = energyColumn[4]
        
        for mixedBrændselRow in mixedBrændselCsv[1:]:
            
            mixedDay = mixedBrændselRow[0]
            hourList = mixedBrændselRow[1:10]
            
            