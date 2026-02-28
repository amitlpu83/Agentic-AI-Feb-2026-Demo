"""
HR Policies MCP Server — built with FastMCP
Exposes company HR policies as MCP resources and tools.

Run for Inspector debugging:
    mcp dev hr_mcp_server.py

Run standalone (stdio):
    python hr_mcp_server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HR Policies Server")

# ─────────────────────────────────────────────
# HR Policy Data (moved from hr_agent.py)
# ─────────────────────────────────────────────

HR_POLICIES: dict[str, str] = {
    "remote_work": """Remote Work Policy:
- Employees may work remotely up to 3 days per week
- Remote work requires manager approval for the arrangement
- Core collaboration hours: 10 am–3 pm in your local timezone
- Must be reachable via Slack/Teams during core hours
- Home-office equipment allowance: $500 per year
- VPN must be used when accessing company systems remotely""",

    "leave": """Leave & Time-Off Policy:
- Annual leave: 15 days (accrued monthly, max carry-over 5 days)
- Sick leave: 10 days per year (no carry-over)
- Personal leave: 3 days per year
- Parental leave: 16 weeks fully paid (primary caregiver); 4 weeks (secondary)
- Bereavement: 5 days for immediate family, 3 days for extended family
- Leave requests require at least 2 weeks advance notice (except sick/emergency)
- All requests must be submitted through the HR portal""",

    "performance": """Performance Review Policy:
- Annual reviews held every December
- Mid-year check-ins held every June
- Ratings on a 1–5 scale (1 = Below Expectations, 5 = Exceptional)
- 360-degree feedback collected from peers and direct reports
- Performance Improvement Plans (PIP) issued for ratings below 2
- Merit salary increases tied to performance ratings
- Promotion eligibility reviewed annually""",

    "code_of_conduct": """Code of Conduct:
- Treat all colleagues with respect and professionalism
- Zero tolerance for harassment, discrimination, or bullying
- Conflicts of interest must be disclosed to HR immediately
- Confidential information must never be shared outside authorised channels
- Report violations to HR or the anonymous Ethics Hotline
- Retaliation against anyone who reports in good faith is strictly prohibited
- Violations may result in disciplinary action up to and including termination""",

    "compensation": """Compensation & Benefits Policy:
- Salaries reviewed annually following performance reviews
- Equity grants vest over 4 years with a 1-year cliff
- Health insurance: company covers 90% of premium (employee + dependants)
- 401(k): company matches up to 4% of salary
- Annual learning & development budget: $1,500 per employee
- Gym/wellness reimbursement: $50/month""",
}

# ─────────────────────────────────────────────
# Resources — policy documents
# ─────────────────────────────────────────────

@mcp.resource("hr://policies/{topic}")
def get_policy_resource(topic: str) -> str:
    """Get a specific HR policy document by topic.

    Available topics: remote_work, leave, performance, code_of_conduct, compensation
    """
    if topic in HR_POLICIES:
        return HR_POLICIES[topic]
    available = ", ".join(HR_POLICIES.keys())
    return f"Policy '{topic}' not found. Available topics: {available}"


@mcp.resource("hr://policies")
def list_policies_resource() -> str:
    """List all available HR policy topics."""
    lines = ["Available HR Policy Topics:\n"]
    for topic in HR_POLICIES:
        lines.append(f"  • {topic}")
    lines.append("\nAccess any policy at: hr://policies/<topic>")
    return "\n".join(lines)

# ─────────────────────────────────────────────
# Tools — callable by LLM / MCP Inspector
# ─────────────────────────────────────────────

@mcp.tool()
def get_hr_policy(topic: str) -> str:
    """Retrieve company HR policy text for a given topic.

    Args:
        topic: Policy topic name. One of: remote_work, leave, performance,
               code_of_conduct, compensation. Partial names are accepted.
    """
    key = topic.lower().replace(" ", "_")

    # Exact match
    if key in HR_POLICIES:
        return HR_POLICIES[key]

    # Fuzzy match
    for k, policy in HR_POLICIES.items():
        if key in k or k in key:
            return policy

    available = ", ".join(HR_POLICIES.keys())
    return f"Policy '{topic}' not found. Available topics: {available}"


@mcp.tool()
def list_hr_policies() -> str:
    """List all available HR policy topics with short descriptions."""
    descriptions = {
        "remote_work": "Remote work days, core hours, equipment allowance",
        "leave": "Annual, sick, personal, parental, and bereavement leave",
        "performance": "Review cycle, ratings scale, PIPs, merit increases",
        "code_of_conduct": "Respect, harassment, conflicts of interest, reporting",
        "compensation": "Salary reviews, equity, health insurance, 401(k), L&D budget",
    }
    lines = ["HR Policy Topics:\n"]
    for topic, desc in descriptions.items():
        lines.append(f"  {topic}: {desc}")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
