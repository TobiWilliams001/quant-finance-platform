#!/usr/bin/env python3
"""
Fix import statements after migration.
"""

import re
from pathlib import Path


def fix_imports_in_file(file_path: Path):
    """Fix imports in a single file."""
    
    if not file_path.exists():
        return
    
    print(f"🔄 Fixing imports in {file_path}")
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Common import patterns to fix
        fixes = [
            # from utils.module_name import ...
            (r'from utils\.([a-zA-Z_][a-zA-Z0-9_]*) import', r'from quantrisk.analytics.\1 import'),
            
            # import utils.module_name
            (r'import utils\.([a-zA-Z_][a-zA-Z0-9_]*)', r'import quantrisk.analytics.\1'),
            
            # utils.module_name.function()
            (r'utils\.([a-zA-Z_][a-zA-Z0-9_]*)\.', r'quantrisk.analytics.\1.'),
            
            # Specific module mappings
            (r'quantrisk\.analytics\.data_fetcher', 'quantrisk.data.fetcher'),
            (r'quantrisk\.analytics\.database', 'quantrisk.data.database'),  
            (r'quantrisk\.analytics\.report_generator', 'quantrisk.utils.reports'),
        ]
        
        original_content = content
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ Updated {file_path}")
        else:
            print(f"  ℹ️  No changes needed in {file_path}")
            
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")


def main():
    """Fix all import statements."""
    
    print("🔄 Fixing import statements in migrated files...")
    
    # Files to fix
    files_to_fix = []
    
    # Streamlit app files
    streamlit_app = Path("streamlit_app")
    if streamlit_app.exists():
        files_to_fix.append(streamlit_app / "app.py")
        
        # All page files
        pages_dir = streamlit_app / "pages"
        if pages_dir.exists():
            files_to_fix.extend(pages_dir.glob("*.py"))
    
    # Fix each file
    for file_path in files_to_fix:
        fix_imports_in_file(file_path)
    
    print("✅ Import fixing completed!")


if __name__ == "__main__":
    main()