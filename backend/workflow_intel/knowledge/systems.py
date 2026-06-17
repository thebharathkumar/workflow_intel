"""Catalog of enterprise systems with integration metadata.

Each entry carries the data the Integration Agent needs to emit a credible integration plan:
canonical name, recognition aliases, category, vendor, supported auth methods, event triggers,
webhook availability, key data objects, and the MCP opportunity.
"""

from __future__ import annotations

from typing import Any

SYSTEM_CATALOG: dict[str, dict[str, Any]] = {
    "Salesforce": {
        "aliases": ["salesforce", "sfdc", "sales cloud"],
        "category": "CRM",
        "vendor": "Salesforce",
        "auth": ["OAuth 2.0 (JWT bearer)", "Connected App"],
        "events": ["record.created", "record.updated", "opportunity.stage_changed"],
        "webhooks": ["Platform Events", "Change Data Capture", "Outbound Messages"],
        "data_objects": ["Account", "Contact", "Opportunity", "Contract", "Case"],
        "mcp": "Expose Salesforce SOQL queries and record CRUD as MCP tools for agents.",
    },
    "HubSpot": {
        "aliases": ["hubspot"],
        "category": "CRM / Marketing",
        "vendor": "HubSpot",
        "auth": ["OAuth 2.0", "Private App token"],
        "events": ["contact.creation", "deal.propertyChange"],
        "webhooks": ["Webhooks API (subscriptions)"],
        "data_objects": ["Contact", "Company", "Deal", "Ticket"],
        "mcp": "MCP tools for CRM enrichment and deal-stage updates.",
    },
    "Slack": {
        "aliases": ["slack"],
        "category": "Messaging",
        "vendor": "Salesforce",
        "auth": ["OAuth 2.0 (bot token)", "App-level token"],
        "events": ["message.channels", "app_mention", "reaction_added"],
        "webhooks": ["Events API", "Incoming Webhooks", "Slash Commands"],
        "data_objects": ["Message", "Channel", "User"],
        "mcp": "MCP server for posting notifications and reading channel context.",
    },
    "Microsoft Teams": {
        "aliases": ["microsoft teams", "ms teams", "teams"],
        "category": "Messaging",
        "vendor": "Microsoft",
        "auth": ["OAuth 2.0 (Microsoft Entra ID)", "Graph API permissions"],
        "events": ["channelMessage.created", "chatMessage.created"],
        "webhooks": ["Graph change notifications", "Incoming Webhook connectors"],
        "data_objects": ["Message", "Channel", "Team"],
        "mcp": "MCP tools over Microsoft Graph for Teams messaging.",
    },
    "Jira": {
        "aliases": ["jira"],
        "category": "Issue Tracking",
        "vendor": "Atlassian",
        "auth": ["OAuth 2.0 (3LO)", "API token (basic)"],
        "events": ["jira:issue_created", "jira:issue_updated", "comment_created"],
        "webhooks": ["Jira Webhooks"],
        "data_objects": ["Issue", "Project", "Sprint", "Comment"],
        "mcp": "MCP tools for ticket triage, creation, and transition.",
    },
    "ServiceNow": {
        "aliases": ["servicenow", "service now", "snow"],
        "category": "ITSM",
        "vendor": "ServiceNow",
        "auth": ["OAuth 2.0", "Basic auth", "Mutual TLS"],
        "events": ["incident.inserted", "incident.updated"],
        "webhooks": ["Business Rules → REST", "Flow Designer webhooks"],
        "data_objects": ["Incident", "Change Request", "CMDB CI"],
        "mcp": "MCP tools for incident enrichment and routing.",
    },
    "SharePoint": {
        "aliases": ["sharepoint", "share point"],
        "category": "Document Management",
        "vendor": "Microsoft",
        "auth": ["OAuth 2.0 (Microsoft Entra ID)", "Graph API"],
        "events": ["driveItem.created", "driveItem.updated"],
        "webhooks": ["Graph change notifications"],
        "data_objects": ["Document", "List Item", "Library"],
        "mcp": "MCP tools for document retrieval and metadata tagging.",
    },
    "SAP": {
        "aliases": ["sap", "s/4hana", "sap erp"],
        "category": "ERP",
        "vendor": "SAP",
        "auth": ["OAuth 2.0", "SAML", "Principal propagation"],
        "events": ["BusinessEvent (Event Mesh)"],
        "webhooks": ["SAP Event Mesh", "OData notifications"],
        "data_objects": ["Purchase Order", "Invoice", "Vendor", "GL Entry"],
        "mcp": "MCP tools over OData/BAPIs for finance and procurement reads.",
    },
    "Snowflake": {
        "aliases": ["snowflake"],
        "category": "Data Warehouse",
        "vendor": "Snowflake",
        "auth": ["Key-pair", "OAuth 2.0", "External browser SSO"],
        "events": ["Streams + Tasks", "Snowpipe notifications"],
        "webhooks": ["Notification integrations (cloud queues)"],
        "data_objects": ["Table", "View", "Stage"],
        "mcp": "MCP tool for governed analytical SQL (read-only role).",
    },
    "Databricks": {
        "aliases": ["databricks"],
        "category": "Data / ML Platform",
        "vendor": "Databricks",
        "auth": ["OAuth 2.0", "Personal Access Token", "Service principal"],
        "events": ["Jobs API run state", "Lakehouse Federation"],
        "webhooks": ["Job webhooks", "Model Registry webhooks"],
        "data_objects": ["Table (Unity Catalog)", "Job", "Model"],
        "mcp": "MCP tool for feature/store reads and job triggers.",
    },
    "Google Workspace": {
        "aliases": ["google workspace", "gsuite", "g suite", "google drive", "drive"],
        "category": "Productivity Suite",
        "vendor": "Google",
        "auth": ["OAuth 2.0", "Service account (domain-wide delegation)"],
        "events": ["Drive push notifications", "Gmail watch"],
        "webhooks": ["Push notifications (Pub/Sub)"],
        "data_objects": ["Doc", "Sheet", "Drive File", "Calendar Event"],
        "mcp": "MCP tools for Docs/Sheets/Drive operations.",
    },
    "Microsoft 365": {
        "aliases": ["microsoft 365", "office 365", "m365", "o365"],
        "category": "Productivity Suite",
        "vendor": "Microsoft",
        "auth": ["OAuth 2.0 (Microsoft Entra ID)", "Graph API"],
        "events": ["Graph change notifications"],
        "webhooks": ["Graph subscriptions"],
        "data_objects": ["Mail", "Document", "Calendar", "User"],
        "mcp": "MCP tools over Microsoft Graph.",
    },
    "Gmail": {
        "aliases": ["gmail"],
        "category": "Email",
        "vendor": "Google",
        "auth": ["OAuth 2.0", "Service account"],
        "events": ["Gmail watch (Pub/Sub)"],
        "webhooks": ["Pub/Sub push"],
        "data_objects": ["Message", "Thread", "Label"],
        "mcp": "MCP tool for email triage and drafting.",
    },
    "Outlook": {
        "aliases": ["outlook", "exchange"],
        "category": "Email",
        "vendor": "Microsoft",
        "auth": ["OAuth 2.0 (Microsoft Entra ID)", "Graph API"],
        "events": ["Graph mail change notifications"],
        "webhooks": ["Graph subscriptions"],
        "data_objects": ["Message", "Event", "Contact"],
        "mcp": "MCP tool for mailbox triage over Graph.",
    },
    "Excel": {
        "aliases": ["excel", "spreadsheet", "spreadsheets", "xlsx"],
        "category": "Spreadsheet",
        "vendor": "Microsoft",
        "auth": ["OAuth 2.0 (Graph)", "File share"],
        "events": ["Workbook change (Graph)"],
        "webhooks": ["Graph subscriptions"],
        "data_objects": ["Worksheet", "Table", "Range"],
        "mcp": "MCP tool for structured read/write of workbooks.",
    },
    "Google Sheets": {
        "aliases": ["google sheets", "sheets"],
        "category": "Spreadsheet",
        "vendor": "Google",
        "auth": ["OAuth 2.0", "Service account"],
        "events": ["Drive change + Apps Script triggers"],
        "webhooks": ["Apps Script / Pub/Sub"],
        "data_objects": ["Sheet", "Range"],
        "mcp": "MCP tool for sheet read/write.",
    },
    "DocuSign": {
        "aliases": ["docusign"],
        "category": "E-Signature",
        "vendor": "Docusign",
        "auth": ["OAuth 2.0 (JWT)", "Connect"],
        "events": ["envelope-completed", "envelope-sent"],
        "webhooks": ["DocuSign Connect"],
        "data_objects": ["Envelope", "Recipient", "Document"],
        "mcp": "MCP tool for envelope status and signature routing.",
    },
    "Workday": {
        "aliases": ["workday"],
        "category": "HCM",
        "vendor": "Workday",
        "auth": ["OAuth 2.0", "ISU credentials"],
        "events": ["Business Process events"],
        "webhooks": ["Workday integrations (EIB/Studio)"],
        "data_objects": ["Worker", "Position", "Absence"],
        "mcp": "MCP tool for HR record reads.",
    },
    "NetSuite": {
        "aliases": ["netsuite"],
        "category": "ERP",
        "vendor": "Oracle",
        "auth": ["OAuth 2.0 (TBA)", "Token-based"],
        "events": ["SuiteScript user events"],
        "webhooks": ["RESTlet callbacks"],
        "data_objects": ["Invoice", "Customer", "Sales Order"],
        "mcp": "MCP tool for finance object reads/writes.",
    },
    "Zendesk": {
        "aliases": ["zendesk"],
        "category": "Customer Support",
        "vendor": "Zendesk",
        "auth": ["OAuth 2.0", "API token"],
        "events": ["ticket.created", "ticket.updated"],
        "webhooks": ["Zendesk Webhooks + Triggers"],
        "data_objects": ["Ticket", "User", "Organization"],
        "mcp": "MCP tool for ticket triage and macro application.",
    },
    "GitHub": {
        "aliases": ["github"],
        "category": "Source Control",
        "vendor": "GitHub",
        "auth": ["OAuth 2.0", "GitHub App", "Fine-grained PAT"],
        "events": ["push", "pull_request", "issues"],
        "webhooks": ["Repository webhooks"],
        "data_objects": ["Pull Request", "Issue", "Commit"],
        "mcp": "MCP server for repo, PR, and issue operations.",
    },
    "Confluence": {
        "aliases": ["confluence"],
        "category": "Knowledge Base",
        "vendor": "Atlassian",
        "auth": ["OAuth 2.0 (3LO)", "API token"],
        "events": ["page_created", "page_updated"],
        "webhooks": ["Confluence webhooks"],
        "data_objects": ["Page", "Space", "Attachment"],
        "mcp": "MCP tool for knowledge retrieval and authoring.",
    },
    "Stripe": {
        "aliases": ["stripe"],
        "category": "Payments",
        "vendor": "Stripe",
        "auth": ["API key", "OAuth (Connect)"],
        "events": ["payment_intent.succeeded", "invoice.paid"],
        "webhooks": ["Stripe Webhooks (signed)"],
        "data_objects": ["PaymentIntent", "Invoice", "Customer"],
        "mcp": "MCP tool for billing reads (no write without approval).",
    },
}


def match_systems(text: str) -> list[dict[str, Any]]:
    """Return catalog entries (with canonical ``name``) referenced in ``text``.

    Matches are ordered by first appearance and de-duplicated. Longer aliases are tried first
    so "microsoft teams" wins over a bare "teams".
    """
    lowered = text.lower()
    found: list[tuple[int, str]] = []
    for name, meta in SYSTEM_CATALOG.items():
        best: int | None = None
        for alias in sorted(meta["aliases"], key=len, reverse=True):
            idx = lowered.find(alias)
            if idx != -1:
                best = idx if best is None else min(best, idx)
        if best is not None:
            found.append((best, name))
    found.sort(key=lambda t: t[0])
    return [{"name": name, **SYSTEM_CATALOG[name]} for _, name in found]
