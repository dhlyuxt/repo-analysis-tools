from repo_analysis_tools.mcp.contracts.scan import SCAN_CONTRACTS
from repo_analysis_tools.mcp.contracts.query import QUERY_CONTRACTS


DOMAIN_CONTRACTS = {
    "scan": SCAN_CONTRACTS,
    "query": QUERY_CONTRACTS,
}

CONTRACT_BY_NAME = {
    contract.name: contract
    for contracts in DOMAIN_CONTRACTS.values()
    for contract in contracts
}
