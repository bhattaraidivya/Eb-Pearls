"""Illustrative, clearly labelled sample data used when no live source is configured.

Nothing here is a verified market statistic. Every finding carries a source object
marked as sample data so the analyst and the reader can see the evidence origin.
"""

from __future__ import annotations

import re

from models import Finding, ResearcherOutput, Source

SAMPLE_NOTE = "Authored for this assignment. Illustrative only, not verified research."
STOPWORDS = {
    "a", "an", "and", "for", "in", "market", "of", "on", "the", "to", "with",
    "analyze", "analyse", "research", "study", "brief", "industry", "company",
}


def _source(dataset: str) -> Source:
    return Source(
        title=f"Sample dataset: {dataset}",
        kind="Labelled sample data",
        note=SAMPLE_NOTE,
    )


TOPICS: list[dict] = [
    {
        "key": "food-delivery-nepal",
        "keywords": ("food delivery", "restaurant delivery", "foodmandu", "pathao food", "online food", "meal delivery", "food app"),
        "scope": "Food delivery market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: demand is described as concentrated in Kathmandu and other urban centres, with ordering through apps, websites and phone calls.", source=_source("food-delivery-nepal")),
            Finding(category="customer", claim="Sample data: customers are described as weighing delivery speed, food quality, packaging and trust in the merchant.", source=_source("food-delivery-nepal")),
            Finding(category="competitor", claim="Sample data: Foodmandu appears in the sample competitive set as a restaurant aggregator brand.", source=_source("food-delivery-nepal")),
            Finding(category="competitor", claim="Sample data: Pathao Food appears in the sample competitive set as an app-based food delivery service.", source=_source("food-delivery-nepal")),
            Finding(category="market", claim="Sample data: rider availability, restaurant onboarding and coverage outside major cities are described as recurring operational constraints.", source=_source("food-delivery-nepal")),
        ],
        "missing_information": [
            "No verified market size, growth rate or order volume",
            "No current market share or revenue figures for any provider",
            "No primary customer survey or pricing comparison",
            "No up-to-date regulatory or licensing information",
        ],
    },
    {
        "key": "ride-hailing-nepal",
        "keywords": ("ride hailing", "ride-hailing", "taxi app", "cab", "indrive", "ride sharing", "bike ride", "pathao ride"),
        "scope": "Ride-hailing market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: the sample focuses on app-based rides in urban areas, where smartphone access and driver supply shape availability.", source=_source("ride-hailing-nepal")),
            Finding(category="customer", claim="Sample data: fare transparency, wait time and driver ratings are described as important customer considerations.", source=_source("ride-hailing-nepal")),
            Finding(category="competitor", claim="Sample data: Pathao is listed in the sample competitive set as a ride-hailing provider.", source=_source("ride-hailing-nepal")),
            Finding(category="competitor", claim="Sample data: inDrive is listed in the sample competitive set as a ride-booking platform.", source=_source("ride-hailing-nepal")),
            Finding(category="market", claim="Sample data: peak-hour shortages and uneven coverage outside city centres are described as operational constraints.", source=_source("ride-hailing-nepal")),
        ],
        "missing_information": [
            "No verified ride volume, fleet size or market share data",
            "No current fare or commission comparison",
            "No driver-side survey or regulation details",
            "No coverage map for cities outside the sample",
        ],
    },
    {
        "key": "ecommerce-nepal",
        "keywords": ("e-commerce", "ecommerce", "online shopping", "online retail", "daraz", "hamrobazar", "online marketplace", "shopping app"),
        "scope": "E-commerce market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: online shopping is described as strongest in urban areas, with social media and messaging used alongside storefronts.", source=_source("ecommerce-nepal")),
            Finding(category="customer", claim="Sample data: delivery reliability, return policies and payment options are described as key trust factors.", source=_source("ecommerce-nepal")),
            Finding(category="competitor", claim="Sample data: Daraz appears in the sample competitive set as an online marketplace.", source=_source("ecommerce-nepal")),
            Finding(category="competitor", claim="Sample data: Hamrobazar appears in the sample competitive set as a local classifieds marketplace.", source=_source("ecommerce-nepal")),
            Finding(category="market", claim="Sample data: last-mile delivery cost and limited coverage outside major cities are described as recurring constraints.", source=_source("ecommerce-nepal")),
        ],
        "missing_information": [
            "No verified GMV, order count or growth rate",
            "No seller or category-level market share",
            "No recent customer satisfaction data",
            "No payment-method breakdown or return-rate figures",
        ],
    },
    {
        "key": "digital-wallet-nepal",
        "keywords": ("digital wallet", "mobile wallet", "fintech", "digital payment", "esewa", "khalti", "qr payment", "mobile banking"),
        "scope": "Digital wallet and fintech market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: digital wallets are described as widely used for utility payments, transfers and merchant QR payments in urban Nepal.", source=_source("digital-wallet-nepal")),
            Finding(category="customer", claim="Sample data: ease of use, merchant acceptance, transaction fees and trust in security are described as key adoption factors.", source=_source("digital-wallet-nepal")),
            Finding(category="competitor", claim="Sample data: eSewa appears in the sample competitive set as a digital payment service.", source=_source("digital-wallet-nepal")),
            Finding(category="competitor", claim="Sample data: Khalti appears in the sample competitive set as a mobile wallet and payment app.", source=_source("digital-wallet-nepal")),
            Finding(category="market", claim="Sample data: interoperability, agent networks and rural digital literacy are described as practical constraints in the sample.", source=_source("digital-wallet-nepal")),
        ],
        "missing_information": [
            "No verified transaction volume, user count or market share",
            "No regulatory or licensing comparison",
            "No fee schedule or merchant pricing benchmark",
            "No primary user trust or fraud-incidence data",
        ],
    },
    {
        "key": "edtech-nepal",
        "keywords": ("edtech", "education technology", "online learning", "e-learning", "elearning", "online course", "exam prep", "learning platform"),
        "scope": "EdTech market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: online learning is described as serving exam preparation, skill courses and supplemental tutoring, with stronger uptake in connected urban areas.", source=_source("edtech-nepal")),
            Finding(category="customer", claim="Sample data: affordability, content relevance, instructor credibility and mobile access are described as important learner priorities.", source=_source("edtech-nepal")),
            Finding(category="competitor", claim="Sample data: Mero School appears in the sample competitive set as an online learning platform.", source=_source("edtech-nepal")),
            Finding(category="competitor", claim="Sample data: eShikshalaya appears in the sample competitive set as a digital education service.", source=_source("edtech-nepal")),
            Finding(category="market", claim="Sample data: internet quality, device access and willingness to pay are described as adoption constraints in the sample.", source=_source("edtech-nepal")),
        ],
        "missing_information": [
            "No verified enrollment, revenue or completion-rate data",
            "No curriculum quality or learning-outcome evidence",
            "No pricing comparison across providers",
            "No rural access or policy analysis",
        ],
    },
    {
        "key": "it-outsourcing-nepal",
        "keywords": ("it outsourcing", "software outsourcing", "it services", "software development company", "tech company nepal", "outsourcing nepal", "bpo", "software export"),
        "scope": "IT outsourcing and software services market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: Nepal's IT services sample describes firms serving international clients with software development, design and support services.", source=_source("it-outsourcing-nepal")),
            Finding(category="customer", claim="Sample data: clients in the sample are described as valuing cost competitiveness, communication, delivery reliability and technical skill.", source=_source("it-outsourcing-nepal")),
            Finding(category="competitor", claim="Sample data: Deerwalk appears in the sample competitive set as a technology services company.", source=_source("it-outsourcing-nepal")),
            Finding(category="competitor", claim="Sample data: Leapfrog appears in the sample competitive set as a software product and services company.", source=_source("it-outsourcing-nepal")),
            Finding(category="market", claim="Sample data: talent retention, infrastructure reliability and global market access are described as recurring constraints.", source=_source("it-outsourcing-nepal")),
        ],
        "missing_information": [
            "No verified export revenue, headcount or growth figures",
            "No client concentration or contract-size data",
            "No compensation benchmark or attrition data",
            "No current government incentive or compliance details",
        ],
    },
    {
        "key": "tourism-nepal",
        "keywords": ("tourism", "travel", "trekking", "hospitality", "hotel", "tour operator", "visit nepal", "adventure tourism"),
        "scope": "Tourism and travel market in Nepal",
        "findings": [
            Finding(category="market", claim="Sample data: tourism is described around trekking, cultural travel and hospitality services, with demand influenced by seasonality and international travel conditions.", source=_source("tourism-nepal")),
            Finding(category="customer", claim="Sample data: travellers in the sample are described as valuing safety, guide quality, price transparency and authentic local experiences.", source=_source("tourism-nepal")),
            Finding(category="competitor", claim="Sample data: Himalaya Treks appears in the sample competitive set as an illustrative tour operator.", source=_source("tourism-nepal")),
            Finding(category="competitor", claim="Sample data: StayNepal appears in the sample competitive set as an illustrative travel booking platform.", source=_source("tourism-nepal")),
            Finding(category="market", claim="Sample data: infrastructure, weather disruption and service-quality consistency are described as operational constraints in the sample.", source=_source("tourism-nepal")),
        ],
        "missing_information": [
            "No verified arrival, spending or occupancy statistics",
            "No segment breakdown by source market or purpose",
            "No current safety, visa or policy data",
            "No provider-level market share or pricing benchmark",
        ],
    },
]


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS}


