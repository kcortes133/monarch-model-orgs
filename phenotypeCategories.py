from neo4j import GraphDatabase
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

query2 = ("MATCH (phenotype:`biolink:PhenotypicFeature`) "
          "RETURN phenotype.id, phenotype.namespace")

class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = session.run(query, parameters)
            data = []
            for record in response:
                data.append(record)
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return data




# directory where data is

# establishing connecton with neo4j
conn = Neo4jConnection(uri="bolt://localhost:7687",
                       # establishing connecton with neo4j
                       user="neo4j")

db = 'monarch-20250217'
response = conn.query(query2, db=db)

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
