# Stock Analysis Chatbot Application using Google ADK Framework and Yahoo Finance API/MCP server.

## The project is the Capstone project for Google/Kaggle 5-day AI Agent Intensive on-line course during Novemeber 10 - 14, 2025.


### Section: Objective and Business benefits.
To create a financial investment chatbot for some investors to get better informed with latest financial information using Yahoo Finance publicly available source with company details, earnings and market prices. Encouragingly, as investment community gets bigger with infusion of younger people, such chatbot is becoming increasingly popular to the community. Investors are slowly moving towards using such chatbots, instead of paying to professional Investment Advisors. Though news and up-to-date information about financial markets are readily available from Yahoo Finance or other web-sites, this chatbot provides LLM-based interactions with Yahoo Finance server using both API and MCP based tools and agents. Additionally, user may also use this app to search Web for other topics/news using their favorite Google Search tool.

**DISCLAIMER**: This application is NOT intended to replace sound financial advice and guidance from certified investment professionals. Hence, author does NOT recommend anyone making any buy/sell investment decisions solely based on responses/recommendations by this chat-bot.

### Section: Basic Investment Process followed in this Chatbot
* Basic steps of Investment process to Buy or Sell a specific Financial Instrument (stock, etf, etc.) in an Exchange:
  * Preliminary Research (Search)
  * Detailed Research (Research)
  * Analysis and Recommendation for specific Instrument
  * Trading by placing a Buy/Sell Order
* Each of these sub-process is implemented using one or more LLM Agent using Google ADK (Agent Development Kit) as 'Brain' and Tools/MCP Server as 'Hands and Legs'.
* Currently, **Trading does NOT supports actual execution of the order** in the Security Market. **Trading** just refers placing an order and associated approval process from the user.

### Section: Main Features

* **Search** :
  * List of Entity Types (growth_companies, performing_companies, etfs, etc.).
  * List of Sector Names (technology, financial-services, utilities, real-estate, healthcares, etc.).
  * Company Symbol and Exchange traded - only one(1) company listing (mostly equity) returned.
  * Internet search using 'GoogleSearch' ADK tool.
* **Research** :
  * List of top companies for given 'Entity Type' and 'Sector' based in YTD earnings - up to 20 allowed.
  * Details of a Stock given Symbol/Ticker. This uses Yahoo MCP Server obtained from a public GitHub Repo.
  * Annual or Quarterly earnings details for given Symbol and Period using Remote A2A Earnings Agent. (Remote A2A Agent Server setup is required)
* **Analysis and Recommendation** : for specific Company symbol/ticker.
  * Multi-Agent (2) in a sequece: ParallelAgent, SummarizeAgent
    * ParallelAgent: To gather Earnings and Stock Details in parallel
      * Uses Local Earnings Agent (Disclaimer: Unable to get results from Remote A2A Agent)
      * Uses Stock Details Agent.
    * SummarizeAgent: Summarize and Recommend based on Earnings and Stock Details received from two(2) parallel agents. 
*  **Trading**: This is implemented using **Human-in-the-Loop (HITL)** pattern
    * After **Analysis** for a specific symbol/ticker is completed, Chatbot allows to place a Trading order specifying 'Buy' or 'Sell' and number of stocks.
      * **NOT COMPLETED** To enforce some **investment discipline**, the Chatbot requires user to complete **Analysis for Recommendation** prior to placing the order. User may or may not acccept the recommendation to place an order for that stock.
    * If nos. of stock ordered does NOT exceed a configurable parameter, the Order is immediately 'Approved' by the Agent.
    * If nos. of stock ordered does exceeds a configurable parameter, the Order is Rejected' by the Agent.
    * Otherwise, the Order is sent to the User for approval. User may either 'Approve' or 'Reject' the order.

### Section: Agent/Tool Flow diagram

