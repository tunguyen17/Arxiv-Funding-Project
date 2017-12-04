
# coding: utf-8

# <center>
# <h1>
# Optimal Academic Funding
# </h1>
# 
# <h3>
# Tu Anh Nguyen
# </h3>
# <h4>
# Tarleton State University, Stephenville, TX
# </h4>
# <h4>
# 12/04/2017
# </h4>
# 
# </center>

# In[35]:


import pandas as pd
import urllib
import io
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt


# In[36]:


# Download and import data

download = False # If download is true download and save data, else just read data

if(download):
    ## Data set
    data_url = "drop"
    df = pd.read_csv(data_url)
    df.to_csv("data.csv", index = False)
    
else:
    df = pd.read_csv("data.csv")


# In[37]:


# Cleaning the dataframe
df.dropna(inplace = True)
df.drop("Unnamed: 0", axis = 1, inplace = True) # Drop the "Unnamed: 0" | this was from index
df.drop_duplicates(subset = "doi", inplace = True)

# Get the category list
all_cat = list(set(df["category"].values))
all_cat.sort()

df.head()


# In[38]:


# Collecting all the aurhors
au_lst = []
for paper_authors in df["authors"].values:
    for author in paper_authors.split(";"):
        au_lst.append(author)
        
# Get all the unique authors       
au_lst = list(set(au_lst))
au_lst.sort()

au_dict = {author:index for (index, author) in enumerate(au_lst)}
cat_dict = {cat:index for (index, cat) in enumerate(all_cat)}

# Creating the matrix
n = len(au_dict)
p = len(all_cat)
credit_matrix = np.zeros((n, p))


# In[39]:


for index, row in df[["authors", "category"]].iterrows():
    
    author_list = row["authors"].split(";")
    contribute = 1.0/len(author_list)
    
    for author in author_list:
        try:
            credit_matrix[ au_dict[author], cat_dict[row["category"]] ] += contribute
        except KeyError as e:
            print(e)

# Calculating stuff
author_activity = credit_matrix / credit_matrix.sum(axis=1, keepdims=True)
author_weight_in_field = credit_matrix / credit_matrix.sum(axis=0, keepdims=True)
field_field_influence = np.transpose(author_activity).dot(author_weight_in_field)

proj1_df = pd.DataFrame(field_field_influence, columns = all_cat, index=all_cat)
proj1_df


# In[40]:


credit_df = pd.DataFrame(credit_matrix, columns = all_cat, index = au_lst)
credit_df.to_csv("credit_data.csv", index = False)


# In[41]:


credit_df.head()


# In[42]:


def update_author_funding(credit, field_funding):
    author_weight_in_field = credit / credit.sum(axis=0,keepdims=True)
    author_funding_from_field = author_weight_in_field * field_funding
    author_funding = author_funding_from_field.sum(axis=1,keepdims=True)
    return author_funding

def compute_credit(author_funding):
    new_credit = author_prod * author_funding
    field_credit = new_credit.sum(axis=0)
    author_credit = new_credit.sum(axis=1)
    total_credit = new_credit.sum()
    return new_credit, total_credit


# In[43]:


num_field = len(all_cat)
num_auth  = len(au_lst)
num_steps = 200

# Learning hyperparameter
p = 0.05
alpha = 0.1

# Current credit
current_credit = credit_matrix

# Current field funding - Generating a random funding
d = np.random.rand(num_field)
current_field_funding = d / d.sum()

# Saving the original field funding 
original_field_funding = current_field_funding.copy()


# In[44]:


# Initial calculation
current_author_funding = update_author_funding(current_credit, current_field_funding)
author_prod = current_credit / current_author_funding # This is invariance
current_credit, current_total_credit = compute_credit(current_author_funding)

# Initialize the best state
best_field_funding = current_field_funding.copy()
best_credit        = current_credit.copy()
best_total_credit  = current_total_credit.copy()

tot_credit_lst = []


# In[45]:


for i in range(num_steps):
    current_author_weight_in_field = current_credit / current_credit.sum(axis=0,keepdims=True)

    if(np.random.rand() < 0.05):
        gradient = np.random.rand(num_field)
    else:
        gradient = (author_prod * current_author_weight_in_field).sum(axis = 0)

    gradient_norm = gradient/(sum(gradient))  # normalize
    # Update field funding
    new_field_funding = current_field_funding + alpha*gradient_norm
    new_field_funding = new_field_funding / (sum(new_field_funding)) # normalize 

    new_author_funding = update_author_funding(current_credit, new_field_funding)
    new_credit, new_total_credit = compute_credit(new_author_funding)
    
    tot_credit_lst.append(new_total_credit)
    
    # update the new best result
    if(best_total_credit < new_total_credit):
        best_field_funding = new_field_funding.copy()
        best_credit        = new_credit.copy()
        best_total_credit  = new_total_credit.copy()

#         print("new Best")

    # Update for new step 
    current_field_funding = new_field_funding.copy()
    current_credit        = new_credit.copy()


# In[46]:


plt.plot(tot_credit_lst)
plt.ylabel('Total Credit')
plt.xlabel('step')
plt.show()


# In[47]:


funding_df = pd.DataFrame(best_field_funding, columns = ["Field Funding"], index = all_cat)
funding_df.sort_values(by="Field Funding", ascending = False)

