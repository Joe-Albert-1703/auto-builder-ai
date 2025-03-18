from dotenv import load_dotenv
import os
import google.generativeai as genai
import subprocess
import json
import re

# Load environment variables
load_dotenv()

# Configure the Gemini model
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=(
        'You are a backend application generator. Your task is to generate backend projects based on a provided JSON object. '
        'The JSON object will contain the programming languages, a project description, and the target directory. '
        'You will output structured JSON with the following keys: "commands" (for shell commands to run), "files" (a list of files with names and content), and "dependencies" (for package installations). '
        'Ensure your output is accurate and ready for direct execution without additional processing.'
    )
)

def call_gemini(prompt):
    """Generates structured output from the Gemini model."""
    try:
        raw = model.generate_content(prompt)
        return raw.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def execute_commands(commands, directory):
    """Executes shell commands sequentially in the specified directory."""
    for command in commands:
        try:
            print(f"💻 Running: {command}")
            subprocess.run(command, shell=True, check=True, cwd=directory)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")

def save_files(files, directory):
    """Writes files to the specified directory."""
    for file in files:
        filepath = os.path.join(directory, file["name"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(file["content"])
        print(f"📄 Saved: {filepath}")

def install_dependencies(dependencies, directory):
    """Installs dependencies in the specified directory."""
    if dependencies:
        command = " ".join(dependencies)
        execute_commands([command], directory)

def get_project_input():
    """Prompts the user for project details and returns a JSON object."""
    languages = input("🗣️ Enter programming languages (comma-separated): ").strip().split(',')
    description = input("📝 Enter project description: ").strip()
    directory = input("📂 Enter target directory (default: ./backend_project): ").strip() or "./backend_project"

    return {
        "languages": [lang.strip() for lang in languages],
        "description": description,
        "directory": directory
    }

def output_cleaner(input_str):
    match = re.search(r"```json(.*?)```", input_str, re.S)
    return match.group(1).strip() if match else ""

def main():
    """Main loop for generating and updating a backend application."""
    print("🚀 Backend App Generator")

    while True:
        user_input = input("📝 Type 'new' to create a project or 'exit' to quit: ").strip().lower()

        if user_input in ['exit', 'quit', 'bye', '']:
            print("👋 Stopping...")
            break

        if user_input == 'new':
            project_data = get_project_input()

            try:
                prompt = f"Languages: {project_data['languages']}, Description: {project_data['description']}"
                output = call_gemini(prompt)
                output = output_cleaner(output)
                print(output)
                if output:
                    structured_output = eval(output)

                    project_directory = project_data.get("directory", "./backend_project")
                    os.makedirs(project_directory, exist_ok=True)

                    if "commands" in structured_output:
                        execute_commands(structured_output["commands"], project_directory)

                    if "files" in structured_output:
                        save_files(structured_output["files"], project_directory)

                    if "dependencies" in structured_output:
                        install_dependencies(structured_output["dependencies"], project_directory)

            except Exception as e:
                print(f"❌ Error processing AI output: {e}")

if __name__ == "__main__":
    main()
