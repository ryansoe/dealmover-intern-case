# Assumptions Made:

Year Format: Years are always 4 digits (e.g., "2023", "2024")
Currency Format: Dollar amounts are preceded by "$" symbol
Negative Numbers: Parentheses indicate negative values
Number Formatting: Numbers may contain commas (e.g., "307,394")
Table Layout: Financial data appears in a consistent table format with "Year Ended December 31" header

# Decision: Regex Pattern Matching vs. Table Parsing Libraries

**Choice Made:** Used regex patterns to extract financial data from PDF text.

**Alternative Considered:** Libraries like `pandas` for table parsing or specialized PDF table extraction tools like `tabula-py`.

**Trade-offs:**

**Pros of Regex Approach:**

- Lightweight and fast execution
- No additional heavy dependencies
- Fine-grained control over what gets extracted
- Works well with the specific format of 10-K filings
- Easy to debug and modify patterns

**Cons of Regex Approach:**

- Brittle - breaks if document format changes significantly
- Requires manual pattern crafting for each data type
- Less flexible for different document structures
- May miss data if formatting varies slightly

**Why I Chose Regex:**
Given that this is a proof-of-concept focused on 10-K filings, regex provided the right balance of simplicity and control. The financial data in these documents follows a fairly consistent format, making regex patterns reliable for this use case.

# Decision: Default to December 31st format (YYYY-12-31) when constructing period end dates.

**Assumption:** Most financial periods end on December 31st, which is standard for annual reports.

**Alternative:** Could have parsed actual dates from the document, but this adds complexity for minimal benefit in the target use case.
