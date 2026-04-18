from repo_analysis_tools.mcp.contracts.anchors import ANCHOR_CONTRACTS
from repo_analysis_tools.mcp.contracts.evidence import EVIDENCE_CONTRACTS
from repo_analysis_tools.mcp.contracts.export import EXPORT_CONTRACTS
from repo_analysis_tools.mcp.contracts.impact import IMPACT_CONTRACTS
from repo_analysis_tools.mcp.contracts.report import REPORT_CONTRACTS
from repo_analysis_tools.mcp.contracts.scan import SCAN_CONTRACTS
from repo_analysis_tools.mcp.contracts.scope import SCOPE_CONTRACTS
from repo_analysis_tools.mcp.contracts.slice import SLICE_CONTRACTS


DOMAIN_CONTRACTS = {
    "scan": SCAN_CONTRACTS,
    "scope": SCOPE_CONTRACTS,
    "anchors": ANCHOR_CONTRACTS,
    "slice": SLICE_CONTRACTS,
    "evidence": EVIDENCE_CONTRACTS,
    "impact": IMPACT_CONTRACTS,
    "report": REPORT_CONTRACTS,
    "export": EXPORT_CONTRACTS,
}

CONTRACT_BY_NAME = {
    contract.name: contract
    for contracts in DOMAIN_CONTRACTS.values()
    for contract in contracts
}
