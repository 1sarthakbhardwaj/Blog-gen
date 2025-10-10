#!/usr/bin/env python3
"""
Setup script to configure the AI Article Backlinking Generator
"""

import os
import sys

def create_env_file():
    """Create .env file with template"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        print(f"⚠️  .env file already exists at {env_path}")
        response = input("Do you want to overwrite it? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Setup cancelled.")
            return False
    
    # Get API key from user
    print("\n🔑 OpenAI API Key Setup")
    print("=" * 50)
    print("You need an OpenAI API key to use this application.")
    print("Get your API key from: https://platform.openai.com/api-keys")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to set it later): ").strip()
    
    if not api_key:
        api_key = "your_openai_api_key_here"
        print("\n⚠️  You can add your API key later by editing the .env file")
    
    # Create .env file
    env_content = f"""# OpenAI API Key (required for CrewAI agents)
OPENAI_API_KEY={api_key}

# Optional: Other LLM providers
# ANTHROPIC_API_KEY=your_anthropic_key
# GOOGLE_API_KEY=your_google_key
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ .env file created successfully at {env_path}")
        return True
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        return False

def verify_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies")
    print("=" * 50)
    
    required_packages = [
        'streamlit',
        'crewai',
        'langchain',
        'langchain_openai',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def main():
    print("=" * 50)
    print("AI Article Backlinking Generator - Setup")
    print("=" * 50)
    print()
    
    # Create .env file
    env_created = create_env_file()
    
    # Verify dependencies
    deps_ok = verify_dependencies()
    
    print("\n" + "=" * 50)
    print("Setup Summary")
    print("=" * 50)
    
    if env_created:
        print("✅ Configuration file created")
    else:
        print("⚠️  Configuration needs attention")
    
    if deps_ok:
        print("✅ Dependencies installed")
    else:
        print("❌ Dependencies need to be installed")
    
    if env_created and deps_ok:
        print("\n🎉 Setup complete! You can now run:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Please complete the setup steps above before running the app.")
    
    print()

if __name__ == "__main__":
    main()

