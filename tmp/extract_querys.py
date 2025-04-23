import json
import re

def extract_sparql_queries(data):
    """
    Extracts SPARQL queries from the 'query' field in the data.

    Args:
        data (dict): A dictionary containing the input data.

    Returns:
        list: A list of SPARQL queries.
    """
    sparql_queries = []
    for item in data["questions"]:
        if "question" in item and "string" in item["question"]:
            sparql_queries.append(item["question"]["string"])
    return sparql_queries

def main():
    # Load the data from the file
    filename = "questions.txt"  # Replace with the actual filename
    output_filename = "extract_questions.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sparql_queries = extract_sparql_queries(data)

    # Print the extracted queries to a new file
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for query in sparql_queries:
            outfile.write(query + '\n')  # Add newline to separate queries

    print(f"Extracted queries written to {output_filename}")

if __name__ == "__main__":
    main()