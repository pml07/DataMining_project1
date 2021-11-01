import pandas as pd
import csv
import numpy as np
from pandas.core.frame import DataFrame
import itertools
from itertools import combinations, chain


df = pd.read_csv("output_convert.csv", converters={"Items": lambda x: x.strip("[]").split(", ")})


print("======== Dataframe head ==========")
print(df.head()) # 列出 dataset 前五欄
print("======== Items head ==========")
print(df['Items'].head()) # 列出 Items欄位 前五欄
print("======== First cutomer, first item==========")
print(df['Items'][0][0]) # Items欄位 , 第一個row的第一個商品

print("======== Detail ==========")

for customer, item in zip(df['TID'], df['Items']):
    print("Customer: ",customer, "Item: ",item, "Item amount: ",len(item))