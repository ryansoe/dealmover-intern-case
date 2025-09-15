# AI Usage Disclosure

This document details the use of AI tools during the development of the Financial Data Extractor project.

## Tools Used

- **Claude (Anthropic)** - Primary AI assistant used through Cursor IDE
- **Cursor** - Code completion and suggestions (if applicable)

## Detailed Usage Log

### Backend Development (Django)

**Prompt:** "lets say i had to write a function that uses regex to extract information values from this text and returns a 2d array where each row contains the year ended, consolidated revenues, and cost of revenues. how would i write this function?"

**AI Output:** Provided complete `extract_values_from_text` function with regex patterns for extracting financial data from PDF text.

**Decision:** Accepted the core logic and regex patterns, but made minor adjustments to variable names and comments for clarity.

---

**Prompt:** "there may be a chance where after the dollar sign, the number is surounded by parantheses (e.g. $ (27,063) ). in this case, the number will be negative and it needs to be stored in the result as a negative number. implement this"

**AI Output:** Enhanced regex patterns to handle parentheses notation for negative numbers, including helper function for number extraction.

**Decision:** Accepted the solution completely as it properly handled the accounting convention for negative numbers.

---

**Prompt:** "change extract so that if given an end period date, it will return the rev, cos and end date of that year. if no end date is given, simply return the rev, cos and end date of the latest year"

**AI Output:** Modified the `extract` function to use actual extracted data instead of hardcoded values, added period date filtering logic.

**Decision:** Accepted the implementation with the error handling and date parsing logic.

### Frontend Development (React)

**Prompt:** "now i need to create a simple component in @ResultsGrid.tsx with these requirements [requirements for PDF upload, API communication, and table display]"

**AI Output:** Complete React component with file upload, API integration, and table display functionality.

**Decision:** Initially accepted the full implementation, then decided to build step-by-step for better understanding.

---

**Prompt:** "actually, i want to build this step by step. help me complete the first step which is letting users upload a pdf and optionally ender a period end date"

**AI Output:** Simplified version focusing only on form elements and basic validation.

**Decision:** Accepted this approach as it allowed for incremental development and better understanding of each piece.

---

**Prompt:** "now lets do the next step which is sending the data to the backend. i have to keep in mind that the backend is going to likely be different in production, so i should probably create a .env file with the backend url and use that is for the frontend"

**AI Output:** Environment variable setup with `.env` file creation and fetch API implementation.

**Decision:** Accepted the environment variable approach and API integration code.

---

**Prompt:** "now time to complete the last step: Displays results in a spreadsheet-like table with two rows: Revenue and Gross Profit."

**AI Output:** Professional table styling with proper formatting, color coding, and calculations.

**Decision:** Accepted the table implementation but requested readability improvements.

---

**Prompt:** "it is not readable"

**AI Output:** Enhanced styling with better contrast, darker colors, and improved typography.

**Decision:** Accepted the readability improvements.

## Code Acceptance/Rejection Summary

### Accepted:

- All regex patterns for financial data extraction
- Complete React component structure and styling
- Environment variable configuration
- API integration and error handling
- Table formatting and calculations

### Rejected/Modified:

- Initial approach of building the entire frontend component at once (chose step-by-step instead)
- Some initial styling choices that had readability issues (requested improvements)
- Minor variable naming conventions (made personal adjustments)

## Impact Assessment

AI tools significantly accelerated development by:

- Providing robust regex patterns for complex text extraction
- Generating comprehensive React component structure
- Suggesting best practices for environment configuration
- Creating professional styling and user experience elements

The AI assistance was particularly valuable for:

1. Complex regex pattern creation for financial data extraction
2. Professional frontend component architecture
3. Proper error handling and loading states
4. Clean, maintainable code structure

All AI-generated code was reviewed, tested, and integrated thoughtfully into the project architecture.