def lookup(query: str) -> ResearcherOutput:
    """Return the best matching labelled sample dataset, or an honest empty result."""

    normalized = query.lower()
    query_tokens = _tokens(normalized)
    best = None
    best_score = 0
    for topic in TOPICS:
        score = 0
        for keyword in topic["keywords"]:
            keyword_lower = keyword.lower()
            if " " in keyword_lower and keyword_lower in normalized:
                score += 3
            elif keyword_lower in query_tokens:
                score += 2
        if score > best_score:
            best, best_score = topic, score

    if best is None or best_score < 2:
        source = Source(
            title="Sample dataset: generic-placeholder",
            kind="Labelled sample data",
            note=SAMPLE_NOTE,
        )
        return ResearcherOutput(
            findings=[
                Finding(
                    category="other",
                    claim="Sample data placeholder: no topic-specific dataset matched this query, so no verified evidence is available.",
                    source=source,
                )
            ],
            missing_information=[
                "No topic-specific sample data is available for this query",
                "No live web search is configured in this prototype",
                "Add a dataset in sample_data.py or configure an LLM to help organize a supported topic",
            ],
        )

    return ResearcherOutput(
        findings=list(best["findings"]),
        missing_information=list(best["missing_information"]),
        data_origin=f"Labelled sample dataset '{best['key']}' (illustrative, not live research)",
    )


def competitor_names(findings: list[Finding]) -> list[str]:
    """Extract at most two competitor names from competitor-tagged findings."""

    names: list[str] = []
    for finding in findings:
        if finding.category != "competitor":
            continue
        match = re.search(r"Sample data:\s*([A-Za-z][\w. -]*?)\s+(?:appears|is listed)", finding.claim)
        name = match.group(1).strip() if match else finding.claim.split(":")[-1].strip().split(" ")[0]
        if name and name not in names:
            names.append(name)
        if len(names) == 2:
            break
    return names
