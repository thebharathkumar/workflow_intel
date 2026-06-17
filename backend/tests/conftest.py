import pytest

EXAMPLE = (
    "Sales emails contracts to Legal. Legal reviews and sends comments back. "
    "Sales updates Salesforce. Finance receives a Slack notification. "
    "Contracts are stored in SharePoint."
)


@pytest.fixture
def example_text() -> str:
    return EXAMPLE
