import json, re


# --- Schritt 1a: Query Reformulierung ---

def create_user_msg_reformulate(nl_query):
    """Erstellt die User-Nachricht für die Reformulierungs-API mit Few-Shot-Beispielen."""
    # 3 Beispiele aus questions.json.txt für Few-Shot Learning
    examples = [
        {
            "original": "What is the primary affiliation of Zhang, Yu?", # Q0001
            "reformulated": "Find primary affiliation for person Zhang, Yu."
        },
        {
            "original": "How many papers did 'Agrawal, Rakesh' publish in 2006?", # Example similar to Q0007
            "reformulated": "Count papers by author 'Agrawal, Rakesh' published in year 2006."
        },
        {
            "original": "Who is the most common co-author of Arthur Van Camp and how many papers do they have together?", # Q0451
            "reformulated": "Find the most frequent co-author for person 'Arthur Van Camp' AND count the number of papers co-authored with them."
        }
    ]

    few_shot_prompt = ""
    for ex in examples:
        few_shot_prompt += f"Original: \"{ex['original']}\"\nReformulated: \"{ex['reformulated']}\"\n\n"

    user_msg = f"""
Hier sind einige Beispiele zur Orientierung:

{few_shot_prompt}
Formuliere nun die folgende Nutzerfrage über die DBLP-Datenbank um.
Mache Absicht, Entitäten und Beziehungen klarer. Entferne Füllwörter.
Sei präzise und gib nur die umformulierte Frage zurück.

Original: "{nl_query}"
Reformulated:"""
    return user_msg.strip()

def reformulate_query_1a(nl_query: str, client):
    """
    Phase 1a: Reformuliert die NL-Query mit OpenAI für bessere Verarbeitung.
    Gibt die reformulierte Query als String zurück.
    """
    print("\n--- Phase 1a: Query-Reformulierung (mit OpenAI) ---")

    system_msg_reformulate = """
Du bist ein Experte im Umformulieren von Fragen über die DBLP-Literaturdatenbank.
Deine Aufgabe ist es, die ursprüngliche Nutzerfrage so umzuformulieren, dass sie präziser, eindeutiger und für eine anschließende automatische Analyse besser geeignet ist.
FOKUSSIERE dich darauf, die Absicht, die Entitäten und die Beziehungen klarer zu machen. Ändere nicht den Sinn der Frage und beantworte sie NICHT. Entferne unnötige Füllwörter.
Formuliere die Frage als knappen Befehl oder eine klare Frage.
Gib NUR die umformulierte Frage als einzelne Zeile zurück (ohne umgebende Anführungszeichen).
"""
    user_msg = create_user_msg_reformulate(nl_query)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Modell für Reformulierung
            messages=[
                {"role": "system", "content": system_msg_reformulate},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.1,
            max_tokens=150
        )
        reformulated_query = response.choices[0].message.content.strip().strip('"')
        print(f"Ursprüngliche Query: '{nl_query}'")
        print(f"Reformulierte Query: '{reformulated_query}'")
        return reformulated_query
    except Exception as e:
        print(f"Fehler bei der Query-Reformulierung (OpenAI): {e}")
        print("Fahre mit ursprünglicher Query fort.")
        return nl_query # Fallback

# --- Schritt 1b: SPARQL-Skelett mit Platzhaltern generieren (LLM) ---

def generate_sparql_skeleton_1b(reformulated_query: str, client):
    """
    Phase 1b: Generiert ein SPARQL-Template/Skelett mit Platzhaltern via OpenAI.
    Basierend auf der reformulierten Query aus 1a.
    """
    print("\n--- Phase 1b: SPARQL-Skelett mit Platzhaltern generieren (mit OpenAI) ---")

    # Standard-Präfixe, die das LLM kennen und verwenden sollte
    standard_prefixes_str = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
# Fügen Sie hier ggf. weitere hinzu, die als "Standard" gelten sollen
"""

    # Definition der Platzhalter-Konvention für den Prompt
    placeholder_convention = """
**Platzhalter-Regeln:**
1.  Ersetze spezifische **Entitätsnamen** (Personen, Paper-Titel, Venue-Namen etc.) durch Platzhalter im Format `<starturi:entity_TYPE_NameOhneLeerzeichen>`. Beispiel: "Zhang, Yu" (Typ person) wird zu `<starturi:entity_person_ZhangYu>`. "VLDB" (Typ venue) wird zu `<starturi:entity_venue_VLDB>`.
2.  Ersetze alle **DBLP-spezifischen Property- und Klassen-URIs** (alles, was nicht zu den Standard-Präfixen rdf, rdfs, owl, xsd, foaf gehört) durch Platzhalter im Format `<starturi:property_PropertyNameCamelCase>` oder `<starturi:class_ClassNameCamelCase>`. Beispiel: Die Property für "primary affiliation" wird zu `<starturi:property_primaryAffiliation>`, die Klasse für "paper" wird zu `<starturi:class_Publication>` oder `<starturi:class_Article>`.
3.  **Behalte** Standard-URIs wie `rdf:type`, `rdfs:label`, `owl:sameAs` bei.
4.  Verwende sinnvolle Variablennamen (z.B. `?paper`, `?author`, `?affiliation`, `?answer`).
5.  Generiere die korrekte SPARQL-Struktur (SELECT, ASK, COUNT, WHERE, FILTER, etc.) basierend auf der reformulierten Frage. Integriere notwendige PREFIX-Deklarationen.
"""

    system_msg_skeleton = f"""
Du bist ein SPARQL-Experte, der präzise, reformulierte SPARQL-Templates/Skelette mit Platzhaltern generiert.

**Kontext:**