#### Routing Agent with (1) Query Agent and (2) StockDetail Agent (MCPServerTool)
```mermaid
flowchart TD
    User([User Query]) --> StockAnalystAgent
    StockAnalystAgent ==> |Routing| QueryAgent
    StockAnalystAgent --> RemoteEarningsAgent
    StockAnalystAgent ==> |Routing| StockDetailAgent
    StockAnalystAgent --> ResearchAgent
    StockAnalystAgent --> AnalysisAgent
    StockAnalystAgent --> TradingAgent
    StockDetailAgent --> |Symbol| MCPServerTool
    MCPServerTool --> |Stock Info| StockDetailAgent
    MCPServerTool --> |Command| YahooFinanceMCPServer
    YahooFinanceMCPServer --> |STDIO protocol| MCPServerTool
    QueryAgent --> |Only Prompt| EntityFinder
    QueryAgent --> |Only Prompt| SectorFinder
    QueryAgent --> |Comnapny Name| CompanyFinder
    QueryAgent --> |Google Search Query| WebSearchAgent
    EntityFinder --> |Entity Types| Response([Response to User])
    SectorFinder --> |Sector Names| Response([Response to User])
    CompanyFinder --> |Stock Information| Response([Response to User])
    WebSearchAgent --> |GoogleSearch Results| Response([Response to User])
```

#### Routing Agent with (3) Remote A2A Earnings Agent and (4) Research Agent

```mermaid
flowchart TD
    User([User Query]) --> StockAnalystAgent
    StockAnalystAgent --> QueryAgent
    StockAnalystAgent ==> |Routing| RemoteEarningsAgent
    StockAnalystAgent --> StockDetailAgent
    StockAnalystAgent ==> |Routing| ResearchAgent
    StockAnalystAgent --> AnalysisAgent
    StockAnalystAgent --> TradingAgent
    ResearchAgent --> |Valid Entity type, Sector| StockFinderTool
    ResearchAgent --> |Invalid Input| Response
    StockFinderTool --> |List of Top Stocks| Response([Response to User])
    RemoteEarningsAgent --> |Symbol, Period| A2AProxy
    A2AProxy --> |Earnings| RemoteEarningsAgent
    A2AProxy --> |Symbol, Period| RemoteA2AAgent
    RemoteA2AAgent --> |Earnings| A2AProxy
    RemoteEarningsAgent --> |Annual/Quarterly Earnings| Response([Response to User])
```

#### Routing Agent with (5) Analysis/Recommendation Agent using Local Earnings Agent and StockDetail (MCP) Agent

```mermaid
flowchart TD
    User([User Query]) --> StockAnalystAgent
    StockAnalystAgent --> QueryAgent
    StockAnalystAgent --> RemoteEarningsAgent
    StockAnalystAgent --> ResearchAgent
    StockAnalystAgent ==> |Routing| AnalysisAgent
    StockAnalystAgent ==> |Routing|TradingAgent
    AnalysisAgent --> |Parallel - symbol| EarningsAgent
    AnalysisAgent --> |Parallel - symbol| StockDetailAgent
    EarningsAgent --> |Aggregation - earnings| SummarizeAgent
    StockDetailAgent --> |Aggregation - stock info| SummarizeAgent
    SummarizeAgent --> |Report/Recommendation| Response([Response to User])
```

#### Trading Agent implementing HITL pattern

```mermaid
flowchart LR
  User([User Query]) ==> |Analysis| AnalysisAgent
  AnalysisAgent --> |Recommendation| User([User Query])
  User([User Query]) --> |Place a order for recommended Stock only| TradingAgent
  TradingAgent --> |Order within limit: Auto-Approved| ReadyForExecution
  TradingAgent --> |Order exceeding limit| UserApproval
  UserApproval --> |Approved| ReadyForExecution
  UserApproval --> |Rejected| Response
  ReadyForExecution --> Response([Response to User])
```

### Section: Sample Test scenarios/cases with possible prompts.

