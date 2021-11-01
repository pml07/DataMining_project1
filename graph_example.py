from ete3 import Tree, TreeStyle, TextFace, add_face_to_node

tree_str = "root" # the result of DFS_text

# generate graph's text format by using DFS parse the tree
def DFS_text(node, layer=0):
	global tree_str
	if node.children == None:
		return
	len_child = len(node.children.values())
	for idx, n in enumerate(node.children.values()):
		if idx ==0:
			tree_str = str(n.key) + " [" + str(n.value) + "]" +")" + tree_str	
		else:
			tree_str = str(n.key) + " [" + str(n.value) + "]" + "," + tree_str		
		DFS_text(n, layer+1)
		if idx == len_child-1:
			tree_str = "(" + tree_str
# plot tree
def graph(save_name=""):
	global tree_str

	def my_layout(node):
		F_node_name = TextFace(node.name, tight_text=True, fsize=12, fgcolor="green", ftype="Arial")
		add_face_to_node(F_node_name, node, column=0, position="branch-right")
		
	t = Tree( tree_str + ";",format=1)
	ts = TreeStyle()

	ts.branch_vertical_margin = 30
	ts.show_leaf_name = False
	ts.show_scale=False
	ts.layout_fn = my_layout
	ts.rotation=90 # vertical=90, horiz=0
	t.render(save_name+".png",  tree_style=ts)

# define node

class Node:
	def __init__(self, parent = None, key=None, value=0, children=None):
		self.parent = parent
		self.key = key
		self.value = value # count for the items
		self.children = children or {}

if __name__ == '__main__':
	# generate tree
	root = Node(parent=None, key="root", value=0)

	bread = Node(parent=root, key="Bread", value=3)
	root.children["bread"] = bread

	egg = Node(parent=root, key="Egg", value=5)
	root.children["egg"] = egg

	milk = Node(parent=bread, key="Milk", value=10)
	bread.children["milk"] = milk
	
	coke = Node(parent=bread, key="Coke", value=1)
	bread.children["coke"] = coke

	# dfs parsing tree
	DFS_text(root)
	print(tree_str) # the format that ete3 library require

	# generate graph
	graph(save_name="result")
	
