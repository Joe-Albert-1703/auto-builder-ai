from dotenv import load_dotenv
import os
import google.generativeai as genai
import subprocess
import re

# Load environment variables
load_dotenv()

# Configure the Gemini model
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    system_instruction=(
        'You are a React application generator. Your task is to create React apps from user input. '
        'You will output structured JSON that includes: "commands" (to run), "files" (with filenames and content), and "dependencies" (for npm packages). '
        'Ensure your output is formatted correctly for direct execution without additional processing.'
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

def execute_commands(commands):
    """Executes shell commands sequentially."""
    for command in commands:
        try:
            print(f"💻 Running: {command}")
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {e}")

def save_files(files):
    """Writes files to disk."""
    for file in files:
        filepath = file["filename"]
        content = file["content"]
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"📄 Saved: {filepath}")

def install_dependencies(dependencies):
    """Installs npm dependencies."""
    if dependencies:
        command = "npm install " + " ".join(dependencies)
        execute_commands([command])

def output_cleaner(input_str):
    match = re.search(r"```json(.*?)```", input_str, re.S)
    return match.group(1).strip() if match else ""

def main():
    """Main loop for generating and updating a React app."""
    print("🚀 React App Generator")

    while True:
        prompt = input("📝 Describe your React app (or type 'exit' to quit): ").strip()

        if prompt.lower() in ['exit', 'quit', 'bye', '']:
            print("👋 Stopping...")
            break

        output = call_gemini(prompt)
        output = output_cleaner(output)
        print(output)
        if output:
            try:
                structured_output = eval(output)

                if "commands" in structured_output:
                    execute_commands(structured_output["commands"])

                if "files" in structured_output:
                    save_files(structured_output["files"])

                if "dependencies" in structured_output:
                    install_dependencies(structured_output["dependencies"])

            except Exception as e:
                print(f"❌ Error processing AI output: {e}")

if __name__ == "__main__":
    main()
