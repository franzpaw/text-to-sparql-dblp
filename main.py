from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI
from SPARQLWrapper import JSON, SPARQLWrapper
from steps.step_1a_analyze_query import reformulate_query_1a
from steps.step_1a_analyze_query import generate_sparql_skeleton_1b


# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Instanziere neuen OpenAI‑Client (openai>=1.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise EnvironmentError(
        "Bitte Umgebungsvariable OPENAI_API_KEY setzen, bevor das Skript gestartet wird."
    )

SPARQL_ENDPOINT = "https://sparql.dblp.org/sparql"



def step_1b_build_retrieval_queries(analysis):
    """Phase 1b: Build SPARQL retrieval queries from analysis"""
    pass


def step_1c_execute_retrieval_queries(queries):
    """Phase 1c: Execute retrieval queries and build valid URI context"""
    pass


def step_2_generate_final_query(nl_query: str, uri_context):
    """Phase 2: Generate final SPARQL query (OpenAI)"""
    pass




if __name__ == "__main__":
    # Beispiel-Testfrage
    test_query = [
        "What is the primary affiliation of Zhang, Yu?",
        "What is the primary affiliation of the author Kunoth, Angela?",
        "What are the papers written by the person Wei Li?",
        "What are the papers written by the person Raman P. Singh?",
        "Mention the primary affiliation of A. Prakash.",
    ]

    for idx, test in enumerate(test_query, 1):
        print(f"\n--- Testfrage {idx} ---")

        # Schritt 1a ausführen
        reformulated = reformulate_query_1a(test, client)

        # Schritt 1b ausführen (wenn 1a erfolgreich war)
        if reformulated:
            sparql_skeleton = generate_sparql_skeleton_1b(reformulated, client)
            if sparql_skeleton:
                print("\n--- Ergebnis: SPARQL-Skelett (Ende 1b) ---")
                # Hier würde der Code für 1c und 2 ansetzen, um die Platzhalter
                # aufzulösen und die Query auszuführen.
            else:
                print("\nKonnte kein SPARQL-Skelett generieren.")