import os
import boto3
from datetime import datetime, timezone
from flask import Flask, request, render_template_string

application = Flask(__name__)

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
s3_client = boto3.client("s3")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Join Our Newsletter</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f4f6f8;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .card {
      background: #ffffff;
      padding: 2.5rem;
      border-radius: 10px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.08);
      max-width: 420px;
      width: 100%;
      text-align: center;
    }
    h1 { font-size: 1.5rem; margin-bottom: 0.5rem; color: #1a202c; }
    p { color: #4a5568; font-size: 0.95rem; margin-bottom: 1.5rem; }
    input[type="email"] {
      width: 100%;
      padding: 10px;
      border: 1px solid #cbd5e0;
      border-radius: 6px;
      box-sizing: border-box;
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }
    button {
      width: 100%;
      padding: 10px;
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover { background: #1d4ed8; }
    .status {
      margin-top: 1.2rem;
      padding: 0.75rem;
      border-radius: 6px;
      font-size: 0.9rem;
    }
    .success { background: #def7ec; color: #03543f; }
    .error { background: #fde8e8; color: #9b1c1c; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Subscribe to the Newsletter</h1>
    <p>Sign up to receive periodic project updates.</p>
    
    <form method="POST" action="/">
      <input type="email" name="email" placeholder="Enter your email address" required />
      <button type="submit">Subscribe</button>
    </form>

    {% if message %}
      <div class="status {{ status }}">{{ message }}</div>
    {% endif %}
  </div>
</body>
</html>
"""

@application.route("/", methods=["GET", "POST"])
def index():
    message = None
    status = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()

        if email and S3_BUCKET:
            try:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                sanitized_email = email.replace("/", "_")
                s3_key = f"emails/{timestamp}_{sanitized_email}.txt"

                file_content = f"Email: {email}\nTimestamp: {timestamp}\n"

                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Body=file_content.encode("utf-8")
                )
                message = "Thank you! Your email has been saved."
                status = "success"
            except Exception as e:
                message = f"Error saving email: {str(e)}"
                status = "error"
        else:
            message = "Please provide an email or check that S3_BUCKET_NAME is configured."
            status = "error"

    return render_template_string(HTML_TEMPLATE, message=message, status=status)

if __name__ == "__main__":
    application.run(debug=True, port=5000)