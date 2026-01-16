from Bio import Entrez
import time
from typing import List, Dict, Optional

Entrez.email = "tu_email@dominio.com"  # obligatorio por NCBI
# Entrez.api_key = "TU_NCBI_API_KEY"   # opcional, recomendado si haces muchas llamadas

QUERY = r'''
(
  ("Carcinoma, Hepatocellular"[MeSH Terms] OR hepatocellular carcinoma[Title/Abstract] OR HCC[Title/Abstract])
  OR
  ("Liver Neoplasms"[MeSH Terms] OR liver cancer[Title/Abstract] OR hepatic tumor*[Title/Abstract])
)
AND
(treat*[Title/Abstract] OR therap*[Title/Abstract] OR drug therapy[MeSH Subheading] OR intervention*[Title/Abstract])
AND
(
  "Clinical Trial"[Publication Type]
  OR "Randomized Controlled Trial"[Publication Type]
  OR "Controlled Clinical Trial"[Publication Type]
  OR "Phase I"[Publication Type] OR "Phase II"[Publication Type] OR "Phase III"[Publication Type] OR "Phase IV"[Publication Type]
  OR trial[Title/Abstract]
)
AND
(
  "Treatment Outcome"[MeSH Terms]
  OR outcome*[Title/Abstract]
  OR response rate[Title/Abstract] OR ORR[Title/Abstract]
  OR "Progression-Free Survival"[MeSH Terms] OR PFS[Title/Abstract]
  OR "Overall Survival"[MeSH Terms] OR OS[Title/Abstract]
)
AND
(
  "Drug-Related Side Effects and Adverse Reactions"[MeSH Terms]
  OR "adverse events"[Title/Abstract]
  OR AE[Title/Abstract]
  OR toxicity[Title/Abstract]
  OR safety[Title/Abstract]
)
AND
(humans[MeSH Terms] AND (english[Language] OR spanish[Language]))
'''.strip()


HIGH_EVIDENCE = {
    "Randomized Controlled Trial",
    "Phase III",
    "Meta-Analysis",
    "Systematic Review",
}

MODERATE_EVIDENCE = {
    "Controlled Clinical Trial",
    "Phase II",
}

ALLOWED_EVIDENCE = HIGH_EVIDENCE | MODERATE_EVIDENCE


def pubmed_search(query: str, retmax: int = 200) -> List[str]:
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax, sort="relevance")
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]


def pubmed_fetch_details(pmids: List[str]):
    # retmode="xml" para sacar AbstractText, PublicationTypeList, etc.
    handle = Entrez.efetch(db="pubmed", id=",".join(pmids), retmode="xml")
    records = Entrez.read(handle)
    handle.close()
    return records


def infer_evidence_level(publication_types: List[str]) -> Optional[str]:
    """
    Devuelve "high", "moderate" o None (si no cumple).
    Regla: si hay al menos un tipo HIGH => high; si no, si hay al menos un tipo MODERATE => moderate.
    """
    pub = set(publication_types)

    if pub & HIGH_EVIDENCE:
        return "high"
    if pub & MODERATE_EVIDENCE:
        return "moderate"
    return None


def matched_pub_types(publication_types: List[str]) -> List[str]:
    """Qué publication types relevantes (alta/moderada) aparecen en el artículo."""
    pub = set(publication_types)
    return sorted(pub & ALLOWED_EVIDENCE)


def extract_abstract(article) -> str:
    abstract = ""
    if "Abstract" in article and "AbstractText" in article["Abstract"]:
        # AbstractText puede ser lista de strings/objetos; lo convertimos a str
        abstract = " ".join([str(x) for x in article["Abstract"]["AbstractText"]])
    return abstract


def run(query: str, retmax_search: int = 200, retmax_keep: int = 100) -> List[Dict]:
    pmids = pubmed_search(query, retmax=retmax_search)
    print(f"PMIDs encontrados (antes de filtrar): {len(pmids)}")

    # Descargamos en batches para evitar peticiones enormes
    batch_size = 50
    kept: List[Dict] = []

    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        time.sleep(0.34)  # buena práctica NCBI

        data = pubmed_fetch_details(batch_pmids)

        for art in data.get("PubmedArticle", []):
            med = art["MedlineCitation"]
            article = med["Article"]

            pub_types = [str(x) for x in article.get("PublicationTypeList", [])]
            level = infer_evidence_level(pub_types)

            # FILTRO: quedarnos solo con alta/moderada
            if level is None:
                continue

            pmid = str(med["PMID"])
            title = str(article.get("ArticleTitle", ""))

            kept.append({
                "pmid": pmid,
                "title": title,
                "evidence_level": level,  # "high" o "moderate"
                "matched_pub_types": matched_pub_types(pub_types),
                "publication_types": pub_types,
                "abstract": extract_abstract(article)[:2000],
            })

            if len(kept) >= retmax_keep:
                break

        if len(kept) >= retmax_keep:
            break

    print(f"PMIDs tras filtrar (alta/moderada): {len(kept)}")
    return kept


if __name__ == "__main__":
    results = run(QUERY, retmax_search=200, retmax_keep=100)
    if results:
        print(results[0])
