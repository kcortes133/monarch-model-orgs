import pandas as pd
import upsetplot as usplt
from matplotlib import pyplot as plt
import seaborn as sns

from neo4jConfig import configDict
from neo4jConnection import Neo4jConnection
from neo4jConfig import configDict
from queries import numUPHENOrg_query, numOrgPhens_query, numGeneOrthoTaxon_query

# establishing connection with neo4j
conn = Neo4jConnection(uri=configDict['uri'],
                       user=configDict['user'],
                       pwd=configDict['pwd'],)

"""
Functions to query the Monarch KG for phenotype and ortholog patterns
across genes and organisms. Produces plots and CSV outputs for visualization.
"""

# -------------------------------
# Phenotype Connections via uPheno
# -------------------------------
def phenotype_pattern(model_orgs=['HP','ZP','MP','WB','FYPO','XPO','DDPHENO']):
    """
    Create an upset plot showing cross-species phenotype connections via uPheno ontology.
    """
    dataDF = {org1: {org2: 0 for org2 in model_orgs} for org1 in model_orgs}
    labels, data = [], []

    for org1 in model_orgs:
        for org2 in model_orgs:
            query = numUPHENOrg_query(org1, org2)
            edge_count = conn.query(query, db='monarch20250812')[0]
            edge_count = int(str(edge_count).split('=')[1].split('>')[0])
            dataDF[org1][org2] = edge_count

            if [org1, org2] not in labels:
                labels.append([org1, org2])
                data.append(edge_count)

    df = pd.DataFrame(data=dataDF)
    print(df)

    # Create upset plot
    import upsetplot as usplt
    example = usplt.from_memberships(labels, data=data)
    usplt.plot(example, subset_size='sum')
    plt.yscale('log')
    plt.savefig('UPhenoConns.svg', format='svg')
    plt.show()


# -------------------------------
# Single Node Phenotype Counts
# -------------------------------
def phenotypesCount(model_orgs=['HGNC','WB','ZFIN','RGD','MGI','FB','PomBase','dictyBase','SGD','NCBIGene','Xenbase']):
    """
    Plot number of phenotypes associated with each organism's genes.
    """
    data = {}
    for org in model_orgs:
        query = numOrgPhens_query(org)
        count = conn.query(query, db='monarch-20250217')[0]
        data[org] = int(str(count).split('=')[1].split('>')[0])

    print(data)

# -------------------------------
# Ortholog Connections Between Organisms
# -------------------------------
def ortholog_pattern(taxons=None):
    """
    Build a heatmap of ortholog counts between organisms.
    Saves the counts as CSV and plots a heatmap.
    """
    if taxons is None:
        taxons = {
            'NCBITaxon:9606':'Humans', 'NCBITaxon:9031':'Jungle Fowl', 'NCBITaxon:9913':'Cow',
            'NCBITaxon:227321':'Fungi', 'NCBITaxon:9615':'Dog', 'NCBITaxon:10090':'Mouse',
            'NCBITaxon:7227':'Fly', 'NCBITaxon:7955':'Zebrafish', 'NCBITaxon:8364':'Frog1',
            'NCBITaxon:10116':'Rat', 'NCBITaxon:6239':'Worm', 'NCBITaxon:44689':'Soil Amoeba',
            'NCBITaxon:4896':'Fission Yeast', 'NCBITaxon:8355':'Frog2', 'NCBITaxon:559292':'Budding Yeast',
            'NCBITaxon:9823':'Wild Boar'
        }

    labels, data = [], []
    dataDF = {label: {label2:0 for label2 in taxons.values()} for label in taxons.values()}

    for org1 in taxons.keys():
        for org2 in taxons.keys():
            query = numGeneOrthoTaxon_query(org1, org2)
            edge_count = conn.query(query, db='monarch20250812')[0]
            edge_count = int(str(edge_count).split('=')[1].split('>')[0])

            label1 = taxons[org1]
            label2 = taxons[org2]
            dataDF[label1][label2] = edge_count

    df = pd.DataFrame(data=dataDF)
    df.to_csv('OrthologData.csv')
    sns.heatmap(df, annot=False, cmap='YlGnBu')
    plt.show()

phenotype_pattern()
phenotypesCount()
ortholog_pattern()
