from neo4j import GraphDatabase
import json

# code to create neo4j connection taken from: https://towardsdatascience.com/create-a-graph-database-in-neo4j-using-python-4172d40f89c4
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
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


# directory where data is

# establishing connecton with neo4j
conn = Neo4jConnection(uri="bolt://localhost:7687",
                       # establishing connecton with neo4j
                       user="neo4j")

def getAllHGenes():
    query1 = 'MATCH (m:`biolink:Gene` WHERE m.id STARTS WITH "HGNC")' \
             'RETURN  m.id'
    response = conn.query(query1, db='monarch-20250217')
    allHumanGenes = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
    return allHumanGenes


def getAllOrthos():
    query = 'MATCH p=(m:`biolink:Gene` WHERE m.id STARTS WITH "HGNC")-[:`biolink:orthologous_to`]-(n:`biolink:Gene`) ' \
            'RETURN n.id, m.id'
    response = conn.query(query, db='monarch-20250217')
    orthologs = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
    humanGwithOrtho = set(filter(lambda x: x.startswith('HGNC'), orthologs))
    return humanGwithOrtho

def getOrthoTypeCount(humanGwithOrtho):
    humanOrthoTypes = {}
    for gene in humanGwithOrtho:
        query = 'MATCH p=(m:`biolink:Gene` {id: "' + gene+ '" })-[:`biolink:orthologous_to`]-(n:`biolink:Gene`) ' \
                                                           'RETURN n.id'
        response = conn.query(query, db='monarch-20250217')
        orthologs = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        humanOrthoTypes[gene] = {}
        for o in orthologs:
            moType = o.split(':')[0]
            if moType not in humanOrthoTypes[gene]:
                humanOrthoTypes[gene][moType] = 1
            else: humanOrthoTypes[gene][moType] += 1
    return humanOrthoTypes

def hasPhenotype(genes):
    genesWithPhenotype = []
    genesWithoutPhenotype = []
    for g in genes:
        query = 'MATCH p=(m:`biolink:Gene` {id: "' + g + '"})-[:`biolink:has_phenotype`]-(n:`biolink:PhenotypicFeature`) ' \
                                                         'RETURN count(p)'
        response = conn.query(query, db='monarch-20250217')
        hPhens = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        if int(hPhens[0]) == 0:
            genesWithoutPhenotype.append(g)
        else:
            genesWithPhenotype.append(g)
    return set(genesWithPhenotype), set(genesWithoutPhenotype)


def orthoHasPhenotype(genes):
    genesWithPhenotype = []
    genesWithoutPhenotype = []
    for g in genes:
        query = 'MATCH p=(m:`biolink:Gene` {id: "' + g + '"})-[`biolink:has_ortholog`]-(`biolink:Gene`)-[:`biolink:has_phenotype`]-(n:`biolink:PhenotypicFeature`) ' \
                                                         'RETURN count(p)'
        response = conn.query(query, db='monarch-20250217')
        hPhens = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        if int(hPhens[0]) == 0:
            genesWithoutPhenotype.append(g)
        else:
            genesWithPhenotype.append(g)
    return set(genesWithPhenotype), set(genesWithoutPhenotype)


def orthoHasPPI(genes):
    genesWithPPI = []
    genesWithoutPPI = []
    for g in genes:
        query = 'MATCH p=(m:`biolink:Gene` {id: "' + g + '"})-[`biolink:has_ortholog`]-(`biolink:Gene`)-[`biolink:interacts_with`]-(n:`biolink:Gene`) ' \
                                                         'RETURN count(p)'
        response = conn.query(query, db='monarch-20250217')
        hPPI = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        if int(hPPI[0]) == 0:
            genesWithoutPPI.append(g)
        else:
            genesWithPPI.append(g)
    return set(genesWithPPI), set(genesWithoutPPI)


