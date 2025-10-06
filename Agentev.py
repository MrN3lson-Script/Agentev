import os
import sys
import requests
import wikipedia
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_query_in_text(text, query, source_name):
    results = []
    lines = text.split('\n')
    for line_num, line in enumerate(lines, 1):
        if query.lower() in line.lower():
            results.append({
                "source": source_name,
                "line_number": line_num,
                "line_text": line.strip()[:150] + ('...' if len(line.strip()) > 150 else '')
            })
    return results

def search_files_in_folders(query, folder_paths):
    results = []
    for folder_path in folder_paths:
        if not os.path.isdir(folder_path):
            print(f"Path not found or invalid: {folder_path}. Skipping.")
            continue
            
        print(f"[LOCAL SEARCH] Searching for '{query}' in: {folder_path}...")
        
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                if not file_name.lower().endswith(('.txt', '.py', '.html', '.css', '.js', '.md', '.log', '.json', '.xml')):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                        file_results = find_query_in_text(file_content, query, file_path)
                        if file_results:
                            for res in file_results:
                                res['file'] = file_path
                                results.append(res)
                except Exception:
                    pass
                    
    return results

def search_website_content(base_url, query):
    print(f"[WEB PARSING] Searching for '{query}' on page: {base_url}")
    all_results = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; Agentev/1.0)'}
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status() 
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error accessing website: {e}"}

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    html_search_results = find_query_in_text(html_content, query, f"HTML ({base_url})")
    all_results.extend(html_search_results)

    script_tags = soup.find_all('script', src=True)

    for tag in script_tags:
        js_url_relative = tag.get('src')
        js_url_absolute = urljoin(base_url, js_url_relative)
        
        try:
            js_response = requests.get(js_url_absolute, headers=headers, timeout=10)
            js_response.raise_for_status()
            
            js_content = js_response.text
            js_search_results = find_query_in_text(js_content, query, f"JS ({js_url_absolute})")
            all_results.extend(js_search_results)
            
        except requests.exceptions.RequestException:
            pass 
            
    return all_results

def search_wikipedia(query):
    print("[WIKIPEDIA] Searching...")
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=3, auto_suggest=False, redirect=True)
        title = wikipedia.page(query, auto_suggest=False, redirect=True).title
        return {
            "source": "Wikipedia",
            "title": title,
            "text": summary
        }
        
    except wikipedia.exceptions.PageError:
        return {"source": "Wikipedia", "error": "Page not found."}
    except Exception as e:
        return {"source": "Wikipedia", "error": f"An error occurred: {e}"}

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
def ask_gemini(query):
    print("[GEMINI] Querying AI...")
    GEMINI_API_KEY = os.getenv("AIzaSyCLjlEI3bMu9zCIpcRrHVECZjHBVIXr1rM")

    if not GEMINI_API_KEY:
        return {"source": "Gemini AI", "error": "API key GEMINI_API_KEY is not set in environment variables."}

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"Answer the following question briefly and to the point in English: {query}"}
                ]
            }
        ]
    }

    url = f"{API_ENDPOINT}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        
        if response_data.get('candidates'):
            answer_text = response_data['candidates'][0]['content']['parts'][0]['text']
            return {"source": "Gemini AI", "answer": answer_text}
        elif response_data.get('error'):
            return {"source": "Gemini AI", "error": f"API Error: {response_data['error']['message']}"}
        else:
            return {"source": "Gemini AI", "error": "Failed to extract answer from JSON."}

    except requests.exceptions.RequestException as e:
        return {"source": "Gemini AI", "error": f"HTTP Request Error: {e}"}
    except Exception as e:
        return {"source": "Gemini AI", "error": f"Unexpected error: {e}"}

