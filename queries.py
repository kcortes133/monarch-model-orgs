"""
queries.py

This module contains Cypher queries for exploring the Monarch Initiative
Knowledge Graph (Neo4j). Each query is documented with its purpose and output.
"""

# -------------------------------
# Basic Queries
# -------------------------------

# Get all human genes (HGNC identifiers)
nameHGNC_query = """
MATCH (m:`biolink:Gene`)
WHERE m.id STARTS WITH "HGNC"
RETURN m.id
"""
#  Returns all HGNC gene IDs in the graph.


# Get orthologs for all human genes
nameHGNCOrthos_query = """
MATCH (m:`biolink:Gene`)-[:`biolink:orthologous_to`]-(n:`biolink:Gene`)
WHERE m.id STARTS WITH "HGNC"
RETURN n.id, m.id
"""
# For each human gene (HGNC), return its orthologous partner(s).


# Get phenotypes associated with human genes
nameHGNCPhens_query = """
MATCH (m:`biolink:Gene`)-[:`biolink:has_phenotype`]-(n:`biolink:PhenotypicFeature`)
WHERE m.id STARTS WITH "HGNC"
RETURN n.id, m.id
"""
#  For each human gene (HGNC), return linked phenotypic features.


# Get all phenotypes, their id and namespace i.e. human phenotype ontology (HPO)
namePhens_query = """
MATCH (phenotype:`biolink:PhenotypicFeature`)
          RETURN phenotype.id, phenotype.namespace"""


# -------------------------------
# Gene-Specific Queries
# -------------------------------

def namesgeneOrthos_query(gene: str) -> str:
    """
    Find orthologs for a specific gene.

    Args:
        gene (str): Gene ID (e.g., "HGNC:12345").

    Returns:
        str: Cypher query string.
    """
    return f"""
    MATCH (m:`biolink:Gene` {{id: "{gene}"}})-[:`biolink:orthologous_to`]-(n:`biolink:Gene`)
    RETURN n.id, m.id
    """


def numgeneDis_query(gene: str) -> str:
    """
    Count how many diseases a given gene is associated with.
    """
    return f"""
    MATCH (m:`biolink:Gene` {{id: "{gene}"}})--(n:`biolink:Disease`)
    RETURN count(*)
    """


def numGenePhens_query(gene: str) -> str:
    """
    Count how many phenotypes are associated with a given gene.
    """
    return f"""
    MATCH (m:`biolink:Gene` {{id: "{gene}"}})--(n:`biolink:PhenotypicFeature`)
    RETURN count(*)
    """


def numGenePhen_query(gene: str) -> str:
    """
    Count phenotype associations where the gene explicitly has a 'has_phenotype' edge.
    """
    return f"""
    MATCH (m:`biolink:Gene` {{id: "{gene}"}})-[:`biolink:has_phenotype`]->(n:`biolink:PhenotypicFeature`)
    RETURN count(*)
    """

def nameGenePhen_query(gene: str) -> str:
    """
    Get phenotype associations where the gene explicitly has a 'has_phenotype' edge.
    """
    return f"""
    MATCH (m:`biolink:Gene` {{id: "{gene}"}})-[:`biolink:has_phenotype`]->(n:`biolink:PhenotypicFeature`)
    RETURN n.id
    """

# -------------------------------
# Organism-Level Queries
# -------------------------------

def numGeneOrthoTaxon_query(org1: str, org2: str) -> str:
    """
    Count the number of orthologous gene pairs between two organisms.

    Args:
        org1 (str): Taxon ID of first organism.
        org2 (str): Taxon ID of second organism.
    """
    return f"""
    MATCH (n:`biolink:Gene` {{in_taxon: "{org1}"}})-[:`biolink:orthologous_to`]-
          (m:`biolink:Gene` {{in_taxon: "{org2}"}})
    RETURN count(*)
    """


def numOrgPhens_query(org_prefix: str) -> str:
    """
    Count the number of phenotype associations for all genes in a given organism.

    Args:
        org_prefix (str): Prefix of gene IDs for the organism (e.g., "HGNC", "ZFIN").
    """
    return f"""
    MATCH (n:`biolink:Gene`)
    WHERE n.id STARTS WITH "{org_prefix}"
    MATCH (n)-[:`biolink:has_phenotype`]->()
    RETURN count(*)
    """


def numUPHENOrg_query(org1: str, org2: str) -> str:
    """
    Count cross-species phenotype connections via uPheno.

    Args:
        org1 (str): Prefix of phenotype IDs for organism 1.
        org2 (str): Prefix of phenotype IDs for organism 2.
    """
    return f"""
    MATCH (n:`biolink:PhenotypicFeature`)
    WHERE n.id STARTS WITH "{org1}"
    MATCH (n)--(u:`biolink:PhenotypicFeature` WHERE u.id STARTS WITH "UPHENO")--
          (m:`biolink:PhenotypicFeature` WHERE m.id STARTS WITH "{org2}")
    RETURN count(*)
    """
