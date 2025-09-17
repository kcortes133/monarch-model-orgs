from neo4j import GraphDatabase
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from neo4jConnection import Neo4jConnection
from neo4jConfig import configDict
import queries


# establishing connection with neo4j
conn = Neo4jConnection(uri=configDict['uri'],
                       user=configDict['user'],
                       pwd=configDict['pwd'])

db = configDict['db']
response = conn.query(queries.namePhens_query, db=db)

df = pd.DataFrame(response, columns=["phenotype", "ontology"])

with open('uphenoNew.pkl', 'rb') as f:
    uphenoDict = pickle.load(f)

phenCounts = {}

for index, row in df.iterrows():
    upheno = row['phenotype']
    org = row['ontology']
    taxon= org
    for highTerm in uphenoDict.keys():
        if upheno in uphenoDict[highTerm]:
            if highTerm in phenCounts:
                if taxon in phenCounts[highTerm]:
                    phenCounts[highTerm][taxon] += 1
                else: phenCounts[highTerm][taxon] = 1
            else:
                phenCounts[highTerm] = {taxon: 1}

countDF = pd.DataFrame(phenCounts).fillna(0)

sns.heatmap(countDF, annot=False, square=True,  cmap="YlGnBu", norm=LogNorm(vmin=1, vmax=12200))
fig = plt.gcf()
fig.set_size_inches(15, 8)
plt.xticks(rotation=85)
plt.title("Phenotype HeatMap")
plt.savefig("heatmap.svg")
plt.show()
