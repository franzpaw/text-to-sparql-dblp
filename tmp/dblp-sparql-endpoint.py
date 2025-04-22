from SPARQLWrapper import SPARQLWrapper, JSON

def main():
    sparql = SPARQLWrapper("https://sparql.dblp.org/sparql")
    sparql.setQuery("""
        SELECT DISTINCT ?property
        WHERE {
          ?subject ?property ?object.
        }
        LIMIT 5
    """)
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            print("Successfully connected to the dblp SPARQL endpoint.")
            print("Some example properties:")
            for result in results["results"]["bindings"]:
                print(result["property"]["value"])
        else:
            print("Connected to the endpoint, but no results were returned for the basic query.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Could not connect to the dblp SPARQL endpoint.")

if __name__ == "__main__":
    main()