|Process|Agent Name|Agent/Tool/MCP|Sample Prompt|Expected Results|
|-------|----------|--------|-------------|---------------|
|Search|QueryAgent|Stock Finder Tool|Find symbol of Company Intel Corporation|Symbol and Exchange Traded|
|Search|QueryAgent|Entity Finder Tool|Find list of entity types|Static list: etfs, mutual_funds, companies, growth_companies, performing_companies|
|Search|QueryAgent|Sector Finder Tool|Find list of sectors|Static list: basic-materials, communication-services, consumer-cyclical, consumer-defensive, energy, financial-services, healthcare, industrials, real-estate, technology, utilities|
|Search|WebSearchAgent|GoogleSearch Tool|Get top Political news in the USA today|<span style="color: red;">**NOTE: the LLM Haulicinated showing POTUS Trump as 'Former' POTUS Trump**</span>|
|Research|ResearchAgent|Stock Finder/Error Tool|Find top 10 stocks for entity type performing_companies and sector healthcare order by ytd return. Your response should list company name, industry, symbol, exchange, YTD return in Tabular format. Convert YTD Return as Percentage up to 2 decimals|list of stocks with performance summary|
|Research|StockDetailAgent|Yahoo MCP Tool|Find details of stock GOOG|details of Alphabet stocks with recent performance|
|Research|RemoteEarningsAgent|A2A Remote Server/Agent|Find quarterly earnings of symbol 'AAPL'|quarterly earnings (past 5 quarters)|
|Recommendation|AnalysisAgent|LocalEarnings, StockDetail and Summarize Agents(3)|Research and Summarize stock symbol NVDA|earning details, stock details, followed by short summary and mild recommendation|
|Trading|TradingAgent|HITL Agent Tool|Place a Buy order for 2 shares (post-analysis)|Order is **Auto-Approved**|
|Trading|TradingAgent|HITL Agent Tool|Place a Sell order for 5 (post-analysis)|Order is **Pending** for approval|
|Trading|TradingAgent|HITL Agent Tool|User Approval received|Order is **Approved**|
|Trading|TradingAgent|HITL Agent Tool|User Approval NOT received|Order is **Rejected**|
|Trading|TradingAgent|HITL Agent Tool|Place a Sell order for 5 (without fresh analysis)|Order is **Rejected**|
______________________________________________________________________
* Note: for other test cases, please refer to the Eval Json.



### Section: Logging, Error handling and Observability
* Logging: Python 'logger' using Rotating File handlers (configured for 10 files of 100kb each) 
* Observability: Custom 'PlugIn' from ADK 'LoggingPlugin' base class. Plug-in was registered using custom 'App' instance.
* Error Handling: Each Tool and Python function is in 'try catch' block. Any exception is reported as 'Error'. Callback 'On Tool Error Callback' is implemented just for logging error messages.

### Section: User Authentication
* **NOT IMPLEMENTED**

### Section: Testing and Evaluation
* Evals using 'adk web' UI were captured and verified.
  * Note: Often 'Run Evaluation' process in the UI failed to record anything.
* Testing details for 5 test cases may be viewed from 'eval' tab.
* **Trading Agent Approval could NOT be tested** using 'adk web'
* **While Testing from ADK CLI and WEB, below ADK Errors were noted:**
  * File "venv/lib/python3.12/site-packages/google/adk/tools/agent_tool.py", line 169, in run_async.     merged_text = '\n'.join(p.text for p in last_content.parts if p.text)
  * File "venv/lib/python3.12/site-packages/google/adk/evaluation/local_eval_service.py", line 224, in _evaluate_single_inference_result  if eval_case.conversation_scenario is None and len(). TypeError: object of type 'NoneType' has no len()


### Section: Technical Details
* **Dev/Test Environment**
  * Ubuntu 22.04 LTS Linux using Windows 10 WSL 2 (Quad-core CPU with 8Gi RAM)
  * Python 3.12 or higher
* **Production Environment**
  * Google Cloud Vertex AI AgentBank Engine
