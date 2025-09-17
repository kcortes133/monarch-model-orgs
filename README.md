# Characterizing Model Organisms in the Monarch Initiative Knowledge Graph  

##  Goal  
The goal of this project is to **characterize how model organisms behave within the Monarch Initiative Knowledge Graph (KG)**. By examining orthologs, phenotypes, and cross-species connections, we aim to demonstrate how model organism data can fill gaps in human gene annotations and enhance understanding of disease biology.  

## Description  
This repository provides the code, analyses, and figures supporting a paper that evaluates the **representation of model organisms** in the Monarch KG.  
- It investigates **ortholog-based inference**, showing how annotations from model organisms enrich human genes lacking direct data.  
- It maps phenotypes across species using the **uPheno ontology**, highlighting both shared and unique biological features.  
- It explores **disease modeling relationships**, where genotypes in model organisms serve as models for human diseases.  
- It generates **tables and figures** that summarize coverage, cross-species connectivity, and case studies (e.g., SNORD118, SFMBT2, PIK3AP1).  

Together, these analyses illustrate the critical role of model organisms in expanding our knowledge of human biology and disease.  

---

##  Key Results  

- **Ortholog inference recovers missing human annotations**:  
  - 10,529 human genes lacking phenotype annotations have orthologs with phenotype annotations.  
  - 401 human genes lacking protein–protein interaction annotations have orthologs with interactions.  
  - 331 human genes lacking biological activity annotations have orthologs that do.  

- **Disease modeling relationships**:  
  - 2,066 human diseases are represented with *“model of”* links to model organism genotypes.  
  - 684 of these diseases lack direct human gene associations; after refinement, 114 remain as strong candidates for gene-association discovery.  

- **Phenotype ontology integration**:  
  - Nine phenotype ontologies contribute to the KG, with cross-species phenotypes (uPheno) dominating.  
  - Shared phenotypes reflect evolutionary proximity (e.g., zebrafish–xenopus, mouse–human).  
  - Some organisms (e.g., worms, fungi) show restricted phenotype coverage.  

- **Cross-species connectivity**:  
  - Richest orthology connections are between human, mouse, and zebrafish.  
  - Orthologs reveal hidden functions and novel interactions (e.g., SFMBT2 ↔ SMOC1).  
  - Some organisms (e.g., jungle fowl, fungi) lack ortholog connections in the KG.  

---

##  Project Context  

- Humans, mice, and zebrafish provide the largest number of gene and phenotype connections in the KG.  
- Ortholog inference adds phenotype, interaction, and activity annotations for thousands of human genes.  
- The uPheno ontology enables cross-species phenotype alignment, revealing shared and divergent biology.  
- “Model of” disease relationships show how model organism genotypes extend human disease biology.  

Key case studies (SNORD118, SFMBT2, PIK3AP1) demonstrate how orthologs and phenotypes extend understanding of human gene function and disease.  

---

## Configuration
configDict = {
    'db': 'monarch20250815',
    'uri': "bolt://localhost:7687",
    'user': "neo4j",
    'pwd': "monarch123"
}

# Acknowledgements 
Chat-GPT 5 was used in this repo for documentation and code clean up
