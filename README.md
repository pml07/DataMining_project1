# Data Mining Project1

### 目錄簡介
---

* apriori2.py：Apriori實作
* fpgrowth2.py：FP-growth實作
* convert_csv.py：對dataset進行轉換
* .../dataset：存放欲讀取的dataset
  * dataset/output_convert.xlsx：讀取之dataset
* .../log：用來儲存輸出之結果
  * output_convert_apriori.txt：Apriori輸出之結果
    * (3,0.5)：代表minsupport=3 / minconfidence=0.5
  * output_convert_fpgrowth.txt：FP-growth輸出之結果

### DataSet Download
---

* IBM_Quest_Synthetic_Data_Generator
   - Download exe.  
   - Using cmd executes program  
   ![](https://i.imgur.com/7uls43m.png)
   - Using LIT module generates data  
   ![](https://i.imgur.com/SxMOmD6.png)
   - execution  
```cpp=
"IBM Quest Data Generator.exe" lit -ascii -ntrans 10 -tlen 3 -nitems 4 -fname output
```

### Data introduction
---

* data三行分別代表customer, transaction, item
![](https://i.imgur.com/jXAFpgS.png)

* 對data進行處理轉成自己想要的資料型態
```cpp=
origional_df = pd.read_csv("output.csv")
d = {'TID':[],'Items':[]}

for id in origional_df['TID'].unique():
    d['TID'].append(id)
    buy_item = origional_df[origional_df['TID'] == id]['Items'].to_list()
    d['Items'].append(buy_item)

pd.DataFrame(d).to_csv("output_convert.csv",index=None)
```

* 將 .csv匯入excel存成 .xlsx，此時兩行之Header分別代表TID, Items

  ![](https://i.imgur.com/DlHCbJI.png)

### Read file
---

* 對檔案做處理時，是將原先 .txt整理成Header為TID、Items兩行的形式(如上圖)
* 再將 .txt放入excel，輸出後得到 .xlsx
  * 此步驟是希望得到結果後，能利用excel來隨機手動查詢結果是否與原先資料吻合
* 也可直接讀取 .csv

```cpp=
def load_data(path):
	ans=[]
	if path.split(".")[-1]=="xlsx":  # file為.xlsx                    
		from xlrd import open_workbook
		import xlwt
		workbook=open_workbook(path)
		sheet=workbook.sheet_by_index(0)  # 讀第一個sheet
		for i in range(1,sheet.nrows):  # 略過header,從第二行開始讀取數據,第一列為TID,第二列為Items
			temp=sheet.row_values(i)[1].strip("[]").split(", ")[:-1]
			if len(temp)==0: continue
			temp=list(set(temp))
			temp.sort()
			ans.append(temp)
	elif path.split(".")[-1]=="csv":  # file為.csv
		import csv
		with open(path,"r") as f:
			reader=csv.reader(f)
			for row in reader:
				row=list(set(row))
				row.sort()
				ans.append(row)
	return ans
```

### Apriori 與 FP-growth比較
---

* 執行時間之比較
   * Apriori執行時間：
     * minsup=3 / minconf=0.0
     ![](https://i.imgur.com/5UvwLCl.png) 
     * minsup=3 / minconf=0.5
     ![](https://i.imgur.com/HRemNQG.png)
     * minsup=5 / minconf=0.5
     ![](https://i.imgur.com/0srAwL2.png)
     * minsup=8 / minconf=0.0
     ![](https://i.imgur.com/2VslucB.png)
     * minsup=8 / minconf=0.5
     ![](https://i.imgur.com/ORr79zP.png)
       * 可以發現Apriori執行時，在itemset長度=2的時候花費時間最多
         * 此時大部分的組合都符合minsupport，所以會產生幾乎Item_size * Item_size種結果
       * 隨著執行越到後期，所需時間會越來越少
         * 小於minsupport的itemset會不斷被刪減，需要從頭掃過的資料減少
       * 若提高minsupport，相對符合的Itemset也會減少，則執行時間會因此加快
       * 且與minconfidence相較之下，minsupport對於產生的規則數量影響更大
 
   * FP-growth執行時間：
     * minsup=3 / minconf=0.0
     ![](https://i.imgur.com/vB7yBKp.png)
     * minsup=3 / minconf=0.5
     ![](https://i.imgur.com/lrNoIa4.png)
     * minsup=5 / minconf=0.5
     ![](https://i.imgur.com/4BUyhjz.png)
     * minsup=8 / minconf=0.0
     ![](https://i.imgur.com/1M6CFqb.png)
     * minsup=8 / minconf=0.5
     ![](https://i.imgur.com/3LsFT6f.png)
   
       * 可以發現FP-growth執行過程花費時間較Apriori短
         * 原因在於FP-growth不需要每次都去比對itemset在整個data中出現的次數
           * 雖然FP-tree也需要列出所有組合，但由於樹的height不⾼，所以產⽣的數量也⼤幅減少
        * 當minsupport提高時，運行時間會減少
        * 與minconfidence相較之下，minsupport對於產生的規則數量影響更大

### Conclusion
---
* 對運行時間及產生關聯規則數量之影響

|  | 增加support | 減少support |
| -------- | -------- | -------- |
| 增加confidence | 最多 | 次少 |
| 減少confidence | 次多 | 最少 |

    minsupport對產生的規則與計算時間影響比minconfidence還大
* 以耗費的時間方面來說，無論是較大dataset、較小minsupport或較小minconfidence中，FP-growth所需時間比Apriori減少很多
  * 但FP-growth不像Apriori會在過程中不斷刪掉小於minsupport的itemset，所以FP-growth會比Apriori需要更多的記憶體空間。

* 由於不熟悉Tree的實作，因此在實作FP-tree遇到很多困難，但也因此更了解兩者的差異，也更深入的學習到這兩種演算法。
