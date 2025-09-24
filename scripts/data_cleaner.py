import pandas as pd
import re
import os

class DataCleaner:
    def __init__(self, data_dir='data', output_dir='output'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.final_columns = ['FirstName', 'LastName', 'Street', 'ZipCode', 
                             'City', 'Country', 'Email', 'Phone']
    
    def load_files(self):
        """Load all three data files"""
        print("Loading files...")
        
        # File 1 (CSV)
        df1 = pd.read_csv(os.path.join(self.data_dir, 'file1.csv'))
        
        # File 2 (XLSX)
        df2 = pd.read_excel(os.path.join(self.data_dir, 'file2.xlsx'))
        
        # File 3 (TXT - tab delimited)
        df3 = pd.read_csv(os.path.join(self.data_dir, 'file3.txt'), sep='\t')
        
        return df1, df2, df3
    
    def split_address(self, address):
        """Split FullAddress into Street, ZipCode, City"""
        if pd.isna(address):
            return '', '', ''
        
        parts = str(address).split(', ')
        if len(parts) >= 2:
            street = parts[0]
            zip_city = parts[1].split(' ', 1)
            zipcode = zip_city[0]
            city = zip_city[1] if len(zip_city) > 1 else ''
            return street, zipcode, city
        return '', '', ''
    
    def clean_file1(self, df):
        """Clean CSV file with combined fields"""
        print("Cleaning File 1 (CSV)...")
        
        # Create a copy to avoid warnings
        df = df.copy()
        
        # Split FullName
        df[['FirstName', 'LastName']] = df['FullName'].str.split(' ', n=1, expand=True)
        
        # Split FullAddress
        df[['Street', 'ZipCode', 'City']] = df['FullAddress'].apply(
            lambda x: pd.Series(self.split_address(x))
        )
        
        return df[self.final_columns]
    
    def clean_file2(self, df):
        """Clean XLSX file (already proper structure)"""
        print("Cleaning File 2 (XLSX)...")
        return df[self.final_columns].copy()
    
    def clean_file3(self, df):
        """Clean TXT file (reorder columns and fix formatting)"""
        print("Cleaning File 3 (TXT)...")
        
        # Create a copy to avoid warnings
        df = df.copy()
        
        # Reorder columns
        df = df[['FirstName', 'LastName', 'Street', 'ZipCode', 'City', 'Country', 'Email', 'Phone']]
        
        # Convert ALL CAPS to proper case
        df['FirstName'] = df['FirstName'].astype(str).str.title()
        df['LastName'] = df['LastName'].astype(str).str.title()
        df['City'] = df['City'].astype(str).str.title()
        df['Street'] = df['Street'].astype(str).str.title()
        df['Country'] = df['Country'].astype(str).str.title()
        
        return df
    
    def standardize_phone(self, phone, country):
        """Standardize phone numbers with country codes"""
        if pd.isna(phone) or pd.isna(country):
            return str(phone) if not pd.isna(phone) else ''
        
        # Convert to string and remove all non-digits
        phone = re.sub(r'\D', '', str(phone))
        
        # Country code mapping
        country_codes = {
            'France': '+33',
            'Germany': '+49', 
            'Uk': '+44',
            'UK': '+44',
            'Spain': '+34',
            'Italy': '+39'
        }
        
        country_digits = {'France': '33', 'Germany': '49', 'UK': '44', 'Uk': '44', 'Spain': '34', 'Italy': '39'}
        
        # If phone starts with country code digits, add +
        for c, code in country_digits.items():
            if phone.startswith(code) and str(country) == c:
                return '+' + phone
        
        # If starts with 0, remove it and add country code
        if phone.startswith('0'):
            phone = phone[1:]
        
        return country_codes.get(str(country), '') + phone
    
    def apply_universal_cleaning(self, dataframes):
        """Apply cleaning steps to all dataframes"""
        print("Applying universal cleaning...")
        
        cleaned_dfs = []
        
        for i, df in enumerate(dataframes):
            print(f"  Processing dataframe {i+1}...")
            
            # Create a copy to avoid SettingWithCopyWarning
            df = df.copy()
            
            # Convert all columns to string type first to avoid type conflicts
            for col in df.columns:
                df[col] = df[col].astype(str)
            
            # Trim whitespace
            string_cols = df.select_dtypes(include=['object']).columns
            df[string_cols] = df[string_cols].apply(lambda x: x.str.strip())
            
            # Remove invalid emails (without "@")
            df = df[df['Email'].str.contains('@', na=False)]
            
            # Standardize phone numbers
            df['Phone'] = df.apply(lambda row: self.standardize_phone(row['Phone'], row['Country']), axis=1)
            
            # Proper case for names
            df['FirstName'] = df['FirstName'].str.title()
            df['LastName'] = df['LastName'].str.title()
            
            cleaned_dfs.append(df)
        
        return cleaned_dfs
    
    def deduplicate(self, df):
        """Remove duplicates based on multiple criteria"""
        print("Removing duplicates...")
        
        initial_count = len(df)
        
        # Create a copy to avoid warnings
        df = df.copy()
        
        # Ensure all relevant columns are strings and handle NaN values
        df['FirstName'] = df['FirstName'].astype(str).replace('nan', '')
        df['LastName'] = df['LastName'].astype(str).replace('nan', '')
        df['Street'] = df['Street'].astype(str).replace('nan', '')
        df['ZipCode'] = df['ZipCode'].astype(str).replace('nan', '')
        df['City'] = df['City'].astype(str).replace('nan', '')
        
        # Create composite keys for comparison
        df['name_address_key'] = (df['FirstName'] + '|' + 
                                 df['LastName'] + '|' + 
                                 df['Street'] + '|' + 
                                 df['ZipCode'] + '|' + 
                                 df['City']).str.lower()
        
        # Remove duplicates prioritizing records with more complete data
        # Count non-empty values (excluding 'nan' strings and empty strings)
        df['completeness'] = df[self.final_columns].apply(
            lambda row: sum(1 for x in row if str(x) not in ['', 'nan', 'None']), axis=1
        )
        
        # Remove duplicates by name+address, keeping most complete
        df = df.sort_values('completeness', ascending=False).drop_duplicates(
            subset=['name_address_key'], keep='first'
        )
        
        # Remove duplicates by email, keeping most complete  
        df = df.sort_values('completeness', ascending=False).drop_duplicates(
            subset=['Email'], keep='first'
        )
        
        # Remove duplicates by phone, keeping most complete
        df = df.sort_values('completeness', ascending=False).drop_duplicates(
            subset=['Phone'], keep='first'
        )
        
        # Clean up helper columns
        df = df[self.final_columns]
        
        final_count = len(df)
        print(f"Removed {initial_count - final_count} duplicate records")
        
        return df
    
    def run_cleaning(self):
        """Main cleaning process"""
        print("Starting data cleaning process...")
        
        try:
            # Load files
            df1, df2, df3 = self.load_files()
            
            # Clean each file according to its structure
            df1_clean = self.clean_file1(df1)
            df2_clean = self.clean_file2(df2)
            df3_clean = self.clean_file3(df3)
            
            # Apply universal cleaning
            cleaned_dfs = self.apply_universal_cleaning([df1_clean, df2_clean, df3_clean])
            
            # Merge all dataframes
            print("Merging dataframes...")
            combined_df = pd.concat(cleaned_dfs, ignore_index=True)
            
            # Deduplicate
            final_df = self.deduplicate(combined_df)
            
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Save results
            output_path = os.path.join(self.output_dir, 'cleaned_data.csv')
            final_df.to_csv(output_path, index=False)
            
            # Print summary
            print(f"\n=== CLEANING SUMMARY ===")
            print(f"Total records after cleaning: {len(final_df)}")
            print(f"Unique emails: {final_df['Email'].nunique()}")
            print(f"Unique phones: {final_df['Phone'].nunique()}")
            print(f"Records with invalid emails: {len(final_df[~final_df['Email'].str.contains('@')])}")
            print(f"Output saved to: {output_path}")
            
            return final_df
            
        except Exception as e:
            print(f"Error during processing: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    cleaner = DataCleaner()
    result = cleaner.run_cleaning()
    if result is not None:
        print("\nData cleaning completed successfully!")
    else:
        print("\nData cleaning failed. Please check the error messages above.")