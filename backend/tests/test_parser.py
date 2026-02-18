import pytest
import os
from core.views import extract_values_from_text

class TestFinancialDataParser:
    
    @pytest.fixture
    def sample_text(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'extracted_text.txt')
        
        with open(test_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def test_extract_values_basic_functionality(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        for row in result:
            assert len(row) == 3
            assert isinstance(row[0], str)
            assert isinstance(row[1], str)
            assert isinstance(row[2], str)
    
    def test_extract_correct_years(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        assert len(result) == 2
        
        years = [row[0] for row in result]
        assert '2023' in years
        assert '2024' in years
        
        assert result[0][0] == '2023'
        assert result[1][0] == '2024'
    
    def test_extract_correct_financial_values(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        data_2023 = next(row for row in result if row[0] == '2023')
        data_2024 = next(row for row in result if row[0] == '2024')
        
        assert data_2023[1] == '307394'
        assert data_2023[2] == '133332'
        
        assert data_2024[1] == '350018'
        assert data_2024[2] == '146306'
    
    def test_numbers_have_no_commas(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        for row in result:
            revenue = row[1]
            cost = row[2]
            
            assert ',' not in revenue
            assert ',' not in cost
            
            assert revenue.lstrip('-').isdigit()
            assert cost.lstrip('-').isdigit()
    
    def test_empty_text_returns_empty_list(self):
        result = extract_values_from_text("")
        assert result == []
        
        result = extract_values_from_text("No financial data here")
        assert result == []
    
    def test_missing_year_header_returns_empty(self):
        invalid_text = """
        Some random text
        Consolidated revenues $ 100,000 $ 200,000
        Cost of revenues $ 50,000 $ 75,000
        """
        result = extract_values_from_text(invalid_text)
        assert result == []
    
    def test_missing_revenue_data_returns_error(self):
        invalid_text = """
        Year Ended December 31,
        2023 2024
        Cost of revenues $ 50,000 $ 75,000
        """
        result = extract_values_from_text(invalid_text)
        assert isinstance(result, dict)
        assert 'error' in result
        assert result['stage'] == 'revenue'

    def test_missing_cost_data_returns_error(self):
        invalid_text = """
        Year Ended December 31,
        2023 2024
        Consolidated revenues $ 100,000 $ 200,000
        """
        result = extract_values_from_text(invalid_text)
        assert isinstance(result, dict)
        assert 'error' in result
        assert result['stage'] == 'cost'
    
    def test_negative_numbers_with_parentheses(self):
        text_with_negatives = """
        Year Ended December 31,
        2023 2024
        Consolidated revenues $ 100000 $ (50000)
        Cost of revenues $ (25000) $ 30000
        """
        result = extract_values_from_text(text_with_negatives)
        
        if result:
            for row in result:
                revenue = row[1]
                cost = row[2]
                
                assert revenue.lstrip('-').isdigit()
                assert cost.lstrip('-').isdigit()
    
    def test_data_types_and_format(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        assert isinstance(result, list)
        
        for i, row in enumerate(result):
            assert isinstance(row, list)
            assert len(row) == 3
            
            year, revenue, cost = row
            
            assert isinstance(year, str)
            assert len(year) == 4
            assert year.isdigit()
            
            assert isinstance(revenue, str)
            assert isinstance(cost, str)
    
    # --- robustness tests ---

    def test_non_december_year_end(self):
        text = (
            "Year Ended March 31,\n"
            "2023 2024\n"
            "Consolidated revenues $ 100,000 $ 200,000\n"
            "Cost of revenues $ 50,000 $ 75,000\n"
        )
        result = extract_values_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0][0] == '2023'
        assert result[1][0] == '2024'

    def test_net_revenues_label(self):
        text = (
            "Year Ended December 31,\n"
            "2023 2024\n"
            "Net revenues $ 100,000 $ 200,000\n"
            "Cost of revenues $ 50,000 $ 75,000\n"
        )
        result = extract_values_from_text(text)
        assert isinstance(result, list)
        assert result[0][1] == '100000'
        assert result[1][1] == '200000'

    def test_cost_of_goods_sold_label(self):
        text = (
            "Year Ended December 31,\n"
            "2023 2024\n"
            "Consolidated revenues $ 100,000 $ 200,000\n"
            "Cost of goods sold $ 50,000 $ 75,000\n"
        )
        result = extract_values_from_text(text)
        assert isinstance(result, list)
        assert result[0][2] == '50000'
        assert result[1][2] == '75000'

    def test_fiscal_year_prefix(self):
        text = (
            "Fiscal Year Ended December 31,\n"
            "2023 2024\n"
            "Consolidated revenues $ 100,000 $ 200,000\n"
            "Cost of revenues $ 50,000 $ 75,000\n"
        )
        result = extract_values_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_three_years_extracted(self):
        text = (
            "Year Ended December 31,\n"
            "2022 2023 2024\n"
            "Consolidated revenues $ 282,836 $ 307,394 $ 350,018\n"
            "Cost of revenues $ 110,959 $ 133,332 $ 146,306\n"
        )
        result = extract_values_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0][0] == '2022'
        assert result[1][0] == '2023'
        assert result[2][0] == '2024'
        assert result[0][1] == '282836'
        assert result[2][1] == '350018'

    # --- end robustness tests ---

    def test_integration_with_real_data(self, sample_text):
        result = extract_values_from_text(sample_text)
        
        assert len(result) == 2
        
        years = {row[0]: {'revenue': row[1], 'cost': row[2]} for row in result}
        
        assert '2024' in years
        assert years['2024']['revenue'] == '350018'
        assert years['2024']['cost'] == '146306'
        
        assert '2023' in years
        assert years['2023']['revenue'] == '307394'
        assert years['2023']['cost'] == '133332'
        
        revenue_2023 = int(years['2023']['revenue'])
        revenue_2024 = int(years['2024']['revenue'])
        assert revenue_2024 > revenue_2023
        
        cost_2023 = int(years['2023']['cost'])
        cost_2024 = int(years['2024']['cost'])
        assert cost_2024 > cost_2023