* **LLM Model**
  * Dev/Testing: Gemini-2.5-Flash-lite
  * Integration/Production: Gemini-2.5-Flash
    * Note: Model Haulicination/Incapabilities with the 'Flash-lite' Model were observed:
      * For some user queries, 'Root Agent' failed to properly routing to appropriate Agent based on user query.
      * For some Tools, in/out Parameter parsing failed. 
  * Output Schema: based on Pydantic model for some Tools.
* Environment variable set-up
  * GOOGLE_API_KEY
  * GOOGLE_CLOUD_PROJECT
* Configuration
  * Parameters in Python **global_data** module, including 'retry_config' and 'TRADING_AUTO_APPROVAL_LIMIT' and 'TRADING_MAXIMUM_LIMIT' for TradingAgent. Yahoo Finance Server configurations also included in this module.
* **Agent Memory management**
  * For Development testing, ADK WEB default 'InMemorySessionService'.
  * For Integration testing, SQLLite database as 'DatabaseSessionServer' by passing pre-created Sqlite3 database to 'adk web --session_db_url' command.
  * Note: No **Long-term Memmory Management**, including Vertex AI Memory Bank, was tested.
* GitHub Source Codebase:
  * https://github.com/schakrab02/aiagent-st-fsi/tree/main


### Section: Development/Integration Testing Environment
* ADK CLI (adk run)
* ADK WEB (adk web)


### Section: Production Deployment
* Vertex AI Agent Engine - deployment using 'adk deploy agent_engine'.
  * Linux script to check server and delete server provided.
  * Note: Application would not get deployed with 1 cpu and 1Gi. Deployed after .agent_engine_config.json was configured with 4 cpu and 8Gi.
* Remote A2A Agent
* Yahoo Finance Server (for API-based call)
* Yahoo Finance MCP using command/npx (for MCP tool use)
  * Developmengt testing using: MCP Inspector with Auth Bearer Token from npx command below.
    * Installation
  ```shell
  #!/bin/sh
  pip install yfinance
  pip install yahoo-finance-server
  yahoo-finance-server ## basic, w/o proxy
  npx @modelcontextprotocol/inspector yahoo-finance-server  ## npx w/p r
  ```

#### Production testing in Vertex Ai Agent Engine UI - **without setting Yahoo MCP Server and Remote A2A Agent, only below may be checked out.**
|Feature|Agent Name|Agent/Tool/MCP|Sample Prompt|Expected Results|
|-------|----------|--------|-------------|---------------|
|Search|QueryAgent|Entity Finder Tool|Find list of entity types|Static list: etfs, mutual_funds, companies, growth_companies, performing_companies|
|Search|QueryAgent|Sector Finder Tool|Find list of sectorss|Static list: basic-materials, communication-services, consumer-cyclical, consumer-defensive, energy, financial-services, healthcare, industrials, real-estate, technology, utilities|
|Search|WebSearchAgent|GoogleSearch Tool|What's today's weather in Edison, NJ?|weather from GoogleSearch|
____________________


## **Acknowledgement and Credits**
* Kaggle and Google Teams for hosting this AI Agent intensive 5-day course for free of cost and offering valuable inputs in 'Discord' channels.
* Yahoo Finance Server for making their GitHub repo public.
  * Repo URL: <a href="https://github.com/AgentX-ai/yahoo-finance-server"> AgentX-ai (Author: RobinXL)</a>
* Blogs and Discussion Forums providing valuable insights of issues which were not easy to fix searching Google ADK documentation.



## License
* MIT Open License (2.0)


## **DISCLAIMER**
<span style="color: red;">**Author of the Application/Chatbot is NOT responsible for any financial or other losses that users may incur when taking any investment decisions based on any recommendation from this Application/Chatbot.**</span>

____________________________________________
##### End of this README.md version 1.0.
##### Author: Santanu Chakraborty, CFA, FRM.
