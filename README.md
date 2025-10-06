# Agentev
Search tool

Agentev: A Multi-Source Search Agent
Agentev is a Python script that acts as a comprehensive search agent, integrating five distinct search modalities into a single command-line tool:
 * Local File Search: Scans specified local folders for the search query within the content of common text and code files (.txt, .py, .html, .css, .js, .md, .log, .json, .xml).
 * Website Parsing: Fetches and searches the content of a specific URL, including the main HTML page and any linked external JavaScript (.js) files.
 * Wikipedia Search: Queries the Wikipedia API to retrieve a brief summary and the title for the query.
Key Features:
 * Modular Functions: The script is structured with dedicated functions for each search type, making it easy to manage and expand.
 * Detailed Local Results: Provides the file path, line number, and a snippet of the line of text where the query was found in local files.
 * Error Handling: Includes robust handling for HTTP errors, file access issues, Wikipedia page errors, and missing API keys.
