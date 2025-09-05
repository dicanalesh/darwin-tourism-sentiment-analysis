import pandas as pd
import sys
import io

# Set default encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError: # In some environments, reconfigure might not be available
        import functools
        print = functools.partial(print, encoding="utf-8")

try:
    # Load the Excel file
    df = pd.read_excel("KAKADU.xlsx")

    # Print the first 5 rows
    print("--- First 5 rows ---")
    print(df.head().to_markdown(index=False))

    # Print dataframe info
    print("\n--- Dataframe Info ---")
    # Create a buffer to capture info output
    buffer = io.StringIO()
    df.info(verbose=True, buf=buffer)
    print(buffer.getvalue())

except FileNotFoundError:
    print("Error: KAKADU.xlsx not found. Make sure the file is in the same directory.")
except Exception as e:
    print(f"An error occurred: {e}")
    print("\nPlease ensure you have the 'pandas' and 'openpyxl' libraries installed.")
    print("You can install them with: pip install pandas openpyxl")
