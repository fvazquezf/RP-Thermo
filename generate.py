#!/usr/bin/env python3
# gemini

import sys
import os
import subprocess

def run_command(command, step_name):
    """
    Helper function to run a command, print its details,
    and exit if it fails.
    """
    print("-" * 20)
    print(f"STEP: {step_name}")
    print(f"Executing: {' '.join(command)}")
    print("-" * 20)
    try:
        # Run the command, check=True will raise an error if it fails
        # text=True decodes stdout/stderr as text
        subprocess.run(command, check=True, text=True)
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during {step_name}:")
        print(f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\nError: Command '{e.filename}' not found.")
        print("Please ensure 'python3' is in your system's PATH.")
        sys.exit(1)

def main():
    # --- 1. Check for correct usage ---
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <number>")
        print(f"Example: python3 {sys.argv[0]} 01")
        sys.exit(1)

    # --- 2. Set up variables ---
    number = sys.argv[1]
    
    # Input files
    encode_input = f"examplesthermo/dom{number}.txt"
    decode_input_static = "thermo.lp"
    
    # Output / Intermediate files
    domain_file = f"domain{number}.lp"
    result_file = f"result{number}.txt"

    print(f"Running workflow for number: {number}")

    # --- 3. Run ENCODE ---
    cmd_encode = ["python3", "encode.py", encode_input, domain_file]
    run_command(cmd_encode, "Encoding")

    # Check if encode step was successful
    if not os.path.exists(domain_file):
        print(f"\nError: {domain_file} was not created. Aborting.")
        sys.exit(1)

    # --- 4. Run DECODE (with 'tee' logic) ---
    print("-" * 20)
    print("STEP: Decoding")
    cmd_decode = ["python3", "decode.py", decode_input_static, domain_file]
    print(f"Executing: {' '.join(cmd_decode)} (output will be printed and saved)")
    print("-" * 20)
    
    try:
        # Open the result file for writing
        with open(result_file, 'w') as f:
            # Start the subprocess
            # We pipe stdout so we can read from it
            process = subprocess.Popen(
                cmd_decode, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1 # Line-buffered
            )
            
            # Read stdout line by line in real-time
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    print(line, end='')  # Print to console in real-time
                    f.write(line)        # Write to file
                process.stdout.close()

            # Wait for the process to finish
            return_code = process.wait()
            
            if return_code != 0:
                # Print any errors from stderr if the process failed
                stderr_output = process.stderr.read()
                print(f"\nError during Decoding (return code {return_code}):\n{stderr_output}", file=sys.stderr)
                sys.exit(1)
            
            process.stderr.close()

    except FileNotFoundError as e:
        print(f"\nError: Command '{e.filename}' not found.")
        print("Please ensure 'python3' is in your system's PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred during decoding: {e}")
        sys.exit(1)

    # --- 5. Run DRAW ---
    cmd_draw = ["python3", "drawThermo.py", encode_input, result_file]
    run_command(cmd_draw, "Drawing")

    print("\n-------------------------------------")
    print("Workflow finished successfully.")

if __name__ == "__main__":
    main()