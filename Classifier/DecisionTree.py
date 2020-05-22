
# coding: utf-8

# # Importing the needed modules

# In[85]:


import numpy as np
import pandas as pd
from graphviz import Digraph
from graphviz import Graph
from pprint import pprint


# # Reading the datasets

# In[63]:


# trainData = pd.read_csv('../Datasets/sample_train.csv')
# devData = pd.read_csv('../Datasets/sample_dev.csv')
# testData = pd.read_csv('../Datasets/sample_test.csv')
# dataFrame = pd.DataFrame(trainData)


# In[64]:


def data_init(file):
    trainData = pd.read_csv(file)
    dataFrame = pd.DataFrame(trainData)
    return dataFrame
#     dataFrame=dataFrame.drop("rating",axis=1)


# In[65]:


def words_count(dataFrame):
    d = []
    if 'rating' in dataFrame.columns:
        d = dataFrame.rating
        dataFrame = dataFrame.drop('rating',axis=1)
    features = ['contains_No', 'contains_Please', 'contains_Thank', 'contains_apologize', 'contains_bad',
    'contains_clean', 'contains_comfortable', 'contains_dirty', 'contains_enjoyed', 'contains_friendly',
    'contains_glad', 'contains_good', 'contains_great', 'contains_happy', 'contains_hot', 'contains_issues',
    'contains_nice', 'contains_noise', 'contains_old', 'contains_poor', 'contains_right', 'contains_small',
    'contains_smell', 'contains_sorry', 'contains_wonderful', 'reviews.text', 'count_reviews.text']

    for i in dataFrame.columns:
        c = i.replace('contains_','')
        col = []
        for j in range(0,dataFrame.shape[0]):
            if dataFrame[i][j]==1:
                col.append(dataFrame['reviews.text'][j].count(c))
            else:
                col.append(0)
        dataFrame['count_'+c]=col

    dataFrame = dataFrame.drop(features,axis=1)
    dataFrame = dataFrame.join(d)
    return dataFrame


# In[66]:


def Is_pure(data):

    rating_column = data[:, -1]
    unique_classes = np.unique(rating_column)

    if len(unique_classes) == 1:
        return True
    else:
        return False


# In[67]:


def Data_classification(data):

    rating_column = data[:, -1]
    unique_classes, counts_unique_classes = np.unique(rating_column, return_counts=True)

    index = counts_unique_classes.argmax()
    classification = unique_classes[index]

    return classification


# In[68]:


def get_splits(data):

    potential_splits = {}
    n_columns = data.shape[1]
    for column_index in range(n_columns - 1):        # excluding the last column which is the rating
        potential_splits[column_index] = []
        values = data[:, column_index]
        unique_values = np.unique(values)

        potential_splits[column_index]=unique_values

    return potential_splits


# In[69]:


def splitting(data, split_column, split_value):

    split_column_values = data[:, split_column]

    data_below = data[split_column_values <= split_value]
    data_above = data[split_column_values > split_value]

    return data_below, data_above


# In[70]:


def calculate_entropy(data):

    rating_column = data[:, -1]
    _, counts = np.unique(rating_column, return_counts=True)

    probabilities = counts / counts.sum()
    entropy = sum(probabilities * -np.log2(probabilities))

    return entropy


# In[71]:


def calculate_overall_entropy(data_below, data_above):

    n = len(data_below) + len(data_above)
    p_data_below = len(data_below) / n
    p_data_above = len(data_above) / n

    overall_entropy =  (p_data_below * calculate_entropy(data_below)
                      + p_data_above * calculate_entropy(data_above))

    return overall_entropy


# In[72]:


def determine_best_split(data, potential_splits):

    overall_entropy = 9999
    for column_index in potential_splits:
        for value in potential_splits[column_index]:
            data_below, data_above = splitting(data, split_column=column_index, split_value=value)
            current_overall_entropy = calculate_overall_entropy(data_below, data_above)

            if current_overall_entropy <= overall_entropy:
                overall_entropy = current_overall_entropy
                best_split_column = column_index
                best_split_value = value

    return best_split_column, best_split_value



# In[73]:


def predict(df,tree):
    df=words_count(df)
    df["classification"] = df.apply(classify_example, axis=1, args=(tree.root,))
    with open('output.txt', 'w') as f:
        for text in df['classification'].tolist():
            f.write(text + '\n')
    return df['classification'].values



# # Implementing Node and Tree Classes

# In[74]:


class Node:

    def __init__(self,key):
        self.val = key
        self.left = None
        self.right = None
    def set_val(self,_val):
        self.val=_val
    def get_val(self):
        return self.val
    def set_left(self,_left):
        self.left=_left
    def get_left(self):
        return self.left
    def set_right(self,_right):
        self.right=_right
    def get_right(self):
        return self.right

    #@dispatch(Node,Node)
    def __eq__ (self, other):
        if not isinstance(other, Node):
            # Don't recognise "other", so let *it* decide if we're equal
            return NotImplemented
        if(self.val== other.val):
            return True
        else:
            return False







# In[75]:


