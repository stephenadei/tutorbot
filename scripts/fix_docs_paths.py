#!/usr/bin/env python3
"""
Fix Documentation Paths
Updates all documentation files to use correct paths for scripts/dev/export_env.sh
"""

import os
import sys
import glob

def ensure_project_root():
    """Ensure we're running from the project root directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if os.getcwd() != project_root:
        print(f"🔄 Changing to project root: {project_root}")
        os.chdir(project_root)
    
    return project_root

PROJECT_ROOT = ensure_project_root()

def fix_documentation_paths():
    """Fix all documentation paths to use correct scripts/dev/ paths"""
    print("🔧 Fixing documentation paths...")
    
    # Find all markdown files in docs directory
    md_files = glob.glob("docs/**/*.md", recursive=True)
    
    changes_made = 0
    
    for file_path in md_files:
        print(f"📝 Checking: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix export_env.sh paths
        content = content.replace(
            "source scripts/export_env.sh",
            "source scripts/dev/export_env.sh"
        )
        content = content.replace(
            "./scripts/export_env.sh",
            "./scripts/dev/export_env.sh"
        )
        content = content.replace(
            "scripts/export_env.sh",
            "scripts/dev/export_env.sh"
        )
        
        # Fix dev.sh paths if needed
        content = content.replace(
            "scripts/dev.sh",
            "scripts/dev/dev.sh"
        )
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            changes_made += 1
        else:
            print(f"⏭️  No changes needed: {file_path}")
    
    print(f"\n🎉 Fixed {changes_made} documentation files!")
    return changes_made

def main():
    """Main function"""
    print("🔧 Documentation Path Fixer")
    print("=" * 40)
    
    changes = fix_documentation_paths()
    
    if changes > 0:
        print(f"\n✅ Successfully updated {changes} files!")
        print("💡 Don't forget to commit these changes:")
        print("   git add docs/")
        print("   git commit -m 'Fix documentation paths to use scripts/dev/'")
    else:
        print("\n✅ All documentation paths are already correct!")

if __name__ == "__main__":
    main() 