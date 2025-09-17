"""
Pipeline:
1. Get human genes and their orthologs from Monarch KG (Neo4j).
2. Get phenotypes of orthologs.
3. Get phenotypes of diseases.
4. Use semsimian to compute similarity between ortholog phenotypes and disease phenotypes.
5. For diseases that are similar, check if they already have gene associations.
"""

import json
import pandas as pd
from semsimian import Semsimian
from neo4jConnection import Neo4jConnection
from neo4jConfig import configDict
from queries import *

from oaklib import get_adapter

# -------------------------------
# Load UPheno ontology remotely
# -------------------------------
# This pulls from OBO PURL; no local file needed
adapter = get_adapter("sqlite:obo:upheno")


# -------------------------------
# Connect to Neo4j
# -------------------------------
conn = Neo4jConnection(
    uri=configDict['uri'],
    user=configDict['user'],
    pwd=configDict['pwd']
)

DB_NAME = "monarch-20250217"

# -------------------------------
# Step 1: Get Human Genes + Orthologs
# -------------------------------
def getHumanGenes():
    response = conn.query(nameHGNC_query, db=DB_NAME)
    return [item for sublist in json.loads(json.dumps(response)) for item in sublist]

def getOrthologs(hgene):
    query = namesgeneOrthos_query(hgene)
    response = conn.query(query, db=DB_NAME)
    return [item for sublist in json.loads(json.dumps(response)) for item in sublist]

# -------------------------------
# Step 2: Get Phenotypes for Ortholog Genes
# -------------------------------
def getPhenotypes(gene_id):
    query = nameGenePhen_query(gene_id)
    response = conn.query(query, db=DB_NAME)
    return [item for sublist in json.loads(json.dumps(response)) for item in sublist]

# -------------------------------
# Step 3: Get Disease Phenotypes
# -------------------------------
def getDiseasePhenotypes():
    query = "MATCH (d:`biolink:Disease`)-[:`biolink:has_phenotype`]-(p:`biolink:PhenotypicFeature`) RETURN d.id, collect(p.id)"
    response = conn.query(query, db=DB_NAME)
    return [(row[0], row[1]) for row in response]

# -------------------------------
# Step 4: Semantic Similarity
# -------------------------------

# -------------------------------
# Ancestor-based Jaccard similarity
# -------------------------------
def get_ancestors(terms):
    """Return set of ancestors + self for each phenotype term."""
    ancestors = set()
    for t in terms:
        for a in adapter.ancestors(t, reflexive=True):
            ancestors.add(a)
    return ancestors

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


def computeSimilarity(ortho_phens, disease_phens):
    """
    Compute semantic similarity between two phenotype sets
    using ancestor-based Jaccard index.
    """
    ortho_anc = get_ancestors(ortho_phens)
    disease_anc = get_ancestors(disease_phens)
    return jaccard_similarity(ortho_anc, disease_anc)
'''
def computeSimilarity(ortho_phens, disease_phens):
    """
    Compute semantic similarity using OAKLib's similarity interface.
    Returns best-match average score.
    """
    scores = adapter.pairwise_similarity(ortho_phens, disease_phens)
    return scores.get("average_score", 0.0)'''

# -------------------------------
# Step 5: Check if Disease Already Has a Gene Association
# -------------------------------
def diseaseHasGene(disease_id, gene_id):
    query = numgeneDis_query(gene_id)
    response = conn.query(query, db=DB_NAME)
    count = [item for sublist in json.loads(json.dumps(response)) for item in sublist][0]
    return int(count) > 0

# -------------------------------
# Main Analysis
# -------------------------------
def runAnalysis():
    human_genes = getHumanGenes()
    disease_phens = getDiseasePhenotypes()

    results = []

    for hgene in human_genes[:50]:  # limit for demo
        orthos = getOrthologs(hgene)

        for ortho in orthos:
            ortho_phens = getPhenotypes(ortho)
            print(ortho_phens)
            if not ortho_phens:
                continue
            if len(ortho_phens) < 4:
                continue

            for disease_id, d_phens in disease_phens:
                if diseaseHasGene(disease_id, hgene):
                    continue # skip diseases with connected genes
                score = computeSimilarity(ortho_phens, d_phens)
                if score > 0.4:  # threshold for phenotypic similarity
                    has_gene_assoc = diseaseHasGene(disease_id, hgene)
                    results.append({
                        "human_gene": hgene,
                        "ortholog_gene": ortho,
                        "disease": disease_id,
                        "similarity_score": score,
                        "disease_has_gene_assoc": has_gene_assoc
                    })

    df = pd.DataFrame(results)
    df.to_csv("disease_gene_similarity_results.csv", index=False)
    print(df.head())
    return df

if __name__ == "__main__":
    runAnalysis()