def orthoHasGOAnnotation(genes):
    genesWithGO = []
    genesWithoutGO = []
    for g in genes:
        query = 'MATCH p=(m:`biolink:Gene` {id: "' + g + '"})-[`biolink:has_ortholog`]-(`biolink:Gene`)--(n:`biolink:BiologicalProcess` where n.id starts with "GO:") ' \
                                                         'RETURN count(p)'
        response = conn.query(query, db='monarch-20250217')
        hGOs = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        if int(hGOs[0]) == 0:
            genesWithoutGO.append(g)
        else:
            genesWithGO.append(g)
    return set(genesWithGO), set(genesWithoutGO)

def hasDiseaseAnnotation(genes):
    genesWithDisease = []
    genesWithoutDisease = []
    for g in genes:
        query2 = 'MATCH p=(m:`biolink:Gene` {id: "' + g + '" })--(n:`biolink:Disease`) ' \
                                                          'RETURN count(p)'
        response = conn.query(query2, db='monarch-20250217')
        disConns = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
        if disConns[0] > 0:
            genesWithDisease.append(g)
        else: genesWithoutDisease.append(g)
    return set(genesWithDisease), set(genesWithoutDisease)

def modelOF():
    query = ("MATCH p=(h:`biolink:Gene` where h.id starts with 'HGNC')--(g:`biolink:Disease`)-[:`biolink:model_of`]-(m:`biolink:Genotype`)"
             "return g.id")
    queryAll = ("MATCH p=(g:`biolink:Disease`)-[:`biolink:model_of`]-(m:`biolink:Genotype`)"
                "return g.id")
    response = conn.query(query, db='monarch-20250217')
    dis = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
    response = conn.query(queryAll, db='monarch-20250217')
    disAll = [item for sublist in json.loads(json.dumps(response)) for item in sublist]
    disWO =  set(disAll) -set(dis)
    print(len(set(dis)), len(set(disAll)))
    print(disWO)
    print(len(disWO))
    s = 0
    o = 0
    remaining = 0

    for dis in disWO:
        obsolete = False
        superClass = True
        query = "MATCH p=(g:`biolink:Disease` {id:'"+dis+"'})<-[:`biolink:subclass_of`]-(n) RETURN count(p)"
        queryName = "MATCH p=(g:`biolink:Disease` {id:'"+dis+"'}) RETURN g.name"
        response = conn.query(query, db='monarch-20250217')
        disConns = [item for sublist in json.loads(json.dumps(response)) for item in sublist]

        response = conn.query(queryName, db='monarch-20250217')
        disNames = [item for sublist in json.loads(json.dumps(response)) for item in sublist]

        if 'obsolete' in disNames[0]:
            obsolete = True
            o+=1
        if disConns[0] == 0:
            superClass = False
            s+=1
        if not obsolete and not superClass:
            remaining+=1
            print(dis)

    print(s, o, remaining, len(disWO))

    return
modelOF()

