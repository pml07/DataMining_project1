import os
import time
from tqdm import tqdm

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

def save_rule(rule,path):
	with open(path,"w") as f:
		f.write("index  confidence"+"   rules\n")
		index=1
		for item in rule:
			s=" {:<4d}  {:.3f}        {}=>{}\n".format(index,item[2],str(list(item[0])),str(list(item[1])))
			index+=1
			f.write(s)
		f.close()
	print("result saved,path is:{}".format(path))

class Apriori():
	def create_c1(self,dataset): #生成c1 candidate
		c1=set()
		for i in dataset:
			for j in i:
				item = frozenset([j])
				c1.add(item)
		return c1

	def create_ck(self,Lk_1,size): #利用frequent itemset Lk-1建ck candidate set
		Ck = set()
		l = len(Lk_1)
		lk_list = list(Lk_1)
		for i in range(l):
			for j in range(i+1, l): #找出前n-1個元素相同的項
				l1 = list(lk_list[i])
				l2 = list(lk_list[j])
				l1.sort()
				l2.sort()
				if l1[0:size-2] == l2[0:size-2]: #當最後一項不同時，生成下一candidate item
					Ck_item = lk_list[i] | lk_list[j]
					if self.has_infrequent_subset(Ck_item, Lk_1): #check candidate subset是否都在Lk-1中
						Ck.add(Ck_item)
		return Ck

	def has_infrequent_subset(self,Ck_item, Lk_1): #check Ck_item subset是否都在Lk-1中
		for item in Ck_item: 
			sub_Ck = Ck_item - frozenset([item])
			if sub_Ck not in Lk_1:
				return False
		return True

	def generate_lk_by_ck(self,data_set,ck,min_support,support_data): #利用ck生成lk，並將frequent item的support存到support_data字典中
		item_count={}
		Lk = set()
		for t in tqdm(data_set):
			for item in ck:
				if item.issubset(t):
					if item not in item_count:
						item_count[item] = 1
					else:
						item_count[item] += 1
		t_num = float(len(data_set))
		for item in item_count: # 若滿足minsupport，則加到frequent itemset
			if item_count[item] >= min_support:
				Lk.add(item)
				support_data[item] = item_count[item]
		return Lk
		

	def generate_L(self,data_set, min_support):
		support_data = {} 
		C1 = self.create_c1(data_set) #生成C1
		L1 = self.generate_lk_by_ck(data_set, C1, min_support, support_data) # 依照C1生成L1
		Lksub1 = L1.copy() # Lk-1=L1
		L = []
		L.append(Lksub1)
		i=2
		while(True):
			Ci = self.create_ck(Lksub1, i)  #依照Lk-1生成Ck
			Li = self.generate_lk_by_ck(data_set, Ci, min_support, support_data) #依照Ck生成Lk
			if len(Li)==0:break
			Lksub1 = Li.copy()  #Lk-1=Lk
			L.append(Lksub1)
			i+=1
		for i in range(len(L)):
			print("frequent item {}：{}".format(i+1,len(L[i])))
		return L, support_data

	def generate_R(self,dataset, min_support, min_conf):
		L,support_data=self.generate_L(dataset,min_support)
		rule_list = []
		sub_set_list = []
		for i in range(0, len(L)):
			for freq_set in L[i]:
				for sub_set in sub_set_list: #sub_set_list中保存的L1到Lk-1
					if sub_set.issubset(freq_set): #check sub_set是否是freq_set的子集
						#是否滿足minsupport，是則加到規則
						conf = support_data[freq_set] / support_data[freq_set - sub_set]
						big_rule = (freq_set - sub_set, sub_set, conf)
						if conf >= min_conf and big_rule not in rule_list:
							rule_list.append(big_rule)
				sub_set_list.append(freq_set)
		rule_list = sorted(rule_list,key=lambda x:(x[2]),reverse=True)
		return rule_list

if __name__=="__main__":

	filename="output_convert.xlsx"
	min_support=8 
	min_conf=0.5
	size=15


	current_path=os.getcwd()
	if not os.path.exists(current_path+"/log"):
		os.mkdir("log")
	path=current_path+"/dataset/"+filename
	save_path=current_path+"/log/"+filename.split(".")[0]+"_apriori.txt"

	data=load_data(path)
	apriori=Apriori()
	rule_list=apriori.generate_R(data,min_support=8, min_conf=0.5)
	save_rule(rule_list,save_path)