* Du erhältst eine natürlichsprachliche Frage, die in eine reformulierte Query umgewandelt wurde.
* Dein Ziel ist es, ein SPARQL-Template zu erstellen, das die Struktur der Abfrage abbildet, aber spezifische Werte durch Platzhalter ersetzt.
* Verwende die untenstehenden Platzhalter-Regeln und SPARQL-Regeln, um ein valides und semantisch korrektes SPARQL-Template zu generieren.

**Platzhalter-Regeln:**

1.  Ersetze spezifische **Entitätsnamen** (Personen, Paper-Titel, Venue-Namen etc.) durch Platzhalter im Format `<starturi:entity_TYPE_NameOhneLeerzeichen>`. Beispiel: "Zhang, Yu" (Typ person) wird zu `<starturi:entity_person_ZhangYu>`. "VLDB" (Typ venue) wird zu `<starturi:entity_venue_VLDB>`.
2.  Ersetze alle **DBLP-spezifischen Property- und Klassen-URIs** (alles, was nicht zu den Standard-Präfixen rdf, rdfs, owl, xsd, foaf gehört) durch Platzhalter im Format `<starturi:property_PropertyNameCamelCase>` oder `<starturi:class_ClassNameCamelCase>`. Beispiel: Die Property für "primary affiliation" wird zu `<starturi:property_primaryAffiliation>`, die Klasse für "paper" wird zu `<starturi:class_Publication>` oder `<starturi:class_Article>`.
3.  **Behalte** Standard-URIs wie `rdf:type`, `rdfs:label`, `owl:sameAs` bei.
4.  Verwende sinnvolle Variablennamen (z.B. `?paper`, `?author`, `?affiliation`, `?answer`, `?x`, `?y`, `?z`).
5.  Generiere die korrekte SPARQL-Struktur (SELECT, ASK, COUNT, WHERE, FILTER, etc.) basierend auf der reformulierten Frage. Integriere notwendige PREFIX-Deklarationen.

**Wichtige SPARQL-Regeln:**

1.  Verwende IMMER `SELECT DISTINCT` für Abfragen, die Ergebnisse zurückgeben (nicht für ASK oder COUNT).
2.  Verwende IMMER `?answer` als primäre Ergebnisvariable in SELECT-Abfragen. Wenn die Frage explizit nach *mehreren* zusammengehörigen Ergebnissen fragt (z.B. Co-Autoren und Anzahl gemeinsamer Paper), verwende zusätzliche Variablen wie `?firstanswer`, `?secondanswer`, etc. Die Hauptentität sollte `?answer` oder `?firstanswer` sein.
3.  Verwende `ASK WHERE { ... }` für Ja/Nein-Fragen.
4.  Für Aggregationen (COUNT, AVG, MIN, MAX), benenne die Ergebnisvariable `?count` oder `?answer` (wenn es die einzige Ergebnisvariable ist). Bei SELECT Abfragen mit Aggregation verwende immer `AS`.
5.  Beachte, dass Abfragen die Anzahl von Entitäten oder Publikationen abfragen, verwende `COUNT`.
6.  Wenn nach Jahren gefragt wird, filtere diese numerisch abfragen ab.
7.  Wenn nach Titeln oder Publikationen gefragt wird, gib diese als Ergebnis zurück.
8.  Wenn nach Eigenschaften von Entitäten gefragt wird, gib diese zurück.
9.  Wenn nach Beziehungen zwischen Entitäten gefragt wird, gib die verbundenen Entitäten zurück.
10. Berücksichtige bei Jahresabfragen den korrekten Datentyp (xsd:integer).
11. Achte auf die korrekte Verwendung von UNION und OPTIONAL.
12.  Vermeide unnötige Verschachtelungen von Abfragen.
13.  Nutze `GROUP BY` in Verbindung mit Aggregatsfunktionen, wenn nötig.
14.  Verwende `FILTER` Klauseln, um Bedingungen an Variablen zu stellen (z.B., um Duplikate auszuschließen oder Werte zu vergleichen).
15.  Verwende BIND zur Zuweisung von Werten zu Variablen, insbesondere für bedingte Zuweisungen (IF-Anweisungen).
16.  Beachte die korrekte Syntax für Operatoren und Funktionen in SPARQL.
17. **(Wichtig für Autorschaft):** Für Abfragen nach Publikationen eines Autors (z.B. 'Was hat Person X geschrieben?'), verwende das **einfache Muster** `?answer <starturi:property_createdBy> <starturi:entity_person_AutorName>` (oder `authoredBy`). `?answer` ist die Publikations-URI. **Füge KEINE zusätzliche `rdf:type`-Überprüfung für `?answer` hinzu**, da die Property dies bereits impliziert, es sei denn, die Frage erfordert es explizit. Die Richtung ist **Publikation -> Property -> Autor**.



"""

    user_msg_skeleton = f"""
Reformulierte Frage: "{reformulated_query}"

Generiere das SPARQL-Template basierend auf den Regeln:
"""

    try:
        response = client.chat.completions.create(
            # GPT-4 wird für strukturelle Generierung dringend empfohlen!
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg_skeleton},
                {"role": "user", "content": user_msg_skeleton}
            ],
            temperature=0.0, # Möglichst deterministisch
        )
        sparql_template = response.choices[0].message.content.strip()
        # Bereinige ```
        sparql_template = re.sub(r'^```sparql\s*', '', sparql_template, flags=re.IGNORECASE)
        sparql_template = re.sub(r'```\s*$', '', sparql_template)
        print(f"Generierte SPARQL-Vorlage:\n{sparql_template}")
        return sparql_template
    except Exception as e:
        print(f"Fehler bei der SPARQL-Template-Generierung (OpenAI): {e}")
        return None