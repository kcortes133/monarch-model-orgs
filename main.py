import pandas as pd
import os, json, statistics
import upsetplot as usplt
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm
from sqlalchemy.dialects.mssql.information_schema import columns
from matplotlib.colors import LogNorm
from neo4jConnection import Neo4jConnection
from neo4jConfig import configDict

#import orthologSankey, neo4jQueries, neo4jConfig, neo4jConnection, phenotypeCategories, queries
import queries, neo4jConfig, neo4jConnection

conn = Neo4jConnection(uri=configDict['uri'],
                       user=configDict['user'],
                       pwd=configDict['pwd'])

db = configDict['db']

# -------------------------------
# Query 1: Gene edge counts (grouped by taxon)
# -------------------------------
def get_gene_taxon_counts():
    """
    Query Neo4j for the number of edges connected to each taxon gene type.

    Returns
    -------
    pd.DataFrame
        A DataFrame with:
        - edge_count: number of edges connected to the gene
        - taxon: the NCBITaxon identifier for the gene
    """
    query = '''
    MATCH (g:`biolink:Gene`)-[e]-()
    RETURN count(e) AS edge_count, g.in_taxon AS taxon
    '''
    response = conn.query(query, db=configDict['db'])
    return pd.DataFrame(response)

# -------------------------------
# Query 3: Phenotypic feature counts by type
# -------------------------------
def get_phenotypic_feature_counts_by_type():
    """
    Query Neo4j for the number of phenotypic features,
    grouped by their type.

    Returns
    -------
    pd.DataFrame
        A DataFrame with one row per phenotypic feature type containing:
        - type: the category/type of the phenotypic feature
        - feature_count: number of phenotypic features of this type
    """
    query = '''
    MATCH (g:`biolink:PhenotypicFeature`)
    RETURN count(g) AS feature_count, g.namespace AS type
    '''
    response = conn.query(query, db=configDict['db'])
    return pd.DataFrame(response)

def get_gene_counts_by_taxon():
    """
    Query Neo4j for the number of genes in each taxon.

    Returns
    -------
    pd.DataFrame
        A DataFrame with one row per taxon containing:
        - taxon: the NCBITaxon identifier
        - gene_count: number of genes in that taxon
    """
    query = '''
    MATCH (g:`biolink:Gene`)
    RETURN g.in_taxon AS taxon, count(g) AS gene_count
    '''
    response = conn.query(query, db=configDict['db'])
    return pd.DataFrame(response)


# -------------------------------
# Usage
# -------------------------------
if __name__ == "__main__":
    raw_gene_results = get_gene_taxon_counts()
    print("Taxon gene edge counts:")
    print(raw_gene_results)

    phen_results = get_phenotypic_feature_counts_by_type()
    print("\nPhenotypic feature counts by type:")
    print(phen_results)

    gene_counts = get_gene_counts_by_taxon()
    print("Number of genes per taxon:")
    print(gene_counts)
