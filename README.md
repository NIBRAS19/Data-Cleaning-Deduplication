# Data Cleaning & Deduplication - Screening Test

## 📑 Deliverables

### 1. Final Cleaned CSV File
**Location:** `output/cleaned_data.csv`

The final dataset with standardized schema:
```
FirstName | LastName | Street | ZipCode | City | Country | Email | Phone
```

### 2. Short Explanation (10-15 lines)

**My Approach:**

I developed a Python solution using pandas to process three heterogeneous data files with different structures. For File 1 (CSV), I split the combined `FullName` and `FullAddress` fields using string parsing techniques. File 2 (XLSX) required minimal restructuring but needed cleaning of duplicated rows and trimming email spaces. File 3 (TXT) had shuffled columns that I reordered and converted from ALL CAPS to proper case.

I applied universal cleaning steps across all files: standardized phone numbers with country codes (+33, +49, +44, +34, +39), removed invalid emails missing "@", and applied proper case formatting to names. For deduplication, I used OR logic where records are considered duplicates if they share the same name+address, email, or phone number. When duplicates were found, I kept the record with the highest completeness score (fewest missing values).

The final pipeline ensures consistent data quality with robust error handling and produces a clean, unified dataset free of duplicates.

### 3. Script Used (Python)

**Main Script:** `scripts/data_cleaner.py`

**Key Features:**
- **Object-oriented design** with `DataCleaner` class
- **File-specific processing** methods for each input format
- **Universal cleaning pipeline** for consistent data quality
- **Smart deduplication logic** with completeness scoring
- **Phone standardization** with country code mapping
- **Comprehensive error handling** and progress reporting

**Usage:**
```bash
python scripts/data_cleaner.py
```

**Dependencies:**
```bash
pip install pandas openpyxl xlrd
```

## 🗂️ Project Structure
```
data-cleaning-project/
├── data/                    # Input files
│   ├── file1.csv           # FullName + FullAddress format
│   ├── file2.xlsx          # Separate columns + duplicates
│   └── file3.txt           # Shuffled columns + ALL CAPS
├── scripts/
│   └── data_cleaner.py     # Main processing script
├── output/
│   └── cleaned_data.csv    # Final cleaned dataset
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Test Requirements Fulfilled

✅ **Split & normalize columns**
- File 1: FullName → FirstName + LastName
- File 1: FullAddress → Street + ZipCode + City  
- File 3: Reordered shuffled columns

✅ **Clean the data**
- Proper case for names (Jean Dupont vs JEAN DUPONT)
- Trimmed extra spaces from emails
- Removed invalid emails (without "@")
- Standardized phone numbers with international format

✅ **Deduplicate**
- Merged all 3 files into unified dataset
- Applied OR logic: same name+address OR email OR phone
- Kept most complete record per duplicate group

✅ **Final output**
- Consistent schema across all records
- Clean, standardized data format
- Duplicate-free dataset

## 📊 Results Summary

The script successfully processes all input files and produces a clean, deduplicated dataset with standardized formatting. Phone numbers are properly formatted with country codes, names use proper capitalization, and all duplicate records are intelligently merged while preserving the most complete information.
