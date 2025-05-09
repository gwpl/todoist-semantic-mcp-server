## Programmer Instructions

### Enhancements Required

1. **Add Limit Parameter to API Calls:**
   - Introduce an obligatory `limit` parameter to all API calls that have the potential to return a large number of records or results. This will ensure the client receives a manageable amount of data, preventing system overloads and improving usability.
   - Identify calls like `list-projects`, `list-tasks`, and `list-labels` as candidates for this enhancement. These calls are typically prone to returning large datasets, especially for long-term users of Todoist.

2. **Implement Fuzzy Search Functionality:**
   - Develop `fuzzy_search` functions for projects and tasks, incorporating a `limit` parameter for results.
   - **Project Fuzzy Search:**
     - Fetch and cache all projects from the server.
     - Perform local fuzzy search on cached data for efficiency and effectiveness.
   - **Task Fuzzy Search:**
     - For tasks within a project, implement similar logic by caching all tasks of a project and executing the fuzzy search on the local dataset.
     - For a fuzzy search across tasks and projects, first perform search on projects with provided project name, if zero matches then perform a fuzzy search for projects (using already defined previously described routine), then within those projects perform task-level fuzzy searches. Combine results before final fuzzy sorting to be presented to the user.
   - These fuzzy searches should be optimized to handle short keyword sequences by initially searching full sequence, if not finding any , then switching to partial sequence queries to todoist server by  downgrading initial query sequence to subset sequences (e.g. trying sequence without word i=0,1,2... etc), and finally, if needed, single words form original query to ensure comprehensive cache construction... (stop once enough tasks cached from all projects matching fuzzy search... 

3. All functions that may return records with many different fields, are required to provide optional parameter that allow user to provide list of fields they want to recieve for each record (otherwise default all should be returned)

4. **Environment Configuration with TODOIST_SERVER_CONFIG_JSON:**
   - Create an environment variable `TODOIST_SERVER_CONFIG_JSON` to hold custom execution parameters such as defaults for limits and search thresholds. If not present, the system should fall back to defined default values.

### Programming

Keep programing style of codebase, take care to abstract into small reusable readable functions when possible (e.g. cache related logic, or filtering which fields to return in each records etc)

### Update README.md

#### Expanded README.md Sections

- **Semantic Usability:**
  - Highlight the focus on creating a more semantic and user-friendly interface by integrating result limits and fuzzy searching to cope with the imprecise nature of user inputs, especially beneficial for LLMs and human interaction.

- **Server Caching and Performance:**
  - Explain the server-side caching technique implemented for efficient fuzzy search operations, noting that these optimizations prioritize reduced round-trips and better resource use.

- **Environment Configuration:**
  - Guide users on setting the `TODOIST_SERVER_CONFIG_JSON` variable for customizing performance parameters, influencing search/result behavior directly without code modification.

### Additional Proposed API Calls

- **`limited_search_projects(max_results=...)`:** Retrieves projects with a configurable upper limit on the number of results.
- **`limited_search_tasks(max_results=...)`:** Similar functionality for task searches.
- **`fuzzy_search_projects(max_results=...)`:** Searches projects using fuzzy logic to accommodate non-exact inputs.
- **`fuzzy_search_tasks(project_name=<fuzzy_project_name>, max_results=...)`:** Combined fuzzy search across tasks and project names, ideal for uncertain inputs.

These enhancements should significantly improve the responsiveness and usability of the MCP Todoist server, benefiting both advanced users and LLMs by delivering streamlined, relevant, and manageable datasets.

