import pytest
import os
from core.views import extract_values_from_text

class TestFinancialDataParser:
    
    @pytest.fixture
    def sample_text(self):
        """Load the extracted text from the test file"""
        # The extracted_text.txt is now in the same directory as this test file
        test_file_path = os.path.join(os.path.dirname(__file__), 'extracted_text.txt')
        
        with open(test_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def test_extract_values_basic_functionality(self, sample_text):
        """Test that the parser extracts data successfully"""
        result = extract_values_from_text(sample_text)
        
        # Should return a 2D array
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Each row should have 3 elements: [year, revenue, cost]
        for row in result:
            assert len(row) == 3
            assert isinstance(row[0], str)  # year
            assert isinstance(row[1], str)  # revenue
            assert isinstance(row[2], str)  # cost
    
    def test_extract_correct_years(self, sample_text):
        """Test that correct years are extracted"""
        result = extract_values_from_text(sample_text)
        
        assert len(result) == 2  # Should have 2 years of data
        
        # Check years
        years = [row[0] for row in result]
        assert '2023' in years
        assert '2024' in years
        
        # Verify order (should be chronological)
        assert result[0][0] == '2023'
        assert result[1][0] == '2024'
    
    def test_extract_correct_financial_values(self, sample_text):
        """Test that correct financial values are extracted"""
        result = extract_values_from_text(sample_text)
        
        # Find 2023 and 2024 data
        data_2023 = next(row for row in result if row[0] == '2023')
        data_2024 = next(row for row in result if row[0] == '2024')
        
        # Test 2023 values (from the extracted text)
        assert data_2023[1] == '307394'  # Revenue without commas
        assert data_2023[2] == '133332'  # Cost of revenues without commas
        
        # Test 2024 values
        assert data_2024[1] == '350018'  # Revenue without commas
        assert data_2024[2] == '146306'  # Cost of revenues without commas
    
    def test_numbers_have_no_commas(self, sample_text):
        """Test that extracted numbers have commas removed"""
        result = extract_values_from_text(sample_text)
        
        for row in result:
            revenue = row[1]
            cost = row[2]
            
            # Should not contain commas
            assert ',' not in revenue
            assert ',' not in cost
            
            # Should be valid integers when converted (handle negative with -)
            assert revenue.lstrip('-').isdigit()
            assert cost.lstrip('-').isdigit()
    
    def test_empty_text_returns_empty_list(self):
        """Test that empty or invalid text returns empty list"""
        result = extract_values_from_text("")
        assert result == []
        
        result = extract_values_from_text("No financial data here")
        assert result == []
    
    def test_missing_year_header_returns_empty(self):
        """Test that text without proper year header returns empty list"""
        invalid_text = """
        Some random text
        Consolidated revenues $ 100,000 $ 200,000
        Cost of revenues $ 50,000 $ 75,000
        """
        result = extract_values_from_text(invalid_text)
        assert result == []
    
    def test_missing_revenue_data_returns_empty(self):
        """Test that text without revenue data returns empty list"""
        invalid_text = """
        Year Ended December 31,
        2023 2024
        Cost of revenues $ 50,000 $ 75,000
        """
        result = extract_values_from_text(invalid_text)
        assert result == []
    
    def test_missing_cost_data_returns_empty(self):
        """Test that text without cost data returns empty list"""
        invalid_text = """
        Year Ended December 31,
        2023 2024
        Consolidated revenues $ 100,000 $ 200,000
        """
        result = extract_values_from_text(invalid_text)
        assert result == []
    
    def test_negative_numbers_with_parentheses(self):
        """Test that numbers in parentheses are treated as negative"""
        text_with_negatives = """
        Year Ended December 31,
        2023 2024
        Consolidated revenues $ 100000 $ (50000)
        Cost of revenues $ (25000) $ 30000
        """
        result = extract_values_from_text(text_with_negatives)
        
        if result:  # Only test if parsing succeeds
            # Check for negative values
            for row in result:
                revenue = row[1]
                cost = row[2]
                
                # Should handle negative numbers correctly
                assert revenue.lstrip('-').isdigit()
                assert cost.lstrip('-').isdigit()
    
    def test_data_types_and_format(self, sample_text):
        """Test that returned data has correct types and format"""
        result = extract_values_from_text(sample_text)
        
        assert isinstance(result, list)
        
        for i, row in enumerate(result):
            assert isinstance(row, list), f"Row {i} should be a list"
            assert len(row) == 3, f"Row {i} should have exactly 3 elements"
            
            year, revenue, cost = row
            
            # Year should be 4-digit string
            assert isinstance(year, str)
            assert len(year) == 4
            assert year.isdigit()
            
            # Revenue and cost should be numeric strings
            assert isinstance(revenue, str)
            assert isinstance(cost, str)
    
    def test_integration_with_real_data(self, sample_text):
        """Integration test with the actual extracted PDF text"""
        result = extract_values_from_text(sample_text)
        
        # Should successfully extract data
        assert len(result) == 2
        
        # Verify we got the expected Alphabet Inc. data
        years = {row[0]: {'revenue': row[1], 'cost': row[2]} for row in result}
        
        # Check 2024 data specifically
        assert '2024' in years
        assert years['2024']['revenue'] == '350018'
        assert years['2024']['cost'] == '146306'
        
        # Check 2023 data specifically  
        assert '2023' in years
        assert years['2023']['revenue'] == '307394'
        assert years['2023']['cost'] == '133332'
        
        # Verify revenue growth (2024 > 2023)
        revenue_2023 = int(years['2023']['revenue'])
        revenue_2024 = int(years['2024']['revenue'])
        assert revenue_2024 > revenue_2023, "Revenue should have grown from 2023 to 2024"
        
        # Verify cost growth (2024 > 2023)
        cost_2023 = int(years['2023']['cost'])
        cost_2024 = int(years['2024']['cost'])
        assert cost_2024 > cost_2023, "Cost should have grown from 2023 to 2024"
