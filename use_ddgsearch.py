from ddgsearch import ddgsearch
import json

query = "how to make a great pastrami sandwich"

# search duckduckgo and scrape the results

results = ddgsearch(query, numresults=4, clean_with_llm=True)

# print the results
print (f"Results: {json.dumps(results, indent=2)}")
