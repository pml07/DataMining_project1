import csv
import pandas as pd

origional_df = pd.read_csv("output.csv")
d = {'TID':[],'Items':[]}

for id in origional_df['TID'].unique():
    d['TID'].append(id)
    buy_item = origional_df[origional_df['TID'] == id]['Items'].to_list()
    d['Items'].append(buy_item)

pd.DataFrame(d).to_csv("output_convert.csv",index=None)

df = pd.read_csv("output_convert.csv",converters={"Items": lambda x: x.strip("[]").split(", ")})
print("======== Dataframe head ==========")
print(df.head()) # 列出 dataset 前五欄
print("======== Items head ==========")
print(df['Items'].head()) # 列出 Items欄位 前五欄
print("======== First cutomer, first item==========")
print(df['Items'][0][0]) # Items欄位 , 第一個row的第一個商品

# print("======== Detail ==========")
# for custormer, item in zip(df['TID'], df['Items']):
#     print("Customer: ",custormer, "Item: ",item, "Item amount: ",len(item))
