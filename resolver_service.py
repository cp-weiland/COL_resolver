#!/usr/bin/env python3
"""
ChecklistBank Species Resolver Service
--------------------------------------
A FastAPI microservice that resolves scientific or vernacular names to their
ChecklistBank taxonomic records (including Catalogue of Life IDs).
"""

import urllib.request
import urllib.parse
import json
from fastapi import FastAPI, Query, HTTPException

app = FastAPI(
    title="ChecklistBank Species Resolver API",
    description="Microservice built on query_species.py to resolve names to ChecklistBank (CoL) taxonomic data.",
    version="1.0.0"
)

DATASET_ID = "3LR"

def query_by_scientific_name(species_name, dataset_id=DATASET_ID):
    """Queries ChecklistBank by exact scientific name."""
    encoded_name = urllib.parse.quote(species_name)
    url = f"https://api.checklistbank.org/dataset/{dataset_id}/nameusage/search?content=SCIENTIFIC_NAME&q={encoded_name}&type=EXACT&offset=0&limit=10"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode("utf-8")
                res = json.loads(data)
                return res.get("result", [])
    except Exception:
        pass
    return []

def query_by_vernacular_name(species_name, dataset_id=DATASET_ID):
    """Queries ChecklistBank by vernacular name (returning the highest relevance match)."""
    encoded_name = urllib.parse.quote(species_name)
    url = f"https://api.checklistbank.org/dataset/{dataset_id}/nameusage/search?content=VERNACULAR_NAME&q={encoded_name}&sortBy=RELEVANCE&offset=0&limit=1"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = response.read().decode("utf-8")
                res = json.loads(data)
                return res.get("result", [])[:1]
    except Exception:
        pass
    return []

@app.get("/resolve")
def resolve_species(name: str = Query(..., description="Scientific or vernacular name of the species to query")):
    """
    Submits a species name (scientific or vernacular) and returns ChecklistBank taxonomy details.
    """
    name_clean = name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Query parameter 'name' cannot be empty.")

    # 1. Attempt scientific name resolution
    results = query_by_scientific_name(name_clean)
    resolved_method = "scientific"

    # 2. If scientific name fails, fall back to vernacular name resolution
    if not results:
        results = query_by_vernacular_name(name_clean)
        resolved_method = "vernacular"

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Could not resolve '{name_clean}' as a scientific or vernacular species name."
        )

    # Format the top matching taxon
    match_item = results[0]
    usage = match_item.get("usage", {})
    classification = match_item.get("classification", [])
    vernacular = match_item.get("vernacularNames", [])

    scientific_name = usage.get("name", {}).get("scientificName", usage.get("label", "N/A"))
    col_id = usage.get("id", "N/A")
    status = usage.get("status", "N/A")
    extinct = usage.get("extinct", False)

    return {
        "query": name_clean,
        "resolved_by": resolved_method,
        "scientific_name": scientific_name,
        "col_id": col_id,
        "taxonomic_status": status,
        "extinct": extinct,
        "classification": [
            {"rank": c.get("rank"), "name": c.get("name")}
            for c in classification
        ],
        "vernacular_names": [
            {"name": v.get("name"), "language": v.get("language")}
            for v in vernacular
        ]
    }