def agentev():
    os.system("clear")
    print("""Agentev: Search Tool
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                                                                    
                                  ./*.   /@@@@@@@@@                                 
                                , .@@@@@@@@@@@@@@@@@                                
                                @ @@@(  @@@@@@@@@@@@@                               
                                 @@@@@@@@@@@@@@%.@@@@@                              
                               @@@@@@@@@@@@(    @@@@@@@@@@@@@@                      
                                              %@@@@@@@@/.&                          
                           @@ &#   ,@@@@@@@@@@@@ &@@@@                              
                        %& @@@@@@@@@@@@@&/@@@@@@@@@@@@                              
                                .@ @@@@@@@@@@@@@@@@@@                               
                                   @@@@@@@@@@@@@@@@%                                
                                   .@@@@@@@@@@@@@@@@                                
                                   *@@@@@@@@@@@@@@@@.@@                             
                                    @@@@@@@@@@@@@@@  @@@@@                           
                                   ,  @ .@@@@@@%  @@@@@@@@@#                        
                                @   @@. %@@@@   @@@@@@@@@@@@@@@                     
                               @@@ @@@ @@@    @@@@@@@@@@@@@@@@@                     
                              @@@ @@@#&@@* @@@@@@@@@@@@@@@@@                       
                              @@ @@@ .@@    @@@@@@@@@@@@@@@&                        
                              @ @@@, @@@  ,@@@@@@@@@  ,@                            
                             @  @@@ @@@  @@@   @* @@@ ,                                                
                                                                                    
                                                                                    
                                                                                    
                                                                                    """)
    user_query = input("Enter search query: ")
    if not user_query:
        print("Query cannot be empty. Exiting.")
        return

    folder_paths_input = input(
        "Enter folders for local search, separated by comma (leave empty to skip): "
    )
    folder_paths = [p.strip() for p in folder_paths_input.split(',') if p.strip()]

    web_url = input("Enter URL for parsing (e.g., https://example.com, leave empty to skip): ")

    all_results = {}

    if folder_paths:
        all_results['local_search'] = search_files_in_folders(user_query, folder_paths)

    if web_url:
        all_results['web_parsing'] = search_website_content(web_url, user_query)

    all_results['wikipedia'] = search_wikipedia(user_query)
    all_results['gemini'] = ask_gemini(user_query)

    print("\n\n========================================================")
    print(f"OVERALL SEARCH RESULTS FOR QUERY: '{user_query}'")
    print("========================================================")

    if 'local_search' in all_results:
        local_res = all_results['local_search']
        if local_res:
            print("\n--- LOCAL FILES ---")
            for res in local_res:
                print(f"    [FILE]: {res['file']}")
                print(f"      Line No: {res['line_number']}")
                print(f"      Line Text: {res['line_text']}")
        else:
            print("\n--- LOCAL FILES: Nothing found. ---")

    if 'web_parsing' in all_results:
        web_res = all_results['web_parsing']
        if isinstance(web_res, dict) and 'error' in web_res:
            print(f"\n--- WEB PARSING: Error: {web_res['error']} ---")
        elif web_res:
            print("\n--- WEB PARSING (HTML/JS) ---")
            for res in web_res:
                print(f"    [SOURCE]: {res['source']}")
                print(f"      Line No: {res['line_number']}")
                print(f"      Text: {res['line_text']}")
        else:
            print("\n--- WEB PARSING: Nothing found. ---")

    wiki_res = all_results['wikipedia']
    print("\n--- WIKIPEDIA ---")
    if 'error' in wiki_res:
        print(f"    ERROR: {wiki_res['error']}")
    else:
        print(f"    [TITLE]: {wiki_res['title']}")
        print(f"    [SUMMARY]: {wiki_res['text']}")

    gemini_res = all_results['gemini']
    print("\n--- GEMINI AI ---")
    if 'error' in gemini_res:
        print(f"    ERROR: {gemini_res['error']}")
    else:
        print(f"    [RESPONSE]: {gemini_res['answer']}")

if __name__ == "__main__":
    agentev()
