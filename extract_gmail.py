# Import required libraries
import sqlite3  # For connecting to and querying SQLite databases
import zlib     # For decompressing compressed data (Gmail messages are stored compressed)

# Define the database file name
# This is the SQLite database file that contains Gmail messages
DB = "bigTopDataDB.306804924"

# ========== CONNECT TO DATABASE ==========
# Create a connection to the SQLite database file
conn = sqlite3.connect(DB)

# Create a cursor object to execute SQL commands
# Think of a cursor as a pointer that lets us navigate through database records
cur = conn.cursor()

# ========== QUERY THE DATABASE ==========
# Execute SQL query to get all message data from the database
# We're selecting two columns:
#   - row_id: unique identifier for each message
#   - zipped_message_proto: the compressed message content
cur.execute("""
SELECT
    row_id,
    zipped_message_proto
FROM item_messages
""")

# Fetch all rows returned by the query and store them in a list
# Each row is a tuple containing (row_id, zipped_message_proto)
rows = cur.fetchall()

# ========== PREPARE OUTPUT FILE ==========
# Open a text file to write the recovered Gmail messages
# "w" = write mode (creates new file or overwrites existing)
# encoding="utf-8" = support for international characters
# errors="ignore" = skip any characters that can't be encoded
outfile = open("Recovered_Gmail.txt", "w", encoding="utf-8", errors="ignore")

# Display how many message rows were found in the database
print(f"Found {len(rows)} rows.")

# Counter to track how many messages were successfully extracted
success = 0

# ========== PROCESS EACH MESSAGE ==========
# Loop through each row (message) from the database
for row_id, blob in rows:

    # Check if the blob (compressed message data) is empty
    # If it's None, skip to the next message
    if blob is None:
        continue

    # Try to decompress and extract the message
    # We use try-except because some messages might be corrupted or in an unexpected format
    try:

        # ===== DECOMPRESS THE MESSAGE =====
        # Gmail stores messages compressed with zlib
        # blob[1:] means "skip the first byte" - Gmail adds an extra byte at the start
        # zlib.decompress() uncompresses the data back to its original form
        data = zlib.decompress(blob[1:])

        # Increment the success counter since decompression worked
        success += 1

        # ===== DECODE TO TEXT =====
        # Convert the raw bytes to readable text using UTF-8 encoding
        # errors="ignore" means skip any bytes that can't be converted to text
        text = data.decode("utf-8", errors="ignore")

        # ===== WRITE TO OUTPUT FILE =====
        # Write a visual separator line (80 equal signs)
        outfile.write("=" * 80 + "\n")

        # Write a header showing which row this message came from
        outfile.write(f"ROW {row_id}\n")

        # Write another separator line
        outfile.write("=" * 80 + "\n")

        # Write the actual message content
        outfile.write(text)

        # Add two blank lines to separate this message from the next one
        outfile.write("\n\n")

        # Print a success message to the console
        print(f"[OK] Row {row_id}")

    # If anything goes wrong (decompression fails, decoding fails, etc.)
    except Exception as e:

        # ===== WRITE ERROR INFORMATION =====
        # Write a separator
        outfile.write("=" * 80 + "\n")

        # Write a header indicating this row failed
        outfile.write(f"ROW {row_id} FAILED\n")

        # Write the error message explaining what went wrong
        outfile.write(str(e))

        # Add spacing
        outfile.write("\n\n")

        # Print a failure message to the console
        print(f"[FAIL] Row {row_id}")

# ========== CLEANUP ==========
# Close the output file to save all changes
outfile.close()

# Close the database connection to free up resources
conn.close()

# ========== FINAL SUMMARY ==========
# Print completion message
print("\nFinished.")

# Show how many messages were successfully extracted
print(f"Successfully extracted {success} records.")

# Remind the user where the output was saved
print("Output saved as Recovered_Gmail.txt")
