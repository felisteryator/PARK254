import base64

shortcode = "174379"

passkey = input("Paste your Daraja Sandbox Passkey: ").strip()
timestamp = input("Enter Timestamp: ").strip()

raw = shortcode + passkey + timestamp

password = base64.b64encode(raw.encode("utf-8")).decode("utf-8")

print("\nGenerated Password:")
print(password)