def orthoSankey():
    #allHumanGenes = getAllHGenes()
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


    modelOF()

    multiOrthologs = set(allOrthologs) - set(onlyOneOrtho) - set(multiOrthoOneOrg)
    gwithPhen, gWOPhen = hasPhenotype(list(multiOrthologs))
    gwithPhenOO, gWOPhenOO = hasPhenotype(onlyOneOrtho)
    gwithPhenMO, gWOPhenMO = hasPhenotype(multiOrthoOneOrg)

    print(orthoHasPhenotype(gWOPhen))

    #print(len(gwithPhen), len(gwithPhenOO), len(gwithPhenMO))
    #print(len(gWOPhen), len(gWOPhenOO), len(gWOPhenMO))

    #gwithDis, gWODis = hasDiseaseAnnotation(list(multiOrthologs))
    #gwithDisOO, gWODisOO = hasDiseaseAnnotation(onlyOneOrtho)
    #gwithDisMO, gWODisMO = hasDiseaseAnnotation(multiOrthoOneOrg)

    #print(gWODisOO.intersection(gwithPhenOO))

    '''
    orthowithPhen, orthoWOPhen = orthoHasPhenotype(list(allOrthologs))
    orthowithGO, orthoWOGO = orthoHasGOAnnotation(list(allOrthologs))
    orthowithPPI, orthoWOPPI = orthoHasPPI(list(allOrthologs))

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


    sanKeyData.append(['Has Phenotypic Feature Many Orthologs', 'Ortholog Has Phenotype',len(gwithDis.intersection(gwithPhen, orthoWOPhen)) ])
    sanKeyData.append(['Has Phenotypic Feature One Ortholog', 'Ortholog Has Phenotype', len(gwithDisOO.intersection(gwithPhenOO, orthoWOPhen)) ])
    sanKeyData.append(['Has Phenotypic Feature Orthologs from One Organism', 'Ortholog Has Phenotype', len(gwithDisMO.intersection(gwithPhenMO, orthoWOPhen))])

    sanKeyData.append(['No Phenotypic Feature Many Orthologs','Ortholog Has no Phenotype', len(gWODis.intersection(gWOPhen, orthowithPhen))])
    sanKeyData.append(['No Phenotypic Feature One Ortholog', 'Ortholog Has no Phenotype',len(gWODisOO.intersection(gWOPhenOO, orthowithPhen))])
    sanKeyData.append(['No Phenotypic Feature Orthologs from One Organism','Ortholog Has no Phenotype', len(gWODisMO.intersection(gWOPhenMO, orthowithPhen))])

    sanKeyData.append(['Has Phenotypic Feature Many Orthologs', 'Ortholog Has NO PPI',len(gwithDis.intersection(gwithPhen, orthoWOPPI)) ])
    sanKeyData.append(['Has Phenotypic Feature One Ortholog', 'Ortholog Has NO PPI', len(gwithDisOO.intersection(gwithPhenOO, orthoWOPPI)) ])
    sanKeyData.append(['Has Phenotypic Feature Orthologs from One Organism', 'Ortholog Has NO PPI', len(gwithDisMO.intersection(gwithPhenMO, orthoWOPPI))])

    sanKeyData.append(['No Phenotypic Feature Many Orthologs','Ortholog Has PPI', len(gWODis.intersection(gWOPhen, orthowithPPI))])
    sanKeyData.append(['No Phenotypic Feature One Ortholog', 'Ortholog Has PPI',len(gWODisOO.intersection(gWOPhenOO, orthowithPPI))])
    sanKeyData.append(['No Phenotypic Feature Orthologs from One Organism','Ortholog Has PPI', len(gWODisMO.intersection(gWOPhenMO, orthowithPPI))])

    sanKeyData.append(['Has Phenotypic Feature Many Orthologs', 'Ortholog Has NO GO',len(gwithDis.intersection(gwithPhen, orthoWOGO)) ])
    sanKeyData.append(['Has Phenotypic Feature One Ortholog', 'Ortholog Has NO GO', len(gwithDisOO.intersection(gwithPhenOO, orthoWOGO)) ])
    sanKeyData.append(['Has Phenotypic Feature Orthologs from One Organism', 'Ortholog Has NO GO', len(gwithDisMO.intersection(gwithPhenMO, orthoWOGO))])

    sanKeyData.append(['No Phenotypic Feature Many Orthologs','Ortholog Has GO', len(gWODis.intersection(gWOPhen, orthowithGO))])
    sanKeyData.append(['No Phenotypic Feature One Ortholog', 'Ortholog Has GO',len(gWODisOO.intersection(gWOPhenOO, orthowithGO))])
    sanKeyData.append(['No Phenotypic Feature Orthologs from One Organism','Ortholog Has GO', len(gWODisMO.intersection(gWOPhenMO, orthowithGO))])


    df = pd.DataFrame(sanKeyData,  columns=['source','target', 'value'])
    df.to_csv('OrthologSankeyDataExpanded.csv')
    print(df)
    hv.extension('matplotib')
    hv.output(fig='svg')
    sankey = hv.Sankey(df, label='Orthologs')
    sankey.opts(label_position='left', edge_color='target', cmap='tab20')
    hv.save(sankey, 'sankey5.svg')
    hv.render(sankey, backend='matplotlib')
    plt.show()
    '''
    return
#orthoSankey()
