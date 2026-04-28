# Bedrock Intelligence Hub

A real-time analytics dashboard for **AWS Bedrock** model invocation data.  
Visualises token usage, IAM identity activity, and model distribution — pulled directly from **CloudWatch Logs Insights**.

---

## What It Does

- **Token analytics** — total input/output tokens per user, per model, over time
- **IAM identity breakdown** — users, assumed roles, root account usage
- **Model distribution** — which Bedrock models are being used and by how much
- **Multi-region support** — switch between any region where Bedrock is active
- **User drill-down** — click any user to see their models, timelines, and ARN details
- **Model drill-down** — see which users invoke a specific model
- **Timeline charts** — hourly token usage trends
- **Auto-refresh** — data refreshes every 5 minutes automatically

---

## Prerequisites

### 1. Python
Python **3.9 or higher** is required.

```bash
python3 --version
```

### 2. AWS Account
You need an IAM user with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity",
        "bedrock:ListFoundationModels",
        "bedrock:GetModelInvocationLoggingConfiguration",
        "logs:StartQuery",
        "logs:GetQueryResults",
        "logs:DescribeLogGroups",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:PutRolePolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

> **Note:** `iam:CreateRole` and `iam:PutRolePolicy` are only needed if you want the app to help set up logging. If you enable logging manually in the console, those are not required.

---

## Installation

### Step 1 — Clone or download the project

```bash
mkdir bedrock-hub
cd bedrock-hub
# Place app.py in this folder
```

### Step 2 — Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Requirements File

Create a file named `requirements.txt` in the same folder as `app.py`:

```
streamlit>=1.32.0
boto3>=1.34.0
pandas>=2.0.0
plotly>=5.20.0
botocore>=1.34.0
```

Or install directly:

```bash
pip install streamlit boto3 pandas plotly
```

---

## Project Structure

```
bedrock-hub/
├── app.py            # Main application (single file)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## Running the App

```bash
streamlit run app.py --server.port 8501
```

Then open your browser at: **http://localhost:8501**

To run on a different port:

```bash
streamlit run app.py --server.port 8080
```

---

## First-Time Setup

### Step 1 — Enable Bedrock Model Invocation Logging

The app reads data from CloudWatch Logs. You must enable Bedrock logging **once per region** before any data appears.

**Do this in the AWS Console:**

1. Go to [Amazon Bedrock → Settings](https://console.aws.amazon.com/bedrock/home#/settings) in your chosen region
2. Toggle **Model invocation logging** ON
3. Select **CloudWatch Logs only**
4. Set log group name to: `/aws/bedrock/invocations`
5. Choose a service role (or let AWS create one)
6. Click **Save settings**

> This is a one-time setup per region. Once enabled, all future Bedrock API calls are logged automatically.

### Step 2 — Log in to the App

1. Open the app at `http://localhost:8501`
2. Enter your **AWS Access Key ID** and **AWS Secret Access Key**
3. Click **Connect to AWS**

The app will:
- Validate your credentials via `sts:GetCallerIdentity`
- Discover available Bedrock regions automatically
- Show a logging status indicator for the selected region

### Step 3 — Select a Region and View Data

- Choose a region from the **Select Region** dropdown in the sidebar
- If logging is **green ✓** — data will load immediately
- If logging is **amber ⚠** — follow the setup steps shown on screen

---

## Logging Status Indicators

| Status | Meaning |
|--------|---------|
| ✓ Green | Logging is active — data is being collected |
| ⚠ Amber | Logging not enabled — follow the on-screen steps |

---

## Dashboard Tabs

| Tab | Contents |
|-----|----------|
| **Overview** | Token share pie, input/output bar chart, identity breakdown, user×model comparison |
| **Users** | All identities ranked by tokens, top-3 models per user, user drill-down |
| **Models** | All models ranked by token volume, model drill-down with user breakdown |
| **Timeline** | Hourly output tokens by model, input vs output trend over time |

---

## Sidebar Filters

| Filter | Description |
|--------|-------------|
| Select Region | Switch between AWS regions |
| Time Range | Last 24h / 1 week / 2 weeks / 3 weeks / 4 weeks |
| Identity Type | Filter by user / role / root |
| Refresh Data | Force refresh CloudWatch data immediately |
| Logout | Clear session and return to login |

---

## Important Notes

- **Data appears only after logging is enabled** — historical calls before enabling are not backfilled
- **Auto-refresh every 5 minutes** — data updates automatically; no need to reload
- **CloudWatch Logs Insights queries** can take 5–15 seconds depending on data volume
- **IAM consistency** — if you just enabled a new IAM role for Bedrock logging, allow 15–30 seconds for propagation before data appears

---

## Troubleshooting

### "No invocation data found"
- Logging may have just been enabled — wait for new Bedrock API calls to be made
- Check the sidebar shows ✓ green for your region
- Try increasing the time range (e.g., switch to "Last 4 weeks")

### "ValidationException: Failed to validate permissions"
- The IAM role for Bedrock logging needs `Resource: "*"` on CloudWatch actions
- Enable logging manually in the Bedrock console — it handles the role setup automatically

### "AccessDeniedException"
- Your IAM user is missing required permissions — see the Prerequisites section above

### Region shows no data but logging is enabled
- Bedrock calls in that region haven't happened yet in the selected time window
- Make a test Bedrock API call then refresh

---

## Security

- Credentials are held **only in Streamlit session state** (in-memory, server-side)
- They are **never written to disk**, logged, or transmitted anywhere except directly to AWS APIs
- The session is cleared on logout

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `boto3` | AWS SDK — CloudWatch Logs, Bedrock, IAM, STS |
| `pandas` | Data processing and aggregation |
| `plotly` | Interactive charts |

---

## License

MIT — free to use and modify.
