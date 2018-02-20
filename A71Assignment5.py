# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 10:29:32 2016

@author: hina
"""
print ()

import networkx
from operator import itemgetter
import matplotlib.pyplot

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('/Users/aaku/Desktop/CIS509/HwAssignment5/amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])
    
# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past
purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph, purchasedAsin, radius=1)

# -------------------------------------------------------------------------------
#           Print the Ego Network       
#pos=networkx.spring_layout(purchasedAsinEgoGraph)
#matplotlib.pyplot.figure(figsize=(15,15))
#networkx.draw_networkx_nodes(purchasedAsinEgoGraph,pos,node_size=1500)
#networkx.draw_networkx_labels(purchasedAsinEgoGraph,pos,font_size=10)
#edgewidth = [ d['weight'] for (u,v,d) in G.edges(data=True)]
#networkx.draw_networkx_edges(purchasedAsinEgoGraph,pos,width=edgewidth)
#edgelabel = networkx.get_edge_attributes(purchasedAsinEgoGraph,'weight')
#networkx.draw_networkx_edge_labels(purchasedAsinEgoGraph,pos,edge_labels=edgelabel,font_size=10)
#matplotlib.pyplot.axis('off')
#matplotlib.pyplot.show()
# -------------------------------------------------------------------------------

# Next, recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()
for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,e)
        
# -------------------------------------------------------------------------------
#           PRINT THE ISLAND GRAPH       

#pos=networkx.spring_layout(purchasedAsinEgoTrimGraph)
#matplotlib.pyplot.figure(figsize=(15,15))
#networkx.draw_networkx_nodes(purchasedAsinEgoTrimGraph,pos,node_size=1500)
#networkx.draw_networkx_labels(purchasedAsinEgoTrimGraph,pos,font_size=10)
#edgewidth = [ d['weight'] for (u,v,d) in purchasedAsinEgoTrimGraph.edges(data=True)]
#networkx.draw_networkx_edges(purchasedAsinEgoTrimGraph,pos,width=edgewidth)
#edgelabel = networkx.get_edge_attributes(purchasedAsinEgoTrimGraph,'weight')
#networkx.draw_networkx_edge_labels(purchasedAsinEgoTrimGraph,pos,edge_labels=edgelabel,font_size=10)
#matplotlib.pyplot.axis('off') 
#matplotlib.pyplot.show()       
 # -------------------------------------------------------------------------------

# Next, recall that given the purchasedAsinEgoTrimGraph you constructed above, 
# you can get at the list of nodes connected to the purchasedAsin by a single 
# hop (called the neighbors of the purchasedAsin) 
purchasedAsinNeighbors = []
purchasedAsinNeighbors = purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)
# print(len(purchasedAsinNeighbors))
# print(purchasedAsinNeighbors)

# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff
print()
weights = {}
for a in purchasedAsinNeighbors:
    # print('ASIN:',a)
    # print('Clustering Coefficient:', amazonBooks[a]['ClusteringCoeff'])
    # print('Degree Centrality:', amazonBooks[a]['DegreeCentrality'])
    # print('Average Rating:', amazonBooks[a]['AvgRating'])
    dc = amazonBooks[a]['DegreeCentrality']
    cc = amazonBooks[a]['ClusteringCoeff']
    sales = amazonBooks[a]['SalesRank']
    val = (cc*dc)/sales
    val = round(val, 5)
    # print('Value:', val)
    weights[a] = val
    # print()
# print(weights)
print()
sorted_weights = sorted(weights.items(), key=itemgetter(1), reverse=True)
# print(sorted_weights)
top5 = {}
i = 0
while i < 5:
    top5[sorted_weights[i][0]] = sorted_weights[i][1]
    i = i + 1
print()
# print(top5)
# print()
    
# Print Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff)
j = 1
print ("Top 5 Recommendations for Customer")
print ("-------------------------------------")
for rec in top5.keys():
    # print(rec)
    print("Recommendation #", j)
    print ("ASIN = ", rec) 
    print ("Title = ", amazonBooks[rec]['Title'])
    print ("SalesRank = ", amazonBooks[rec]['SalesRank'])
    print ("TotalReviews = ", amazonBooks[rec]['TotalReviews'])
    print ("AvgRating = ", amazonBooks[rec]['AvgRating'])
    print ("DegreeCentrality = ", amazonBooks[rec]['DegreeCentrality'])
    print ("ClusteringCoeff = ", amazonBooks[rec]['ClusteringCoeff'])
    j = j + 1
    print()
