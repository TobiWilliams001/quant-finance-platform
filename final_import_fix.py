#!/usr/bin/env python3
"""
Final fix for import statements after migration.
"""

import re
from pathlib import Path


def fix_specific_imports():
    """Fix the specific import issues."""
    
    fixes = [
        # File-specific fixes based on the errors
        ("from quantrisk.analytics.risk_analytics import", "from quantrisk.analytics.risk import"),
        ("from quantrisk.analytics.options_pricing import", "from quantrisk.analytics.options import"),  
        ("from quantrisk.analytics.portfolio_optimizer import", "from quantrisk.analytics.portfolio import"),
        ("from quantrisk.analytics.monte_carlo import", "from quantrisk.analytics.monte_carlo import"),
        ("from quantrisk.analytics.pairs_trading import", "from quantrisk.analytics.pairs_trading import"),
        ("from quantrisk.data.data_fetcher import", "from quantrisk.data.fetcher import"),
        ("from quantrisk.utils.report_generator import", "from quantrisk.utils.reports import"),
    ]
    
    # Get all Python files in streamlit_app
    python_files = []
    streamlit_dir = Path("streamlit_app")
    if streamlit_dir.exists():
        python_files.extend(streamlit_dir.rglob("*.py"))
    
    for file_path in python_files:
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            for old_import, new_import in fixes:
                content = content.replace(old_import, new_import)
            
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                print(f"✅ Fixed imports in {file_path}")


if __name__ == "__main__":
    fix_specific_imports()
    print("🎉 Import fixes completed!")