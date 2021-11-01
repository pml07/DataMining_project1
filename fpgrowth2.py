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

class Node:
	def __init__(self, node_name,count,parentNode):
		self.name = node_name
		self.count = count
		self.nodeLink = None
		self.parent = parentNode
		self.children = {}

class Fp_growth():
	def update_header(self,node, targetNode): # 更新headertable中的node形成的nodeLink
		while node.nodeLink != None:
			node = node.nodeLink
		node.nodeLink = targetNode

	def update_fptree(self,items, node, headerTable): #更新fptree
		if items[0] in node.children:
			# 判斷items的第一個node是不是子结點
			node.children[items[0]].count+=1
		else:
			# 建新的分支
			node.children[items[0]] = Node(items[0],1,node)
			# 更新frequece itemset
			if headerTable[items[0]][1] == None:
				headerTable[items[0]][1] = node.children[items[0]]
			else:
				self.update_header(headerTable[items[0]][1], node.children[items[0]])
		if len(items) > 1:
			self.update_fptree(items[1:], node.children[items[0]], headerTable)

	def create_fptree(self,data_set, min_support,flag=False): # 建tree
		'''
		依照data_set建fptree
		header_table結構為
		{"nodename":[num,node],..} 根據node.nodelink可以找到整棵樹中的所有nodename
		'''
		item_count = {} #各項出現次數
		for t in data_set: # 第一次掃資料
			for item in t:
				if item not in item_count:
					item_count[item]=1
				else:
					item_count[item]+=1
		headerTable={}
		for k in item_count:  #刪除 < minsupport的項
			if item_count[k] >= min_support:
				headerTable[k]=item_count[k]
		
		freqItemSet = set(headerTable.keys()) #滿足minsupport的frequent itemset
		if len(freqItemSet) == 0:
			return None, None
		for k in headerTable:
			headerTable[k] = [headerTable[k], None] # element: [count, node]
		tree_header = Node('head node',1,None)
		if flag:
			ite=tqdm(data_set)
		else:
			ite=data_set
		for t in ite: # 第二次掃資料
			localD = {}
			for item in t:
				if item in freqItemSet: # 只取滿足minsupport的frequent itemset
					localD[item] = headerTable[item][0] # element : count
			if len(localD) > 0:
				# 依照frequence由大到小排序
				order_item = [v[0] for v in sorted(localD.items(), key=lambda x:x[1], reverse=True)]
				# 利用排序好的更新tree
				self.update_fptree(order_item, tree_header, headerTable)
		return tree_header, headerTable

	def find_path(self,node, nodepath):
		'''
		將node的父結點加入路徑
		'''
		if node.parent != None:
			nodepath.append(node.parent.name)
			self.find_path(node.parent, nodepath)

	def find_cond_pattern_base(self,node_name, headerTable):
		'''
		找出所有condition pattern base
		'''
		treeNode = headerTable[node_name][1]
		cond_pat_base = {}
		while treeNode != None:
			nodepath = []
			self.find_path(treeNode, nodepath)
			if len(nodepath) > 1:
				cond_pat_base[frozenset(nodepath[:-1])] = treeNode.count 
			treeNode = treeNode.nodeLink 
		return cond_pat_base

	def create_cond_fptree(self,headerTable, min_support, temp, freq_items,support_data):
		# 一開始的frequent itemset是headerTable中的各元素
		freqs = [v[0] for v in sorted(headerTable.items(), key=lambda p:p[1][0])] #依照frequent itemset之frequence排序
		for freq in freqs: 
			freq_set = temp.copy()
			freq_set.add(freq)
			freq_items.add(frozenset(freq_set))
			if frozenset(freq_set) not in support_data: #check frequent itemset是否在support_data中
				support_data[frozenset(freq_set)]=headerTable[freq][0]
			else:
				support_data[frozenset(freq_set)]+=headerTable[freq][0]

			cond_pat_base = self.find_cond_pattern_base(freq, headerTable)
			cond_pat_dataset=[]
			for item in cond_pat_base:
				item_temp=list(item)
				item_temp.sort()
				for i in range(cond_pat_base[item]):
					cond_pat_dataset.append(item_temp)
			# 建condition pattern base tree
			cond_tree, cur_headtable = self.create_fptree(cond_pat_dataset, min_support)
			if cur_headtable != None:
				self.create_cond_fptree(cur_headtable, min_support, freq_set, freq_items,support_data)

	def generate_L(self,data_set,min_support):
		freqItemSet=set()
		support_data={}
		tree_header,headerTable=self.create_fptree(data_set,min_support,flag=True) #建fptree
		self.create_cond_fptree(headerTable, min_support, set(), freqItemSet,support_data)
		
		max_l=0
		for i in freqItemSet: #依照frequent itemset大小存到L中
			if len(i)>max_l:max_l=len(i)
		L=[set() for _ in range(max_l)]
		for i in freqItemSet:
			L[len(i)-1].add(i)
		for i in range(len(L)):
			print("frequent item {}:{}".format(i+1,len(L[i]))) 
		return L,support_data 

	def generate_R(self,data_set, min_support, min_conf):
		L,support_data=self.generate_L(data_set,min_support)
		rule_list = []
		sub_set_list = []
		for i in range(0, len(L)):
			for freq_set in L[i]:
				for sub_set in sub_set_list:
					if sub_set.issubset(freq_set) and freq_set-sub_set in support_data:#and freq_set-sub_set in support_data
						conf = support_data[freq_set] / support_data[freq_set - sub_set]
						big_rule = (freq_set - sub_set, sub_set, conf)
						if conf >= min_conf and big_rule not in rule_list:
						    # print freq_set-sub_set, " => ", sub_set, "conf: ", conf
							rule_list.append(big_rule)
				sub_set_list.append(freq_set)
		rule_list = sorted(rule_list,key=lambda x:(x[2]),reverse=True)
		return rule_list

if __name__=="__main__":

	filename="output_convert.xlsx"
	min_support=8
	min_conf=0.5

	spend_time=[]
	current_path=os.getcwd()
	if not os.path.exists(current_path+"/log"):
	    os.mkdir("log")

	path=current_path+"/dataset/"+filename
	save_path=current_path+"/log/"+filename.split(".")[0]+"_fpgrowth.txt"

	data_set=load_data(path)
	fp=Fp_growth()
	rule_list = fp.generate_R(data_set, min_support=8, min_conf=0.5)
	save_rule(rule_list,save_path)
