from neo4j import GraphDatabase
import json
from neo4jConnection import Neo4jConnection
from neo4jConfig import configDict
import pandas as pd
import holoviews as hv
import matplotlib.pyplot as plt
from neo4jConfig import configDict
from queries import *

# establishing connection with neo4j
conn = Neo4jConnection(uri=configDict['uri'],
                       user=configDict['user'],
                       pwd=configDict['pwd'])
DB_NAME = configDict['db']


def getAllHGenes():
    """Return all human genes with HGNC IDs."""
    response = conn.query(nameHGNC_query, db=DB_NAME)
    return [item for sublist in json.loads(json.dumps(response)) for item in sublist]


def getAllOrthos():
    """Return all human genes that have orthologs in other organisms."""
    response = conn.query(nameHGNCOrthos_query, db=DB_NAME)
    orthologs = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
    return set(filter(lambda x: x.startswith('HGNC'), orthologs))


def getOrthoTypeCount(humanGwithOrtho):
    """Count ortholog types (by taxon prefix) for each human gene."""
    humanOrthoTypes = {}
    for gene in humanGwithOrtho:
        query = namesgeneOrthos_query( gene)  # substitute
        response = conn.query(query, db=DB_NAME)
        orthologs = [item for sublist in json.loads(json.dumps(response)) for item in sublist]

        humanOrthoTypes[gene] = {}
        for o in orthologs:
            moType = o.split(':')[0]
            humanOrthoTypes[gene][moType] = humanOrthoTypes[gene].get(moType, 0) + 1
    return humanOrthoTypes


def hasPhenotype(genes):
    """Split genes into those with and without phenotypic annotations."""
    genesWithPhenotype, genesWithoutPhenotype = [], []
    for g in genes:
        query = numGenePhens_query(g)
        response = conn.query(query, db=DB_NAME)
        count = [item for sublist in json.loads(json.dumps(response)) for item in sublist][0]
        if int(count) > 0:
            genesWithPhenotype.append(g)
        else:
            genesWithoutPhenotype.append(g)
    return set(genesWithPhenotype), set(genesWithoutPhenotype)


def hasDiseaseAnnotation(genes):
    """Split genes into those with and without disease annotations."""
    genesWithDisease, genesWithoutDisease = [], []
    for g in genes:
        query = numgeneDis_query(g)
        response = conn.query(query, db=DB_NAME)
        count = [item for sublist in json.loads(json.dumps(response)) for item in sublist][0]
        if int(count) > 0:
            genesWithDisease.append(g)
        else:
            genesWithoutDisease.append(g)
    return set(genesWithDisease), set(genesWithoutDisease)

# -------------------------------
# Sankey Visualization
# -------------------------------


def orthoSankey():
    allOrthologs = getAllOrthos()
    humanOrthoTypes = getOrthoTypeCount(allOrthologs)

    onlyOneOrtho = []
    multiOrthoOneOrg = []
    for hgene in humanOrthoTypes:
        if len(humanOrthoTypes[hgene]) == 1:
            modelOrg = list(humanOrthoTypes[hgene].keys())[0]
            if humanOrthoTypes[hgene][modelOrg] == 1:
                onlyOneOrtho.append(hgene)
            else: multiOrthoOneOrg.append(hgene)


    multiOrthologs = set(allOrthologs) - set(onlyOneOrtho) - set(multiOrthoOneOrg)
    gwithPhen, gWOPhen = hasPhenotype(list(multiOrthologs))
    gwithPhenOO, gWOPhenOO = hasPhenotype(onlyOneOrtho)
    gwithPhenMO, gWOPhenMO = hasPhenotype(multiOrthoOneOrg)


    gwithDis, gWODis = hasDiseaseAnnotation(list(multiOrthologs))
    gwithDisOO, gWODisOO = hasDiseaseAnnotation(onlyOneOrtho)
    gwithDisMO, gWODisMO = hasDiseaseAnnotation(multiOrthoOneOrg)

    sanKeyData = []
    sanKeyData.append(['Human Genes with Orthologs', 'Genes with Many Orthologs', len(multiOrthologs)])
    sanKeyData.append(['Human Genes with Orthologs', 'Genes with One Ortholog', len(onlyOneOrtho)])
    sanKeyData.append(['Human Genes with Orthologs', 'Genes with Orthologs from One Organism', len(multiOrthoOneOrg)])

    sanKeyData.append(['Genes with Many Orthologs', 'Has Disease Annotation', len(gwithDis)])
    sanKeyData.append(['Genes with One Ortholog', 'Has Disease Annotation', len(gwithDisOO)])
    sanKeyData.append(['Genes with Orthologs from One Organism', 'Has Disease Annotation', len(gwithDisMO)])

    sanKeyData.append(['Genes with Many Orthologs', 'No Disease Annotation', len(gWODis)])
    sanKeyData.append(['Genes with One Ortholog', 'No Disease Annotation', len(gWODisOO)])
    sanKeyData.append(['Genes with Orthologs from One Organism', 'No Disease Annotation', len(gWODisMO)])

    sanKeyData.append(['Has Disease Annotation', 'Has Phenotypic Feature Many Orthologs', len(gwithDis.intersection(gwithPhen)) ])
    sanKeyData.append(['Has Disease Annotation', 'Has Phenotypic Feature One Ortholog', len(gwithDisOO.intersection(gwithPhenOO))])
    sanKeyData.append(['Has Disease Annotation', 'Has Phenotypic Feature Orthologs from One Organism', len(gwithDisMO.intersection(gwithPhenMO))])

    sanKeyData.append(['No Disease Annotation', 'No Phenotypic Feature Many Orthologs', len(gWODis.intersection(gWOPhen))])
    sanKeyData.append(['No Disease Annotation', 'No Phenotypic Feature One Ortholog', len(gWODisOO.intersection(gWOPhenOO))])
    sanKeyData.append(['No Disease Annotation', 'No Phenotypic Feature Orthologs from One Organism', len(gWODisMO.intersection(gWOPhenMO))])


    df = pd.DataFrame(sanKeyData,  columns=['source','target', 'value'])
    df.to_csv('OrthologSankeyDataExpanded.csv')
    hv.extension('matplotib')
    hv.output(fig='svg')
    sankey = hv.Sankey(df, label='Orthologs')
    sankey.opts(label_position='left', edge_color='target', cmap='tab20')
    hv.save(sankey, 'sankey5.svg')
    hv.render(sankey, backend='matplotlib')
    plt.show()

    return
orthoSankey()
