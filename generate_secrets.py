import os

# Generate a random byte string
random_bytes = os.urandom(24)

# Convert the byte string to a hexadecimal string
secret_key = random_bytes.hex()

# Print the secret key
print(secret_key)