class Tree:
    def __init__(self, _val = None):
        self.root = Node(_val)
        self.right, self.left = None, None
    def insert_right(self,right_node):
        if not isinstance(right_node, Tree):
            self.root.right=right_node
        else:
            self.root.right=right_node.root

    def insert_left(self,left_node):
        if not isinstance(left_node, Tree):
            self.root.left=left_node
        else:
            self.root.left=left_node.root
    #@dispatch(Tree,Tree)
    def __eq__(self, other):
        if not isinstance(other, Tree):
            # Don't recognise "other", so let *it* decide if we're equal
            return NotImplemented
        if(self.root.val== other.root.val):
            return True
        else:
            return False



# In[76]:


def todict(root):
        dictionary ={root.val:[]}
        if root.left==root.right==None:
            return root.val

        else:
            right_=todict(root.right)
            left_=todict(root.left)

        dictionary[root.val].append(right_)
        dictionary[root.val].append(left_)

        return dictionary


# In[81]:

def decision_tree_algorithm(df, counter=0, min_samples=2, max_depth=5):

    # data preparations
    if counter == 0:
        global COLUMN_HEADERS
        COLUMN_HEADERS = df.columns
        data = df.values
    else:
        data = df


    # base cases
    if (Is_pure(data)) or (len(data) < min_samples) or (counter == max_depth):
        classification = Data_classification(data)
        return Node(classification)


    # recursive part
    else:
        counter += 1
        # helper functions
        potential_splits = get_splits(data)
        split_column, split_value = determine_best_split(data, potential_splits)
        data_below, data_above = splitting(data, split_column, split_value)

        if len(data_below)==0 or len(data_above)==0:
            classification = Data_classification(data)
            return Node(classification)


        # instantiate sub-tree --to be converted into nodes
        feature_name = COLUMN_HEADERS[split_column]
        question = "{} <= {}".format(feature_name, split_value)
        sub_tree = Tree(question)

        yes_answer= decision_tree_algorithm(data_below, counter, min_samples, max_depth)
        no_answer = decision_tree_algorithm(data_above, counter, min_samples, max_depth)

        if yes_answer == no_answer:
                sub_tree = yes_answer
        else:
            sub_tree.insert_left(yes_answer)
            sub_tree.insert_right(no_answer)
        return sub_tree



# In[78]:


def classify_example(example, root):
    question = root.val
    feature_name, comparison_operator, value = question.split()

    # ask question
    # example.count()
    if str(example[feature_name]) <= value:
        answer = root.left
    else:
        answer = root.right

    # base case
    if answer.left==answer.right==None:
        return answer.val

    # recursive part
    else:
        residual_root = answer
        return classify_example(example, residual_root)

def classify_review_text(review_text,root):
    question=root.val
    feature_name, _, value = question.split()
    feature_name = feature_name.replace('count_','')
    # ask question
    if review_text.count(feature_name) <= int(value):
          answer = root.left
    else:
          answer = root.right
    # base case
    if answer.left==answer.right==None:  
        return answer.val
    # recursive part
    else:
        residual_root = answer
        return classify_review_text(review_text, residual_root)

# In[79]:


def calculate_accuracy(df_, tree,show=False):
    df=words_count(df_)
    df["classification"] = df.apply(classify_example, axis=1, args=(tree.root,))
    df["classification_correct"] = df["classification"] == df["rating"]

    accuracy = df["classification_correct"].mean()
    if show==True:
        #print(df.classification)
        #print(df.classification_correct)
#         print(df[['classification'],['classification_correct']])
        print(df[['classification', 'classification_correct']])
    return accuracy


# In[82]:

d = Digraph(name='graph',format='png')
def draw_graph(root):
    global d
    # initGraph()
    # make the id of node in graph unique by getting the object id of the node and assign to it
    root_id =str(id(root))
    root_val=root.val
    # get the left node value and id
    yes_node=root.left
    yes_id  =str(id(yes_node))
    yes_val =yes_node.val
    # get the right node value and id
    no_node =root.right
    no_id   =str(id(no_node))
    no_val =no_node.val
    #add node with root of sub tree to graph
    d.node(root_id ,root_val,style='filled',color="#FFC300",shape='rectangle')
    #if the yes_node was classification node add it to graph and don't recurse
    #create edge between the yes node and the root of subtree
    if yes_node.left==yes_node.right==None:
        d.node(yes_id,yes_val,style='filled',color= '#E50A0A' if yes_val == 'Negative' else '#10C160')
        d.edge(root_id,yes_id,label='True')
    # if node was a question (root to another tree)  crete node and edge ,continue recursion
    else:
        d.node(yes_id,yes_val,style='filled',color= "#FFC300",shape='rectangle')
        d.edge(root_id,yes_id,label='True')
        draw_graph(yes_node)
   #do the same for n0_node
    if no_node.left==no_node.right==None:
        d.node(no_id,no_val,style='filled',color= '#E50A0A' if no_val == 'Negative' else '#10C160')
        d.edge(root_id,no_id,label='False')

    else:
        d.node(no_id,no_val,style='filled',color= "#FFC300",shape='rectangle')
        d.edge(root_id,no_id,label='False')
        draw_graph(no_node)
    return
