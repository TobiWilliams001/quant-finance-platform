#!/usr/bin/env python3
"""
Migration script to move from current structure to professional structure.
Run this from your project root directory.
"""

import os
import shutil
from pathlib import Path


def create_professional_structure():
    """Create the professional directory structure."""
    
    directories = [
        "src/quantrisk/analytics",
        "src/quantrisk/data", 
        "src/quantrisk/utils",
        "src/quantrisk/core",
        "streamlit_app/pages",
        "streamlit_app/components",
        "streamlit_app/styles",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "config",
        "docs",
        "data/exports",
        "logs"
    ]
    
    print("🏗️  Creating professional directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Add __init__.py for Python packages
        if directory.startswith("src/"):
            init_file = Path(directory) / "__init__.py"
            init_file.touch()
    
    print("✅ Directory structure created")


def migrate_business_logic():
    """Move utils/ to src/quantrisk/analytics/"""
    
    print("📦 Migrating business logic...")
    
    # Mapping of current files to new locations
    migrations = {
        "utils/risk_analytics.py": "src/quantrisk/analytics/risk.py",
        "utils/portfolio_optimizer.py": "src/quantrisk/analytics/portfolio.py", 
        "utils/options_pricing.py": "src/quantrisk/analytics/options.py",
        "utils/monte_carlo.py": "src/quantrisk/analytics/monte_carlo.py",
        "utils/pairs_trading.py": "src/quantrisk/analytics/pairs_trading.py",
        "utils/data_fetcher.py": "src/quantrisk/data/fetcher.py",
        "utils/report_generator.py": "src/quantrisk/utils/reports.py",
        "utils/database.py": "src/quantrisk/data/database.py",
    }
    
    for old_path, new_path in migrations.items():
        if Path(old_path).exists():
            shutil.copy2(old_path, new_path)
            print(f"  ✅ {old_path} → {new_path}")
        else:
            print(f"  ⚠️  {old_path} not found")


def migrate_streamlit_app():
    """Move app.py and pages/ to streamlit_app/"""
    
    print("🎨 Migrating Streamlit application...")
    
    # Copy main app
    if Path("app.py").exists():
        shutil.copy2("app.py", "streamlit_app/app.py")
        print("  ✅ app.py → streamlit_app/app.py")
    
    # Copy pages
    if Path("pages").exists():
        for page_file in Path("pages").glob("*.py"):
            dest = Path("streamlit_app/pages") / page_file.name
            shutil.copy2(page_file, dest)
            print(f"  ✅ {page_file} → {dest}")


def migrate_config():
    """Move configuration files to config/ directory."""
    
    print("⚙️  Migrating configuration...")
    
    config_migrations = {
        ".env.example": "config/secrets.example.env",
        ".streamlit/config.toml": "config/streamlit.toml",
    }
    
    for old_path, new_path in config_migrations.items():
        if Path(old_path).exists():
            shutil.copy2(old_path, new_path)
            print(f"  ✅ {old_path} → {new_path}")


def create_init_files():
    """Create proper __init__.py files with exports."""
    
    print("📝 Creating package initialization files...")
    
    # Main package __init__.py
    main_init = Path("src/quantrisk/__init__.py")
    main_init.write_text('''"""
QuantRisk - Professional Quantitative Finance Analytics Platform
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Core imports for easy access
from .analytics import risk, portfolio, options, monte_carlo, pairs_trading
from .data import fetcher, database
from .utils import reports

__all__ = [
    "risk",
    "portfolio", 
    "options",
    "monte_carlo",
    "pairs_trading",
    "fetcher",
    "database",
    "reports"
]
''')
    
    # Analytics package __init__.py
    analytics_init = Path("src/quantrisk/analytics/__init__.py")
    analytics_init.write_text('''"""
Analytics modules for quantitative finance calculations.
"""

from . import risk, portfolio, options, monte_carlo, pairs_trading

__all__ = ["risk", "portfolio", "options", "monte_carlo", "pairs_trading"]
''')
    
    # Data package __init__.py
    data_init = Path("src/quantrisk/data/__init__.py")
    data_init.write_text('''"""
Data handling and fetching modules.
"""

from . import fetcher, database

__all__ = ["fetcher", "database"]
''')
    
    # Utils package __init__.py
    utils_init = Path("src/quantrisk/utils/__init__.py")
    utils_init.write_text('''"""
Utility modules for reports, logging, and configuration.
"""

from . import reports

__all__ = ["reports"]
''')
    
    print("  ✅ Package initialization files created")


def update_imports_in_files():
    """Update import statements in migrated files."""
    
    print("🔄 Updating import statements...")
    
    # This is a simplified version - in practice, you'd need more sophisticated import updating
    files_to_update = [
        "streamlit_app/app.py",
        *Path("streamlit_app/pages").glob("*.py"),
    ]
    
    for file_path in files_to_update:
        if file_path.exists():
            try:
                content = file_path.read_text()
                # Update imports from utils.* to quantrisk.*
                updated_content = content.replace(
                    "from utils import", "from quantrisk.analytics import"
                ).replace(
                    "import utils.", "import quantrisk.analytics."
                ).replace(
                    "utils.", "quantrisk.analytics."
                )
                file_path.write_text(updated_content)
                print(f"  ✅ Updated imports in {file_path}")
            except Exception as e:
                print(f"  ⚠️  Could not update {file_path}: {e}")


def create_backup():
    """Create a backup of current structure."""
    
    print("💾 Creating backup of current structure...")
    
    if Path("backup").exists():
        shutil.rmtree("backup")
    
    # Backup key directories
    dirs_to_backup = ["utils", "pages", "scripts"]
    
    Path("backup").mkdir()
    for directory in dirs_to_backup:
        if Path(directory).exists():
            shutil.copytree(directory, f"backup/{directory}")
    
    # Backup key files
    files_to_backup = ["app.py", "pyproject.toml", ".env.example"]
    for file in files_to_backup:
        if Path(file).exists():
            shutil.copy2(file, f"backup/{file}")
    
    print("  ✅ Backup created in ./backup/")


def main():
    """Main migration orchestration."""
    
    print("🚀 QuantRisk Professional Structure Migration")
    print("=" * 50)
    
    # Safety check
    if not Path("app.py").exists() and not Path("utils").exists():
        print("❌ This doesn't look like a QuantRisk project directory")
        print("   Please run from your project root directory")
        return
    
    try:
        # Step 1: Create backup
        create_backup()
        
        # Step 2: Create new structure
        create_professional_structure()
        
        # Step 3: Migrate business logic
        migrate_business_logic()
        
        # Step 4: Migrate Streamlit app
        migrate_streamlit_app()
        
        # Step 5: Migrate configuration
        migrate_config()
        
        # Step 6: Create proper package files
        create_init_files()
        
        # Step 7: Update imports (basic)
        update_imports_in_files()
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the new structure: cd streamlit_app && streamlit run app.py")
        print("2. Install in development mode: pip install -e .")
        print("3. Run any tests: pytest")
        print("4. If everything works, you can remove the ./backup/ directory")
        print("\nNote: You may need to manually fix some import statements.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Your original files are safe. Check the error and try again.")


if __name__ == "__main__":
    main()