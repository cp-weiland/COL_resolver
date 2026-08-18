## ChecklistBank Species Resolver

A lightweight FastAPI microservice to resolve scientific and vernacular species names to their Catalogue of Life(COL)/ChecklistBank taxonomic records.

### Recap ChecklistBank API 

#### Direct ChecklistBank API Endpoints
The service queries the upstream ChecklistBank API (`https://api.checklistbank.org`):

- **Exact Scientific Name Search**:
  ```
  https://api.checklistbank.org/dataset/{dataset_id}/nameusage/search?content=SCIENTIFIC_NAME&q={encoded_name}&type=EXACT&offset=0&limit=10
  ```
- **Vernacular (Common) Name Search**:
  ```
  https://api.checklistbank.org/dataset/{dataset_id}/nameusage/search?content=VERNACULAR_NAME&q={encoded_name}&sortBy=RELEVANCE&offset=0&limit=1
  ```
ChecklistBank Sort Modes Overview

When querying the upstream ChecklistBank `/nameusage/search` endpoint directly:
- `RELEVANCE` *(default)*: Ranks results by Elasticsearch fulltext match score.
- `TAXONOMIC`: Orders results hierarchically through the Tree of Life.
- `NAME`: Orders results alphabetically (A–Z) by scientific name.
q

> **Note**: `{dataset_id}` is set to `3LR`. 
---

### The Service

#### Quickstart with Docker

#### 1. Build the Docker Image
```bash
docker build -t querycol .
```

#### 2. Run the Container
```bash
docker run -d -p 8000:8000 --name querycol-service querycol
```

The service will be available at `http://localhost:8000`. Interactive Swagger UI is accessible at `http://localhost:8000/docs`.

---

#### Microservice Endpoint (`GET /resolve`)I

Resolves a species name into taxonomic information.

- **Query Parameters**:
  - `name` *(string, required)*: Scientific (e.g. `Panthera onca`) or vernacular name (e.g. `Jaguar`, `tiger`).
- **Resolution Strategy**:
  1. Exact scientific name lookup on ChecklistBank.
  2. Fallback to vernacular name search if scientific lookup yields no results.


### Example Queries

#### 1. Example Query using a Scientific Name (*Panthera onca*)

**Request:**
```bash
curl -G "http://localhost:8000/resolve" --data-urlencode "name=Panthera onca"
```

**Response:**
```json
{
  "query": "Panthera onca",
  "resolved_by": "scientific",
  "scientific_name": "Panthera onca",
  "col_id": "4CGXQ",
  "taxonomic_status": "accepted",
  "extinct": false,
  "classification": [
    { "rank": "kingdom", "name": "Animalia" },
    { "rank": "phylum", "name": "Chordata" },
    { "rank": "class", "name": "Mammalia" },
    { "rank": "order", "name": "Carnivora" },
    { "rank": "family", "name": "Felidae" },
    { "rank": "genus", "name": "Panthera" },
    { "rank": "species", "name": "Panthera onca" }
  ],
  "vernacular_names": [
    { "name": "Jaguar", "language": "eng" },
    { "name": "Jaguar", "language": "fra" },
    { "name": "yaguar", "language": "spa" }
  ]
}
```

---

#### 2. Example Query using a Vernacular Name (*Jaguar*)

**Request:**
```bash
curl -G "http://localhost:8000/resolve" --data-urlencode "name=Jaguar"
```

**Response:**
```json
{
  "query": "Jaguar",
  "resolved_by": "vernacular",
  "scientific_name": "Panthera onca",
  "col_id": "4CGXQ",
  "taxonomic_status": "accepted",
  "extinct": false,
  "classification": [
    { "rank": "kingdom", "name": "Animalia" },
    { "rank": "phylum", "name": "Chordata" },
    { "rank": "class", "name": "Mammalia" },
    { "rank": "order", "name": "Carnivora" },
    { "rank": "family", "name": "Felidae" },
    { "rank": "genus", "name": "Panthera" },
    { "rank": "species", "name": "Panthera onca" }
  ],
  "vernacular_names": [
    { "name": "Jaguar", "language": "fra" },
    { "name": "yaguar", "language": "spa" },
    { "name": "tigre real", "language": "spa" }
  ]
}
```
---
#### 3. Issue: Example Query with name ambiguity

Omitting the 'h' in Panthera leads to matching via vernacular names that include 'Pantera' - here "Neofelis diardi" - as a name component.

**Request:**
```bash
curl -G "http://localhost:8000/resolve" --data-urlencode "name=Pantera onca"
```
**Response:**
```json
{
  "query": "Pantera onca",
  "resolved_by": "vernacular",
  "scientific_name": "Neofelis diardi",
  "col_id": "46H7Y",
  "taxonomic_status": "accepted",
  "extinct": false,
  "classification": [
    { "rank": "domain", "name": "Eukaryota" },
    { "rank": "kingdom", "name": "Animalia" },
    { "rank": "phylum", "name": "Chordata" },
    { "rank": "subphylum", "name": "Vertebrata" },
    { "rank": "infraphylum", "name": "Gnathostomata" },
    { "rank": "parvphylum", "name": "Osteichthyes" },
    { "rank": "megaclass", "name": "Tetrapoda" },
    { "rank": "class", "name": "Mammalia" },
    { "rank": "subclass", "name": "Theria" },
    { "rank": "infraclass", "name": "Eutheria" },
    { "rank": "order", "name": "Carnivora" },
    { "rank": "suborder", "name": "Feliformia" },
    { "rank": "family", "name": "Felidae" },
    { "rank": "subfamily", "name": "Pantherinae" },
    { "rank": "genus", "name": "Neofelis" },
    { "rank": "species", "name": "Neofelis diardi" }
  ],
  "vernacular_names": [
    { "name": "Panthère longibande", "language": "fra" },
    { "name": "Sunda clouded leopard", "language": "eng" },
    { "name": "Pantera longibanda", "language": "spa" },
    { "name": "Diardi's Clouded Leopard", "language": "eng" },
    { "name": "pantera nebulosa", "language": "spa" }
  ]
}
```
