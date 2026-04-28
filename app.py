import streamlit as st
import boto3
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
from botocore.exceptions import ClientError

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bedrock Intelligence Hub",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":      "#0b0b10",
    "surface": "#111119",
    "s2":      "#17171f",
    "border":  "#23232f",
    "accent":  "#5b9cf6",
    "purple":  "#9b7ff4",
    "green":   "#3ecf8e",
    "amber":   "#f4a942",
    "red":     "#f16c6c",
    "text":    "#e3e3ec",
    "muted":   "#8888a8",
}

PAL = [
    "#5b9cf6","#9b7ff4","#3ecf8e","#f4a942","#f16c6c",
    "#e879f9","#22d3ee","#a3e635","#fb923c","#c084fc",
]

def hex_rgba(h, a=0.09):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"

PB = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=C["text"], size=12),
    margin=dict(l=8, r=8, t=32, b=8),
    colorway=PAL,
)
AX = dict(
    gridcolor=C["border"],
    zeroline=False,
    tickfont=dict(size=11, family="'JetBrains Mono', monospace"),
    linecolor=C["border"],
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — clean, minimal, no decorative clutter
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
  font-family: 'Inter', sans-serif;
  background: {C['bg']};
  color: {C['text']};
  -webkit-font-smoothing: antialiased;
}}
.stApp {{ background: {C['bg']}; }}
.block-container {{ padding: 2rem 2.25rem 3rem; max-width: 1400px; }}
#MainMenu, footer, header {{ visibility: hidden; }}

::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {C['border']}; border-radius: 99px; }}

/* ── Inputs ── */
.stTextInput > label,
.stSelectbox > label,
.stMultiSelect > label {{
  color: {C['muted']} !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.7px !important;
  margin-bottom: 5px !important;
}}
.stTextInput > div > div > input {{
  background: {C['surface']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
  color: {C['text']} !important;
  font-size: 13px !important;
  padding: 9px 13px !important;
  transition: border-color 0.15s;
}}
.stTextInput > div > div > input:focus {{
  border-color: {C['accent']} !important;
  outline: none !important;
}}
.stSelectbox > div > div,
.stMultiSelect > div > div {{
  background: {C['surface']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
  color: {C['text']} !important;
  font-size: 13px !important;
}}

/* ── Buttons ── */
.stButton > button {{
  background: {C['s2']} !important;
  border: 1px solid {C['border']} !important;
  border-radius: 8px !important;
  color: {C['text']} !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 8px 18px !important;
  transition: all 0.15s !important;
  width: 100% !important;
  cursor: pointer !important;
}}
.stButton > button:hover {{
  border-color: {C['accent']} !important;
  color: {C['accent']} !important;
  background: {C['surface']} !important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
  background: {C['surface']};
  border: 1px solid {C['border']};
  border-radius: 10px;
  padding: 18px 20px 16px;
}}
[data-testid="metric-container"] > div > div:first-child {{
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.7px !important;
  color: {C['muted']} !important;
  margin-bottom: 6px !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  font-size: 28px !important;
  font-weight: 700 !important;
  letter-spacing: -0.5px !important;
  line-height: 1.1 !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: {C['surface']} !important;
  border-radius: 9px !important;
  padding: 3px !important;
  border: 1px solid {C['border']} !important;
  gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
  font-size: 12px !important;
  font-weight: 500 !important;
  color: {C['muted']} !important;
  border-radius: 7px !important;
  padding: 7px 20px !important;
  transition: all 0.15s !important;
}}
.stTabs [aria-selected="true"] {{
  background: {C['s2']} !important;
  color: {C['text']} !important;
}}
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: {C['surface']} !important;
  border-right: 1px solid {C['border']} !important;
}}
section[data-testid="stSidebar"] .block-container {{
  padding: 1.5rem 1.25rem !important;
}}

hr {{ border: none !important; border-top: 1px solid {C['border']} !important; margin: 1rem 0 !important; }}

/* ─────────── Custom components ─────────── */

/* Section header */
.sec-hdr {{
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: {C['muted']};
  padding-bottom: 9px;
  border-bottom: 1px solid {C['border']};
  margin-bottom: 14px;
}}

/* Page title */
.page-title {{ font-size: 19px; font-weight: 700; color: {C['text']}; letter-spacing: -0.3px; }}
.page-sub   {{ font-size: 12px; color: {C['muted']}; margin-top: 3px; line-height: 1.4; }}

/* Status dot */
.dot {{
  display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: {C['green']}; animation: blink 2.4s ease infinite;
  margin-right: 5px; vertical-align: middle;
}}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.25}} }}

/* Badges */
.badge {{
  display: inline-block; border-radius: 5px; padding: 2px 8px;
  font-size: 10px; font-weight: 500;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap; line-height: 1.6;
}}
.b-blue   {{ background:rgba(91,156,246,0.12);  color:{C['accent']};  border:1px solid rgba(91,156,246,0.25); }}
.b-amber  {{ background:rgba(244,169,66,0.12);   color:{C['amber']};   border:1px solid rgba(244,169,66,0.25); }}
.b-red    {{ background:rgba(241,108,108,0.12);  color:{C['red']};     border:1px solid rgba(241,108,108,0.25); }}
.b-muted  {{ background:rgba(136,136,168,0.10);  color:{C['muted']};   border:1px solid rgba(136,136,168,0.2); }}
.b-purple {{ background:rgba(155,127,244,0.12);  color:{C['purple']};  border:1px solid rgba(155,127,244,0.25); }}

/* Data table */
.tbl {{ width:100%; border-collapse:collapse; font-size:13px; table-layout:auto; }}
.tbl th {{
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.6px; color: {C['muted']};
  padding: 9px 14px; border-bottom: 1px solid {C['border']};
  background: {C['s2']}; white-space: nowrap; text-align: left;
}}
.tbl td {{
  padding: 11px 14px; border-bottom: 1px solid {C['border']};
  color: {C['text']}; vertical-align: top; line-height: 1.5;
}}
.tbl tr:last-child td {{ border-bottom: none; }}
.tbl tr:hover td {{ background: rgba(255,255,255,0.02); }}
.mono {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; }}
.c-acc {{ color:{C['accent']}; font-weight:600; }}
.c-pur {{ color:{C['purple']}; }}
.c-grn {{ color:{C['green']}; }}
.c-amb {{ color:{C['amber']}; }}
.c-mut {{ color:{C['muted']}; }}

/* Role chip showing "role → user" */
.role-map {{
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(244,169,66,0.07);
  border: 1px solid rgba(244,169,66,0.2);
  border-radius: 6px; padding: 3px 9px;
  font-size: 10px; font-family: 'JetBrains Mono', monospace;
  color: {C['amber']}; margin-top: 4px; flex-wrap: wrap;
}}
.role-map .arrow {{ color: {C['muted']}; }}
.role-map .actor {{ color: {C['text']}; }}

/* Mini progress bars for top-3 models */
.mbar-wrap {{ display:flex; flex-direction:column; gap:5px; margin-top:8px; }}
.mbar-row  {{ display:flex; align-items:center; gap:8px; }}
.mbar-name {{
  width: 130px; min-width: 130px; font-size: 10px;
  color: {C['muted']}; font-family: 'JetBrains Mono', monospace;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.mbar-bg   {{ flex:1; background:{C['border']}; border-radius:3px; height:5px; }}
.mbar-fill {{ height:5px; border-radius:3px; }}
.mbar-val  {{
  width: 40px; min-width: 40px; text-align: right;
  font-size: 10px; color: {C['accent']};
  font-family: 'JetBrains Mono', monospace;
}}

/* Drill-down panel */
.drill {{
  background: {C['s2']};
  border: 1px solid {C['border']};
  border-left: 3px solid {C['accent']};
  border-radius: 10px;
  padding: 20px 22px;
  margin-top: 14px;
}}
.stat-row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }}
.stat-box {{
  flex:1; min-width:88px;
  background: {C['surface']};
  border: 1px solid {C['border']};
  border-radius: 8px;
  padding: 11px 14px;
}}
.stat-v {{ font-size:17px; font-weight:700; font-family:'JetBrains Mono',monospace; line-height:1.2; }}
.stat-l {{ font-size:9px; font-weight:600; text-transform:uppercase; letter-spacing:0.6px; color:{C['muted']}; margin-top:3px; }}

/* Active-filter chips */
.filter-chips {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; align-items:center; }}
.chip {{
  display:inline-flex; align-items:center; gap:5px;
  background: rgba(91,156,246,0.08);
  border: 1px solid rgba(91,156,246,0.22);
  border-radius:20px; padding:3px 11px;
  font-size:11px; color:{C['accent']};
}}

/* Identity breakdown card */
.id-card {{
  background: {C['surface']};
  border: 1px solid {C['border']};
  border-radius: 10px;
  padding: 16px 18px;
}}

/* ── LOGIN ── */
.login-page {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  padding: 2rem;
}}
.login-box {{
  background: {C['surface']};
  border: 1px solid {C['border']};
  border-radius: 14px;
  padding: 0;
  width: 100%;
  max-width: 400px;
  overflow: hidden;
}}
.login-header {{
  padding: 28px 32px 22px;
  border-bottom: 1px solid {C['border']};
}}
.login-eyebrow {{
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.5px; color: {C['accent']}; margin-bottom: 8px;
}}
.login-title {{
  font-size: 22px; font-weight: 700; color: {C['text']};
  letter-spacing: -0.3px; margin-bottom: 5px;
}}
.login-desc {{
  font-size: 13px; color: {C['muted']}; line-height: 1.5;
}}
.err-box {{
  background: rgba(241,108,108,0.08);
  border: 1px solid rgba(241,108,108,0.28);
  border-radius: 7px; padding: 10px 14px;
  color: {C['red']}; font-size: 13px; margin-top: 8px;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in [("authenticated", False), ("creds", {})]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────────────────────────────────────
# AWS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def make_client(service, ak, sk, region="us-east-1"):
    return boto3.client(service, aws_access_key_id=ak,
                        aws_secret_access_key=sk, region_name=region)


def validate_creds(ak, sk):
    """Validate using a neutral region; returns (ok, err, account_id)."""
    try:
        r = make_client("sts", ak, sk).get_caller_identity()
        return True, None, r.get("Account","")
    except ClientError as e:
        return False, str(e), ""
    except Exception as e:
        return False, str(e), ""


# ── ALL_BEDROCK_REGIONS – every region that has Bedrock ──────────────────────
ALL_BEDROCK_REGIONS = [
    "us-east-1","us-west-2","eu-west-1","eu-west-2","eu-west-3",
    "eu-central-1","eu-north-1","ap-southeast-1","ap-southeast-2",
    "ap-northeast-1","ap-northeast-2","ap-south-1","ca-central-1",
    "sa-east-1","us-gov-west-1",
]


@st.cache_data(ttl=300, show_spinner=False)
def get_available_regions(ak, sk):
    """
    Return regions where the credentials have access to Bedrock.
    We do a lightweight describe_log_groups call to check CloudWatch access,
    and additionally try a bedrock list_foundation_models to confirm Bedrock exists.
    Falls back to ALL_BEDROCK_REGIONS if both checks fail.
    """
    available = []
    for region in ALL_BEDROCK_REGIONS:
        try:
            make_client("bedrock", ak, sk, region).list_foundation_models()
            available.append(region)
        except ClientError as e:
            code = e.response["Error"]["Code"]
            # If it is an auth/access error we stop; region-not-supported is fine to skip
            if code in ("UnrecognizedClientException","InvalidClientTokenId"):
                break
            # "ValidationException" or endpoint errors = region not supported, skip
        except Exception:
            pass
    return available if available else ALL_BEDROCK_REGIONS


# ── LOGGING AUTOMATION ────────────────────────────────────────────────────────
LOG_GROUP = "/aws/bedrock/invocations"
LOG_ROLE_NAME = "BedrockLoggingRole"

def _build_trust_policy(account_id):
    import json
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "bedrock.amazonaws.com"},
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {"aws:SourceAccount": account_id},
                "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock:*:{account_id}:*"},
            },
        }],
    })


def ensure_logging_role(ak, sk, account_id, region):
    """
    Create/reuse BedrockLoggingRole.
    Policy uses Resource:"*" — required by Bedrock's IAM simulation.
    Always updates the policy so switching regions works.
    """
    import json
    iam = make_client("iam", ak, sk)

    # Policy exactly as AWS docs recommend for Bedrock logging
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
            ],
            "Resource": "*",
        }],
    })

    role_arn = None
    try:
        role     = iam.get_role(RoleName=LOG_ROLE_NAME)
        role_arn = role["Role"]["Arn"]
    except iam.exceptions.NoSuchEntityException:
        try:
            role     = iam.create_role(
                RoleName=LOG_ROLE_NAME,
                AssumeRolePolicyDocument=_build_trust_policy(account_id),
                Description="Bedrock Intelligence Hub — CloudWatch logging",
            )
            role_arn = role["Role"]["Arn"]
        except Exception as e:
            return None, f"Cannot create role: {e}"

    # Always update inline policy (fixes old region-scoped policies)
    try:
        iam.put_role_policy(
            RoleName=LOG_ROLE_NAME,
            PolicyName="BedrockCWLogging",
            PolicyDocument=policy,
        )
    except Exception as e:
        return role_arn, f"Policy update failed: {e}"

    return role_arn, None


def ensure_log_group(ak, sk, region):
    """
    Create /aws/bedrock/invocations log group + put a resource policy
    so Bedrock can write to it. Returns (ok, error_msg).
    """
    import json
    try:
        cw = make_client("logs", ak, sk, region)

        # Create log group if missing
        existing = cw.describe_log_groups(
            logGroupNamePrefix=LOG_GROUP).get("logGroups", [])
        if not any(g["logGroupName"] == LOG_GROUP for g in existing):
            cw.create_log_group(logGroupName=LOG_GROUP)
            try:
                cw.put_retention_policy(
                    logGroupName=LOG_GROUP, retentionInDays=30)
            except Exception:
                pass

        return True, None
    except Exception as e:
        return False, str(e)


def enable_bedrock_logging(ak, sk, account_id, region):
    """
    Automate Bedrock → CloudWatch logging setup for one region.

    Exact same steps the AWS console performs:
      1. Check if already enabled
      2. Create /aws/bedrock/invocations log group
      3. Create/update BedrockLoggingRole (Resource:* policy)
      4. Wait for IAM propagation (15 s)
      5. put_model_invocation_logging_configuration

    The ValidationException was caused by Bedrock doing a live IAM simulation
    where it constructs its own log group ARN. Resource:"*" is the only policy
    that passes this simulation — matching the official AWS docs example.
    """
    try:
        br = make_client("bedrock", ak, sk, region)

        # ── 1. Already enabled? ───────────────────────────────────────────────
        try:
            cfg = br.get_model_invocation_logging_configuration()
            lc  = cfg.get("loggingConfig", {})
            cw  = lc.get("cloudWatchConfig", {})
            if lc.get("textDataDeliveryEnabled") and cw.get("logGroupName") == LOG_GROUP:
                return True, "already_enabled"
        except ClientError:
            pass

        # ── 2. Ensure log group exists in this region ─────────────────────────
        lg_ok, lg_err = ensure_log_group(ak, sk, region)
        if not lg_ok:
            return False, f"Could not create log group: {lg_err}"

        # ── 3. Create/update IAM role ─────────────────────────────────────────
        role_arn, role_err = ensure_logging_role(ak, sk, account_id, region)
        if not role_arn:
            return False, (
                f"Could not create BedrockLoggingRole: {role_err}. "
                "Ensure your IAM user has iam:CreateRole permission, "
                "or enable logging manually via the Bedrock console."
            )

        # ── 4+5. Wait for IAM propagation then enable — retry up to 3 times ──
        # IAM is eventually consistent across regions. Bedrock does a live
        # iam:SimulatePrincipalPolicy call. We retry with increasing waits
        # (15s → 25s → 35s) so the user never needs to click twice.
        logging_cfg = {
            "textDataDeliveryEnabled":      True,
            "imageDataDeliveryEnabled":     True,
            "embeddingDataDeliveryEnabled": True,
            "cloudWatchConfig": {
                "logGroupName": LOG_GROUP,
                "roleArn":      role_arn,
            },
        }
        last_err = None
        for attempt, wait_secs in enumerate([15, 25, 35], start=1):
            time.sleep(wait_secs)
            try:
                br.put_model_invocation_logging_configuration(
                    loggingConfig=logging_cfg)
                return True, "enabled"
            except ClientError as e:
                code = e.response["Error"]["Code"]
                msg  = e.response["Error"]["Message"]
                if code == "ValidationException":
                    last_err = msg
                    continue          # retry after longer wait
                if code == "AccessDeniedException":
                    return False, (
                        "AccessDenied — your IAM user needs: "
                        "bedrock:PutModelInvocationLoggingConfiguration"
                    )
                return False, f"{code}: {msg}"
            except Exception as e:
                return False, str(e)

        # All 3 attempts failed — role is set up correctly but IAM is slow
        return False, (
            f"ValidationException after 3 attempts (75 s total): {last_err}. "
            "The IAM role and log group are correctly configured. "
            "Click Auto-Enable Logging one more time."
        )

    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        if code == "AccessDeniedException":
            return False, (
                "AccessDenied — your IAM user needs: "
                "bedrock:PutModelInvocationLoggingConfiguration"
            )
        return False, f"{code}: {msg}"
    except Exception as e:
        return False, str(e)


def check_logging_status(ak, sk, region):
    """
    Returns a dict:
      enabled (bool), log_group (str), role_arn (str), message (str)
    """
    try:
        br  = make_client("bedrock", ak, sk, region)
        cfg = br.get_model_invocation_logging_configuration()
        lc  = cfg.get("loggingConfig", {})
        cw  = lc.get("cloudWatchConfig", {})
        return {
            "enabled":   lc.get("textDataDeliveryEnabled", False),
            "log_group": cw.get("logGroupName", ""),
            "role_arn":  cw.get("roleArn", ""),
            "message":   "ok",
        }
    except ClientError as e:
        return {"enabled": False, "log_group": "", "role_arn": "",
                "message": e.response["Error"]["Code"]}
    except Exception as e:
        return {"enabled": False, "log_group": "", "role_arn": "", "message": str(e)}


def run_query(client, log_group, query_str, hours):
    end_t   = int(time.time())
    start_t = end_t - hours * 3600
    try:
        qid = client.start_query(
            logGroupName=log_group, startTime=start_t,
            endTime=end_t, queryString=query_str, limit=10000,
        )["queryId"]
        while True:
            r = client.get_query_results(queryId=qid)
            if r["status"] in ("Complete", "Failed", "Cancelled"):
                return r["results"]
            time.sleep(1)
    except Exception as e:
        st.error(f"CloudWatch error: {e}")
        return []


def to_df(results, cols):
    rows = [{i["field"]: i["value"] for i in rec} for rec in results]
    return pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_data_region(ak, sk, region, hours):
    """Fetch data for a single region. Returns (df_um, df_tl) with region column."""
    cl  = make_client("logs", ak, sk, region)
    q_um = """
fields identity.arn, modelId, input.inputTokenCount, output.outputTokenCount
| stats sum(input.inputTokenCount)  as totalInput,
        sum(output.outputTokenCount) as totalOutput
  by identity.arn, modelId
| sort totalOutput desc | limit 1000"""
    q_tl = """
fields @timestamp, identity.arn, modelId, input.inputTokenCount, output.outputTokenCount
| stats sum(input.inputTokenCount)  as totalInput,
        sum(output.outputTokenCount) as totalOutput
  by datefloor(@timestamp, 1h) as hour, identity.arn, modelId
| sort hour asc | limit 2000"""
    df_um = to_df(run_query(cl, LOG_GROUP, q_um, hours),
                  ["identity.arn", "modelId", "totalInput", "totalOutput"])
    df_tl = to_df(run_query(cl, LOG_GROUP, q_tl, hours),
                  ["hour", "identity.arn", "modelId", "totalInput", "totalOutput"])
    for df in [df_um, df_tl]:
        df["region"] = region
        for col in ["totalInput", "totalOutput"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df_um, df_tl


def fetch_data(ak, sk, regions, hours):
    """Fetch and combine data across multiple regions."""
    if isinstance(regions, str):
        regions = [regions]
    all_um, all_tl = [], []
    for region in regions:
        try:
            df_um, df_tl = fetch_data_region(ak, sk, region, hours)
            if not df_um.empty:
                all_um.append(df_um)
            if not df_tl.empty:
                all_tl.append(df_tl)
        except Exception:
            pass
    df_um_out = pd.concat(all_um, ignore_index=True) if all_um else pd.DataFrame(
        columns=["identity.arn","modelId","totalInput","totalOutput","region"])
    df_tl_out = pd.concat(all_tl, ignore_index=True) if all_tl else pd.DataFrame(
        columns=["hour","identity.arn","modelId","totalInput","totalOutput","region"])
    return df_um_out, df_tl_out


# ─────────────────────────────────────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt(n):
    n = int(n)
    if n >= 1_000_000: return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:     return f"{n / 1_000:.1f}K"
    return str(n)


def parse_arn(arn):
    """
    Returns a dict with keys:
      type        – 'user' | 'role' | 'root' | 'other'
      display     – short label for the row (e.g. 'user2', 'user1')
      role_name   – role name if assumed-role, else ''
      assumed_by  – the session/user part if assumed-role, else ''
      full_arn    – original ARN
    """
    s = str(arn)
    d = {"full_arn": s, "role_name": "", "assumed_by": ""}

    if ":assumed-role/" in s:
        # arn:aws:sts::acct:assumed-role/ROLE_NAME/SESSION
        parts = s.split(":assumed-role/", 1)
        rest  = parts[1].split("/")            # [ROLE_NAME, SESSION]
        role  = rest[0] if len(rest) > 0 else ""
        sess  = rest[1] if len(rest) > 1 else ""
        d["type"]       = "role"
        d["role_name"]  = role
        d["assumed_by"] = sess
        d["display"]    = sess or role          # show session (usually the username)
    elif ":root" in s:
        d["type"]    = "root"
        d["display"] = "root"
    elif ":user/" in s:
        d["type"]    = "user"
        d["display"] = s.split(":user/")[-1]
    else:
        d["type"]    = "other"
        d["display"] = s.split("/")[-1] if "/" in s else s[-24:]
    return d


def smodel(mid):
    """Human-readable model label. Split on first '.' to keep full name."""
    s = str(mid).strip()
    if s.startswith("arn:aws:bedrock") and "inference-profile" in s:
        tail = s.split("/")[-1]
        tail = tail.split(".", 1)[-1] if "." in tail else tail
        return tail[:40]
    if "." in s:
        provider, rest = s.split(".", 1)
        return f"{provider} / {rest}"
    return s[:40]


def enrich(df):
    df = df.copy()
    parsed              = df["identity.arn"].apply(parse_arn)
    df["user"]          = parsed.apply(lambda d: d["display"])
    df["identityType"]  = parsed.apply(lambda d: d["type"])
    df["roleName"]      = parsed.apply(lambda d: d["role_name"])
    df["assumedBy"]     = parsed.apply(lambda d: d["assumed_by"])
    df["modelLabel"]    = df["modelId"].apply(smodel)
    df["totalTokens"]   = df["totalInput"] + df["totalOutput"]
    return df


# ─────────────────────────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────────────────────────
BADGE_CLS = {"user": "b-blue", "role": "b-amber", "root": "b-red", "other": "b-muted"}


def identity_html(row):
    """Safe HTML for the identity table cell — no nested quote conflicts."""
    name  = row["user"]
    itype = row["identityType"]
    bcls  = BADGE_CLS.get(itype, "b-muted")
    badge = f"<span class='badge {bcls}'>{itype}</span>"

    role_chip = ""
    if itype == "role" and row.get("roleName"):
        actor = row.get("assumedBy") or name
        rname = row["roleName"]
        role_chip = (
            f"<div class='role-map' style='margin-top:3px;'>"
            f"<span class='actor'>{actor}</span>"
            f"<span class='arrow'> → </span>"
            f"<span>{rname}</span>"
            f"</div>"
        )

    return (
        f"<div style='font-size:13px;font-weight:500;margin-bottom:3px;'>{name}</div>"
        f"{badge}{role_chip}"
    )


def top3_html(df_um_filtered, user):
    """Mini progress bars for the top 3 models used by a user."""
    df_u = df_um_filtered[df_um_filtered["user"] == user]
    if df_u.empty:
        return ""
    top3  = (df_u.groupby("modelLabel", as_index=False)["totalTokens"]
             .sum().sort_values("totalTokens", ascending=False).head(3))
    total = int(top3["totalTokens"].sum()) or 1
    rows  = ""
    for idx, (_, r) in enumerate(top3.iterrows()):
        pct   = int(r["totalTokens"] / total * 100)
        color = PAL[idx % len(PAL)]
        label = r["modelLabel"]
        val = fmt(r["totalTokens"])
        rows += (
            f"<div class='mbar-row'>"
            f"<div class='mbar-name' title='{label}'>{label}</div>"
            f"<div class='mbar-bg'>"
            f"<div class='mbar-fill' style='width:{max(pct,3)}%;background:{color};'></div>"
            f"</div>"
            f"<div class='mbar-val'>{val}</div>"
            f"</div>"
        )
    return f'<div class="mbar-wrap">{rows}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def hbar_chart(labels, values, height=280):
    """Horizontal bar — clamps label length so axes don't overlap."""
    if not labels:
        return go.Figure()
    colors    = [PAL[i % len(PAL)] for i in range(len(labels))]
    # Clip labels for display on axis (full label shown in hover)
    disp = [l if len(l) <= 32 else l[:30] + "…" for l in labels]
    fig = go.Figure(go.Bar(
        x=values, y=disp, orientation="h",
        marker=dict(color=colors, line=dict(width=0), opacity=0.88),
        text=[fmt(v) for v in values],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color=C["muted"]),
        customdata=labels,
        hovertemplate="<b>%{customdata}</b><br>%{x:,} tokens<extra></extra>",
    ))
    fig.update_layout(
        **PB, height=height,
        yaxis=dict(autorange="reversed", **AX),
        xaxis=dict(**AX),
    )
    return fig


def pie_chart(df, height=380):
    if df.empty:
        return go.Figure()
    agg = (df.groupby("modelLabel", as_index=False)["totalTokens"]
           .sum().sort_values("totalTokens", ascending=False))

    # Group slices under 3% into "Other" to prevent label clutter
    total = agg["totalTokens"].sum() or 1
    agg["pct"] = agg["totalTokens"] / total * 100
    main  = agg[agg["pct"] >= 3].copy()
    small = agg[agg["pct"] <  3]
    if not small.empty:
        other_val = int(small["totalTokens"].sum())
        main = pd.concat(
            [main, pd.DataFrame([{"modelLabel": "Other",
                                   "totalTokens": other_val,
                                   "pct": other_val / total * 100}])],
            ignore_index=True,
        )
    agg = main.reset_index(drop=True)

    # Only show label text on slices >= 5%; smaller ones are clear in the legend/hover
    text_vals = [
        f"{row['pct']:.1f}%" if row["pct"] >= 5 else ""
        for _, row in agg.iterrows()
    ]

    fig = go.Figure(go.Pie(
        labels=agg["modelLabel"],
        values=agg["totalTokens"],
        hole=0.62,
        marker=dict(
            colors=PAL[:len(agg)],
            line=dict(color=C["bg"], width=2),
        ),
        text=text_vals,
        textinfo="text",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=12, color="#ffffff"),
        hovertemplate="<b>%{label}</b><br>%{value:,} tokens · %{percent}<extra></extra>",
    ))

    pb_no_margin = {k: v for k, v in PB.items() if k != "margin"}
    fig.update_layout(
        **pb_no_margin,
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.01, y=1.0,
            xanchor="left",
            yanchor="top",
            font=dict(size=10, family="JetBrains Mono"),
            itemsizing="constant",
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            tracegroupgap=2,
        ),
        annotations=[dict(
            text=f"<b>{len(agg)}</b><br><span style='font-size:11px'>models</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color=C["text"]),
        )],
    )
    return fig

def io_bar_chart(df, gcol, top_n=8, height=300):
    """Grouped Input/Output bar. Uses horizontal layout to avoid label overlap."""
    if df.empty:
        return go.Figure()
    agg = (df.groupby(gcol, as_index=False)
           .agg(totalInput=("totalInput", "sum"), totalOutput=("totalOutput", "sum"))
           .sort_values("totalInput", ascending=False)
           .head(top_n))
    disp = agg[gcol].apply(lambda x: x if len(x) <= 28 else x[:26] + "…")
    fig  = go.Figure()
    fig.add_trace(go.Bar(
        name="Input", x=agg["totalInput"], y=disp, orientation="h",
        marker_color=C["accent"], opacity=0.85,
        hovertemplate="<b>%{y}</b><br>Input: %{x:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Output", x=agg["totalOutput"], y=disp, orientation="h",
        marker_color=C["purple"], opacity=0.85,
        hovertemplate="<b>%{y}</b><br>Output: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        **PB, height=height, barmode="group",
        yaxis=dict(autorange="reversed", **AX),
        xaxis=dict(**AX),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
    )
    return fig


def user_model_bar(df_um, top_users=5, top_models=4, height=460):
    """
    Grouped bar: X = top users, groups = top models.
    Legend placed below chart to avoid overlap.
    """
    if df_um.empty:
        return None
    top_u = (df_um.groupby("user")["totalTokens"].sum()
             .sort_values(ascending=False).head(top_users).index.tolist())
    top_m = (df_um.groupby("modelLabel")["totalTokens"].sum()
             .sort_values(ascending=False).head(top_models).index.tolist())
    df_f  = df_um[df_um["user"].isin(top_u) & df_um["modelLabel"].isin(top_m)]
    if df_f.empty:
        return None
    pivot = (df_f.groupby(["user", "modelLabel"], as_index=False)["totalTokens"]
             .sum()
             .pivot(index="user", columns="modelLabel", values="totalTokens")
             .fillna(0)
             .reindex(top_u))
    fig = go.Figure()
    for i, model in enumerate(pivot.columns):
        # Keep legend names short: "provider / model-name" → trim to 22 chars
        short = model if len(model) <= 22 else model[:20] + "…"
        fig.add_trace(go.Bar(
            name=short,
            x=[u if len(u) <= 14 else u[:12] + "…" for u in pivot.index],
            y=pivot[model].tolist(),
            marker_color=PAL[i % len(PAL)],
            opacity=0.88,
            hovertemplate=f"<b>%{{x}}</b><br>{model}<br>%{{y:,}} tokens<extra></extra>",
        ))
    pb_no_margin = {k: v for k, v in PB.items() if k != "margin"}
    fig.update_layout(
        **pb_no_margin,
        height=height,
        barmode="group",
        margin=dict(l=8, r=160, t=20, b=40),   # right margin for vertical legend
        xaxis=dict(**AX),
        yaxis=dict(**AX, title="Tokens"),
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02,
            font=dict(size=10, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            itemwidth=30,
            traceorder="normal",
        ),
        bargap=0.22, bargroupgap=0.08,
    )
    return fig


def timeline_chart(df_tl, height=320):
    if df_tl.empty or "hour" not in df_tl.columns:
        return None
    df   = df_tl.copy()
    df["time"] = pd.to_datetime(df["hour"], errors="coerce")
    grp  = df.groupby(["time", "modelLabel"], as_index=False)["totalOutput"].sum()

    # Limit to top-8 models by total output so the legend stays readable
    top_models = (grp.groupby("modelLabel")["totalOutput"].sum()
                  .sort_values(ascending=False).head(8).index.tolist())
    grp = grp[grp["modelLabel"].isin(top_models)]

    fig  = go.Figure()
    for i, model in enumerate(top_models):
        sub   = grp[grp["modelLabel"] == model].sort_values("time")
        color = PAL[i % len(PAL)]
        # Trim legend label to 22 chars max
        short = model if len(model) <= 22 else model[:20] + "…"
        fig.add_trace(go.Scatter(
            x=sub["time"], y=sub["totalOutput"],
            name=short, mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy", fillcolor=hex_rgba(color, 0.07),
            hovertemplate=f"<b>{model}</b><br>%{{x}}<br>Output: %{{y:,}}<extra></extra>",
        ))
    pb_no_margin = {k: v for k, v in PB.items() if k != "margin"}
    fig.update_layout(
        **pb_no_margin,
        height=height,
        hovermode="x unified",
        margin=dict(l=8, r=160, t=20, b=8),
        xaxis=dict(**AX),
        yaxis=dict(**AX),
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left",   x=1.02,
            font=dict(size=10, family="JetBrains Mono"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    )
    return fig


def io_trend_chart(df_tl, height=260):
    if df_tl.empty or "hour" not in df_tl.columns:
        return None
    df   = df_tl.copy()
    df["time"] = pd.to_datetime(df["hour"], errors="coerce")
    grp  = df.groupby("time", as_index=False).agg(
        totalInput=("totalInput", "sum"),
        totalOutput=("totalOutput", "sum"),
    )
    fig  = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp["time"], y=grp["totalInput"], name="Input",
        mode="lines", line=dict(color=C["green"], width=2),
        fill="tozeroy", fillcolor=hex_rgba(C["green"], 0.08),
        hovertemplate="Input: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=grp["time"], y=grp["totalOutput"], name="Output",
        mode="lines", line=dict(color=C["purple"], width=2),
        fill="tozeroy", fillcolor=hex_rgba(C["purple"], 0.08),
        hovertemplate="Output: %{y:,}<extra></extra>",
    ))
    pb_no_margin = {k: v for k, v in PB.items() if k != "margin"}
    fig.update_layout(
        **pb_no_margin,
        height=height,
        hovermode="x unified",
        margin=dict(l=8, r=20, t=20, b=8),
        xaxis=dict(**AX), yaxis=dict(**AX),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            font=dict(size=11), bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def render_login():
    # The trick: style the middle column's container as the card.
    # Streamlit widgets cannot be placed inside HTML div tags,
    # so we target the column's internal div with CSS instead.
    _bg  = C["bg"];  _sf  = C["surface"]; _bd  = C["border"]
    _ac  = C["accent"]; _pu  = C["purple"]; _tx  = C["text"]
    _mt  = C["muted"]; _rd  = C["red"]

    st.markdown(f"""
    <style>
    .stApp {{ background:{_bg} !important; }}
    #MainMenu, footer, header {{ visibility:hidden; }}
    section[data-testid="stSidebar"] {{ display:none !important; }}

    /* Remove all default padding so we can centre cleanly */
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }}
    /* Full-height flex row */
    [data-testid="stHorizontalBlock"] {{
        min-height: 100vh;
        align-items: center;
        gap: 0 !important;
    }}
    /* Style the middle column as the card */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {{
        background: {_sf} !important;
        border: 1px solid {_bd} !important;
        border-radius: 18px !important;
        padding: 40px 36px 32px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.55) !important;
        margin: 24px 0 !important;
    }}
    /* Inputs inside card */
    [data-testid="stHorizontalBlock"] > div:nth-child(2)
        .stTextInput > div > div > input {{
        background: {_bg} !important;
        border: 1px solid {_bd} !important;
        border-radius: 8px !important;
        color: {_tx} !important;
        font-size: 13px !important;
        padding: 9px 13px !important;
    }}
    [data-testid="stHorizontalBlock"] > div:nth-child(2)
        .stTextInput > div > div > input:focus {{
        border-color: {_ac} !important;
    }}
    /* Gradient connect button */
    [data-testid="stHorizontalBlock"] > div:nth-child(2)
        .stButton > button {{
        background: linear-gradient(135deg, {_ac}, {_pu}) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 11px 20px !important;
        box-shadow: 0 4px 18px rgba(91,156,246,0.3) !important;
        width: 100% !important;
    }}
    [data-testid="stHorizontalBlock"] > div:nth-child(2)
        .stButton > button:hover {{
        opacity: 0.88 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Three columns — middle is the card
    left, mid, right = st.columns([1, 1.1, 1])

    with mid:
        # ── Logo + heading (pure HTML, sits at top of card) ──────────────────
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:28px;">
          <div style="width:50px;height:50px;
               background:linear-gradient(135deg,{_ac},{_pu});
               border-radius:13px;margin:0 auto 18px;
               display:flex;align-items:center;justify-content:center;
               font-size:22px;
               box-shadow:0 6px 24px rgba(91,156,246,0.35);">⬡</div>
          <div style="font-size:22px;font-weight:700;color:{_tx};
               letter-spacing:-0.4px;margin-bottom:5px;">Intelligence Hub</div>
          <div style="font-size:12px;color:{_mt};">
               AWS Bedrock · CloudWatch Analytics</div>
        </div>
        <div style="height:1px;background:{_bd};margin-bottom:22px;"></div>
        """, unsafe_allow_html=True)

        # ── Streamlit widgets (must be direct children of column) ────────────
        ak = st.text_input("AWS Access Key ID",
                           placeholder="AKIAIOSFODNN7EXAMPLE", key="l_ak")
        sk = st.text_input("AWS Secret Access Key",
                           placeholder="wJalrXUtnFEMI/K7MDENG…",
                           type="password", key="l_sk")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        clicked = st.button("Connect to AWS", use_container_width=True, key="connect")

        if clicked:
            if not ak or not sk:
                st.markdown(
                    f"<div style='background:rgba(241,108,108,0.09);"
                    f"border:1px solid rgba(241,108,108,0.28);border-radius:8px;"
                    f"padding:10px 14px;color:{_rd};font-size:12px;margin-top:10px;'>"
                    f"Access Key and Secret Key are required.</div>",
                    unsafe_allow_html=True)
            else:
                with st.spinner("Validating credentials…"):
                    ok, err, acct = validate_creds(ak, sk)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.creds = {"ak": ak, "sk": sk, "account_id": acct}
                    st.session_state.pop("available_regions", None)
                    st.session_state.pop("logging_results", None)
                    st.rerun()
                else:
                    st.markdown(
                        f"<div style='background:rgba(241,108,108,0.09);"
                        f"border:1px solid rgba(241,108,108,0.28);border-radius:8px;"
                        f"padding:10px 14px;color:{_rd};font-size:12px;margin-top:10px;'>"
                        f"{err}</div>",
                        unsafe_allow_html=True)

        st.markdown(
            f"<div style='font-size:10px;color:{_mt};text-align:center;"
            f"margin-top:20px;line-height:1.6;opacity:.65;'>"
            f"Credentials are used only to query your AWS account<br>"
            f"and are never stored or transmitted.</div>",
            unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard():
    creds      = st.session_state.creds
    account_id = creds.get("account_id", "")

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;
             letter-spacing:1.5px;color:{C['accent']};margin-bottom:2px;">Bedrock Hub</div>
        <div style="font-size:16px;font-weight:700;color:{C['text']};
             margin-bottom:18px;letter-spacing:-0.2px;">Configuration</div>
        """, unsafe_allow_html=True)

        # ── Region discovery + selection ─────────────────────────────────────
        st.markdown(f'<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                    f'letter-spacing:.7px;color:{C["muted"]};margin-bottom:6px;">AWS Regions</div>',
                    unsafe_allow_html=True)

        if "available_regions" not in st.session_state:
            with st.spinner("Discovering Bedrock regions…"):
                st.session_state.available_regions = get_available_regions(
                    creds["ak"], creds["sk"])

        avail = st.session_state.available_regions
        selected_region = st.selectbox(
            "Select Region",
            options=avail,
            index=0,
            key="sel_region",
            help="Choose the region to query",
        )
        # Wrap in list so downstream code is unchanged
        selected_regions = [selected_region]

        st.markdown("---")

        # ── Logging status (check only — no auto-enable button) ───────────────
        st.markdown(
            f"<div style='font-size:10px;font-weight:600;text-transform:uppercase;"
            f"letter-spacing:.7px;color:{C['muted']};margin-bottom:8px;'>"
            f"Logging Status</div>",
            unsafe_allow_html=True,
        )

        status = check_logging_status(creds["ak"], creds["sk"], selected_region)
        console_url = (
            f"https://{selected_region}.console.aws.amazon.com/bedrock/home"
            f"?region={selected_region}#/settings"
        )
        _cg = C["green"]; _cm = C["muted"]; _ca = C["accent"]

        if status["enabled"]:
            lg = status.get("log_group", LOG_GROUP)
            st.markdown(
                f"<div style='background:rgba(62,207,142,0.08);"
                f"border:1px solid rgba(62,207,142,0.25);"
                f"border-radius:8px;padding:10px 12px;'>"
                f"<div style='font-size:11px;font-weight:600;color:{_cg};"
                f"margin-bottom:3px;'>✓ Logging Active</div>"
                f"<div style='font-size:10px;color:{_cm};font-family:monospace;'>{lg}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background:rgba(244,169,66,0.08);"
                f"border:1px solid rgba(244,169,66,0.25);"
                f"border-radius:8px;padding:10px 12px;margin-bottom:8px;'>"
                f"<div style='font-size:11px;font-weight:600;color:{C['amber']};'>"
                f"⚠ Logging Not Enabled</div>"
                f"<div style='font-size:10px;color:{_cm};margin-top:3px;'>"
                f"Enable it to see token data</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<a href='{console_url}' target='_blank'>"
                f"<div style='background:{C['s2']};border:1px solid {C['border']};"
                f"border-radius:8px;padding:9px 12px;text-align:center;"
                f"font-size:11px;font-weight:600;color:{_ca};cursor:pointer;'>"
                f"Open Bedrock Console →</div></a>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── Filters ───────────────────────────────────────────────────────────
        st.markdown(f'<div style="font-size:10px;font-weight:600;text-transform:uppercase;'
                    f'letter-spacing:.7px;color:{C["muted"]};margin-bottom:6px;">Filters</div>',
                    unsafe_allow_html=True)

        time_opt = st.selectbox(
            "Time Range",
            ["Last 24 hours","Last 1 week","Last 2 weeks",
             "Last 3 weeks","Last 4 weeks"],
            index=1, key="tr",
        )
        h_map = {
            "Last 24 hours": 24,  "Last 1 week":  168,
            "Last 2 weeks":  336, "Last 3 weeks": 504, "Last 4 weeks": 672,
        }
        hours = h_map[time_opt]

        id_filter = st.multiselect(
            "Identity Type", ["user","role","root"],
            placeholder="All types", key="idf",
        )
        st.markdown("---")

        if st.button("Refresh Data", use_container_width=True, key="ref"):
            fetch_data_region.clear()
            st.rerun()
        if st.button("Logout", use_container_width=True, key="lo"):
            for k in ["authenticated","creds","available_regions","logging_results"]:
                st.session_state.pop(k, None)
            fetch_data_region.clear()
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:11px;color:{C['muted']};line-height:2;">
          <span class="dot"></span>Connected<br>
          Region: {selected_region}<br>
          Range: {time_opt}<br>
          Auto-refresh: 5 min
        </div>
        """, unsafe_allow_html=True)

    # ── Page header ──────────────────────────────────────────────────────────
    hc1, hc2 = st.columns([4, 1])
    with hc1:
        region_display = ", ".join(selected_regions) if len(selected_regions) <= 3                          else f"{len(selected_regions)} regions"
        st.markdown(f"""
        <div class="page-title">Bedrock Intelligence Hub</div>
        <div class="page-sub">
          <span class="dot"></span>Live · {region_display.upper()} · {time_opt}
        </div>
        """, unsafe_allow_html=True)
    with hc2:
        st.markdown(
            f'<div style="text-align:right;padding-top:8px;font-size:11px;'
            f'color:{C["muted"]};">'
            f'{datetime.now().strftime("%H:%M  %d %b %Y")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Fetch + enrich ────────────────────────────────────────────────────────
    # Show a per-region status while loading
    load_placeholder = st.empty()
    with load_placeholder:
        with st.spinner(f"Querying CloudWatch across {len(selected_regions)} region(s)…"):
            df_um_raw, df_tl_raw = fetch_data(
                creds["ak"], creds["sk"], selected_regions, hours)
    load_placeholder.empty()

    if df_um_raw.empty:
        # Check whether logging is actually enabled to show the right message
        _status = check_logging_status(creds["ak"], creds["sk"], selected_region)
        _ca = C["accent"]; _cm = C["muted"]; _cg = C["green"]; _cb = C["border"]
        _s2 = C["s2"]

        if _status["enabled"]:
            # Logging is ON but no data yet — calls haven't happened in this window
            st.markdown(
                f"<div style='background:{_s2};border:1px solid {_cb};"
                f"border-left:3px solid {_cg};border-radius:10px;"
                f"padding:20px 24px;'>"
                f"<div style='font-size:14px;font-weight:600;color:{_cg};"
                f"margin-bottom:8px;'>✓ Logging is active in {selected_region}</div>"
                f"<div style='font-size:13px;color:{_cm};line-height:1.7;'>"
                f"No Bedrock invocations found in the selected time range.<br>"
                f"This means either:<br>"
                f"&nbsp;&nbsp;• No Bedrock model calls were made in this period, or<br>"
                f"&nbsp;&nbsp;• Logging was enabled recently — only <b>new</b> calls "
                f"after enabling are logged (no backfill).<br><br>"
                f"Make some Bedrock API calls then refresh the dashboard."
                f"</div></div>",
                unsafe_allow_html=True,
            )
        else:
            # Logging is OFF — show clear numbered steps to enable it
            _console_url = (
                f"https://{selected_region}.console.aws.amazon.com/bedrock/home"
                f"?region={selected_region}#/settings"
            )
            steps_html = (
                f"<div style='background:{_s2};border:1px solid {_cb};"
                f"border-left:3px solid {_ca};border-radius:12px;padding:22px 26px;'>"

                f"<div style='font-size:15px;font-weight:700;color:{_ca};"
                f"margin-bottom:4px;'>⚠ Logging not enabled in {selected_region}</div>"
                f"<div style='font-size:12px;color:{_cm};margin-bottom:18px;'>"
                f"Bedrock model invocation logging must be turned on before token "
                f"usage data can be collected.</div>"

                # Step 1
                f"<div style='display:flex;gap:12px;margin-bottom:14px;align-items:flex-start;'>"
                f"<div style='min-width:24px;height:24px;background:{_ca};border-radius:50%;"
                f"display:flex;align-items:center;justify-content:center;"
                f"font-size:11px;font-weight:700;color:#fff;flex-shrink:0;'>1</div>"
                f"<div style='font-size:12px;color:{_cm};line-height:1.6;'>"
                f"<a href='{_console_url}' target='_blank' "
                f"style='color:{_ca};font-weight:600;'>Open Bedrock Settings</a>"
                f" in the AWS Console for <b>{selected_region}</b>"
                f"</div></div>"

                # Step 2
                f"<div style='display:flex;gap:12px;margin-bottom:14px;align-items:flex-start;'>"
                f"<div style='min-width:24px;height:24px;background:{_ca};border-radius:50%;"
                f"display:flex;align-items:center;justify-content:center;"
                f"font-size:11px;font-weight:700;color:#fff;flex-shrink:0;'>2</div>"
                f"<div style='font-size:12px;color:{_cm};line-height:1.6;'>"
                f"Toggle <b>Model invocation logging</b> ON, "
                f"select <b>CloudWatch Logs only</b>"
                f"</div></div>"

                # Step 3
                f"<div style='display:flex;gap:12px;margin-bottom:14px;align-items:flex-start;'>"
                f"<div style='min-width:24px;height:24px;background:{_ca};border-radius:50%;"
                f"display:flex;align-items:center;justify-content:center;"
                f"font-size:11px;font-weight:700;color:#fff;flex-shrink:0;'>3</div>"
                f"<div style='font-size:12px;color:{_cm};line-height:1.6;'>"
                f"Set log group name to "
                f"<code style='background:{_cb};border-radius:4px;padding:2px 6px;"
                f"font-size:11px;color:{_ca};'>/aws/bedrock/invocations</code>"
                f"</div></div>"

                # Step 4
                f"<div style='display:flex;gap:12px;margin-bottom:18px;align-items:flex-start;'>"
                f"<div style='min-width:24px;height:24px;background:{_ca};border-radius:50%;"
                f"display:flex;align-items:center;justify-content:center;"
                f"font-size:11px;font-weight:700;color:#fff;flex-shrink:0;'>4</div>"
                f"<div style='font-size:12px;color:{_cm};line-height:1.6;'>"
                f"Select a service role (or let AWS create one), click <b>Save settings</b>"
                f"</div></div>"

                # CTA button
                f"<a href='{_console_url}' target='_blank' style='text-decoration:none;'>"
                f"<div style='background:{_ca};border-radius:8px;padding:10px 18px;"
                f"text-align:center;font-size:12px;font-weight:600;color:#fff;"
                f"cursor:pointer;'>Go to Bedrock Settings →</div></a>"

                f"</div>"
            )
            st.markdown(steps_html, unsafe_allow_html=True)
        return

    df_um = enrich(df_um_raw)
    df_tl = enrich(df_tl_raw) if not df_tl_raw.empty else pd.DataFrame()

    # Sidebar identity-type filter
    if id_filter:
        df_um = df_um[df_um["identityType"].isin(id_filter)]
        if not df_tl.empty:
            df_tl = df_tl[df_tl["identityType"].isin(id_filter)]

    # Sorted dropdown options
    all_users  = sorted(df_um["user"].unique().tolist())
    all_models = sorted(df_um["modelLabel"].unique().tolist())


    # ── Search / filter row ──────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        usel = st.selectbox(
            "Filter by User", ["All users"] + all_users,
            key="usel", help="Type to search",
        )
    with fc2:
        msel = st.selectbox(
            "Filter by Model", ["All models"] + all_models,
            key="msel", help="Type to search",
        )
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear", use_container_width=True, key="clr"):
            st.rerun()

    au = None if usel == "All users"   else usel
    am = None if msel == "All models"  else msel
    ar = None

    df_f  = df_um.copy()
    df_tf = df_tl.copy() if not df_tl.empty else pd.DataFrame()

    if au:
        df_f  = df_f[df_f["user"] == au]
        if not df_tf.empty: df_tf = df_tf[df_tf["user"] == au]
    if am:
        df_f  = df_f[df_f["modelLabel"] == am]
        if not df_tf.empty: df_tf = df_tf[df_tf["modelLabel"] == am]


    # Active filter banner
    parts = []
    if au: parts.append(f'<span class="chip">👤 {au}</span>')
    if am: parts.append(f'<span class="chip">⬡ {am}</span>')

    if parts:
        st.markdown(f'<div class="filter-chips">{"".join(parts)}</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Unique Users",  fmt(df_f["user"].nunique()))
    k2.metric("Models Used",   fmt(df_f["modelId"].nunique()))
    k3.metric("Total Tokens",  fmt(df_f["totalTokens"].sum()))
    k4.metric("Input Tokens",  fmt(df_f["totalInput"].sum()))
    k5.metric("Output Tokens", fmt(df_f["totalOutput"].sum()))

    st.markdown(f"""<style>
    div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"]
      {{color:{C['accent']}!important}}
    div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"]
      {{color:{C['purple']}!important}}
    div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"]
      {{color:{C['green']}!important}}
    div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"]
      {{color:{C['amber']}!important}}
    div[data-testid="metric-container"]:nth-child(5) [data-testid="stMetricValue"]
      {{color:{C['red']}!important}}
    </style>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tabs = st.tabs(["Overview", "Users", "Models", "Timeline"])

    # ═════════════════════════════════════════════
    # OVERVIEW
    # ═════════════════════════════════════════════
    with tabs[0]:
        r1a, r1b = st.columns([1, 1], gap="large")
        with r1a:
            st.markdown('<div class="sec-hdr">Token Share by Model</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(pie_chart(df_f), use_container_width=True,
                            config={"displayModeBar": False})
        with r1b:
            st.markdown('<div class="sec-hdr">Input vs Output — Top Models</div>',
                        unsafe_allow_html=True)
            fio = io_bar_chart(df_f, "modelLabel")
            if fio:
                st.plotly_chart(fio, use_container_width=True,
                                config={"displayModeBar": False})



        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Identity Breakdown</div>',
                    unsafe_allow_html=True)
        ta    = df_f.groupby("identityType")["totalTokens"].sum().reset_index()
        grand = ta["totalTokens"].sum() or 1
        tc    = {"user": C["accent"], "role": C["amber"],
                 "root": C["red"],    "other": C["muted"]}
        if not ta.empty:
            id_cols = st.columns(min(len(ta), 4), gap="medium")
            for i, (_, row) in enumerate(ta.iterrows()):
                cc  = tc.get(row["identityType"], C["muted"])
                pct = int(row["totalTokens"] / grand * 100)
                with id_cols[i % 4]:
                    st.markdown(f"""
                    <div class="id-card" style="border-left:3px solid {cc};">
                      <div style="font-size:10px;font-weight:600;text-transform:uppercase;
                           letter-spacing:.7px;color:{C['muted']};margin-bottom:7px;">
                        {row['identityType']}</div>
                      <div style="font-size:24px;font-weight:700;color:{cc};
                           font-family:'JetBrains Mono',monospace;line-height:1.1;">
                        {fmt(row['totalTokens'])}</div>
                      <div style="font-size:11px;color:{C['muted']};margin-top:4px;">
                        {pct}% of total</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Top Users × Top Models — Token Comparison</div>',
                    unsafe_allow_html=True)
        st.caption("Each cluster = one user. Each bar = their usage of a top model.")
        um = user_model_bar(df_f)
        if um:
            st.plotly_chart(um, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.info("Not enough data for this chart.")

    # ═════════════════════════════════════════════
    # USERS
    # ═════════════════════════════════════════════
    with tabs[1]:
        user_meta = (
            df_f.drop_duplicates(subset="user")
            [["user","identityType","roleName","assumedBy","identity.arn"]]
            .set_index("user")
        )
        usum = (
            df_f.groupby("user", as_index=False)
            .agg(totalTokens=("totalTokens","sum"), totalInput=("totalInput","sum"),
                 totalOutput=("totalOutput","sum"), models=("modelId","nunique"))
            .sort_values("totalTokens", ascending=False)
            .reset_index(drop=True)
        )
        for col in ["identityType","roleName","assumedBy","identity.arn"]:
            usum[col] = usum["user"].map(user_meta[col])

        ul, ur = st.columns([3, 2], gap="large")
        with ul:
            st.markdown('<div class="sec-hdr">Active Identities — Top 3 Models Inline</div>',
                        unsafe_allow_html=True)
            rows_html = ""
            for i, row in usum.iterrows():
                id_cell = identity_html(row)
                t3      = top3_html(df_f, row["user"])
                rows_html += f"""
                <tr>
                  <td class="mono c-mut" style="width:36px;">#{i+1}</td>
                  <td style="min-width:180px;">{id_cell}{t3}</td>
                  <td class="mono c-acc" style="text-align:right;white-space:nowrap;">
                    {fmt(row['totalTokens'])}</td>
                  <td class="mono c-grn" style="text-align:right;white-space:nowrap;">
                    {fmt(row['totalInput'])}</td>
                  <td class="mono c-pur" style="text-align:right;white-space:nowrap;">
                    {fmt(row['totalOutput'])}</td>
                  <td class="mono c-amb" style="text-align:right;white-space:nowrap;">
                    {int(row['models'])}</td>
                </tr>"""
            st.markdown(f"""
            <div style="background:{C['surface']};border:1px solid {C['border']};
                 border-radius:10px;overflow:hidden;max-height:560px;overflow-y:auto;">
            <table class="tbl">
              <thead><tr>
                <th>#</th><th>Identity</th>
                <th style="text-align:right">Total</th>
                <th style="text-align:right">Input</th>
                <th style="text-align:right">Output</th>
                <th style="text-align:right">Models</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table></div>""", unsafe_allow_html=True)

        with ur:
            st.markdown('<div class="sec-hdr">Top Users by Volume</div>',
                        unsafe_allow_html=True)
            top8 = usum.head(8)
            if not top8.empty:
                st.plotly_chart(
                    hbar_chart(top8["user"].tolist(),
                               top8["totalTokens"].tolist(), height=320),
                    use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">User Detail View</div>', unsafe_allow_html=True)
        sel_u = st.selectbox("Select a user to explore",
                             ["— select —"] + all_users, key="udd")
        if sel_u and sel_u != "— select —":
            ud = df_f[df_f["user"] == sel_u]
            if not ud.empty:
                u_row  = ud.iloc[0]
                u_arn  = u_row["identity.arn"]
                u_type = u_row["identityType"]
                u_role = u_row.get("roleName", "")
                u_sess = u_row.get("assumedBy", "")
                u_tot  = int(ud["totalTokens"].sum())
                u_in   = int(ud["totalInput"].sum())
                u_out  = int(ud["totalOutput"].sum())
                u_mods = ud["modelId"].nunique()
                badge_cls = BADGE_CLS.get(u_type, "b-muted")
                role_chip = ""
                if u_type == "role" and u_role:
                    _actor = u_sess or sel_u
                    role_chip = (
                        f"<div class='role-map' style='margin-top:6px;'>"
                        f"<span class='actor'>{_actor}</span>"
                        f"<span class='arrow'> → </span>"
                        f"<span>{u_role}</span>"
                        f"</div>"
                    )
                # Build drill HTML with pre-extracted variables (no dict-key quotes inside f-string)
                _cm = C["muted"]; _ca = C["accent"]; _cg = C["green"]
                _cp = C["purple"]; _cb = C["amber"]
                drill_html = (
                    "<div class='drill'>"
                    "<div style='display:flex;justify-content:space-between;"
                    "align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:8px;'>"
                    "<div style='flex:1;min-width:0;'>"
                    f"<div style='font-size:15px;font-weight:700;margin-bottom:4px;'>{sel_u}</div>"
                    f"<div style='font-size:11px;color:{_cm};"
                    "font-family:JetBrains Mono,monospace;word-break:break-all;"
                    f"margin-bottom:6px;'>{u_arn}</div>"
                    f"<span class='badge {badge_cls}'>{u_type}</span>"
                    f"{role_chip}"
                    "</div></div>"
                    "<div class='stat-row' style='margin-top:12px;'>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_ca};'>{fmt(u_tot)}</div>"
                    "<div class='stat-l'>Total</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cg};'>{fmt(u_in)}</div>"
                    "<div class='stat-l'>Input</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cp};'>{fmt(u_out)}</div>"
                    "<div class='stat-l'>Output</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cb};'>{u_mods}</div>"
                    "<div class='stat-l'>Models</div></div>"
                    "</div></div>"
                )
                st.markdown(drill_html, unsafe_allow_html=True)
                da1, da2 = st.columns(2, gap="large")
                with da1:
                    st.markdown('<div class="sec-hdr" style="margin-top:16px;">Models Used</div>',
                                unsafe_allow_html=True)
                    mdf = (ud.groupby("modelLabel", as_index=False)["totalTokens"]
                           .sum().sort_values("totalTokens", ascending=False))
                    st.plotly_chart(
                        hbar_chart(mdf["modelLabel"].tolist(),
                                   mdf["totalTokens"].tolist(), height=230),
                        use_container_width=True, config={"displayModeBar": False})
                with da2:
                    st.markdown('<div class="sec-hdr" style="margin-top:16px;">Activity Timeline</div>',
                                unsafe_allow_html=True)
                    if not df_tf.empty:
                        u_tl = df_tf[df_tf["user"] == sel_u]
                        tl   = timeline_chart(u_tl, height=230)
                        if tl:
                            st.plotly_chart(tl, use_container_width=True,
                                            config={"displayModeBar": False})
                        else:
                            st.info("No timeline data for this user.")

    # ═════════════════════════════════════════════
    # MODELS
    # ═════════════════════════════════════════════
    with tabs[2]:
        msum = (
            df_f.groupby("modelLabel", as_index=False)
            .agg(totalTokens=("totalTokens","sum"), totalInput=("totalInput","sum"),
                 totalOutput=("totalOutput","sum"), users=("user","nunique"))
            .sort_values("totalTokens", ascending=False)
            .reset_index(drop=True)
        )
        grand_m = msum["totalTokens"].sum() or 1
        ml, mr = st.columns([3, 2], gap="large")
        with ml:
            st.markdown('<div class="sec-hdr">All Models</div>', unsafe_allow_html=True)
            rows_html = ""
            for i, row in msum.iterrows():
                pct   = int(row["totalTokens"] / grand_m * 100)
                col_c = PAL[i % len(PAL)]
                rows_html += f"""
                <tr>
                  <td class="mono c-mut" style="width:36px;">#{i+1}</td>
                  <td style="min-width:160px;">
                    <div style="font-size:12px;font-weight:500;margin-bottom:5px;
                         word-break:break-word;">{row['modelLabel']}</div>
                    <div style="background:{C['border']};border-radius:3px;height:4px;max-width:200px;">
                      <div style="background:{col_c};height:4px;border-radius:3px;width:{max(pct,1)}%;"></div>
                    </div>
                  </td>
                  <td class="mono c-acc" style="text-align:right;white-space:nowrap;">{fmt(row['totalTokens'])}</td>
                  <td class="mono c-mut" style="text-align:right;white-space:nowrap;">{pct}%</td>
                  <td class="mono c-grn" style="text-align:right;white-space:nowrap;">{fmt(row['totalInput'])}</td>
                  <td class="mono c-pur" style="text-align:right;white-space:nowrap;">{fmt(row['totalOutput'])}</td>
                  <td class="mono c-amb" style="text-align:right;white-space:nowrap;">{int(row['users'])}</td>
                </tr>"""
            st.markdown(f"""
            <div style="background:{C['surface']};border:1px solid {C['border']};
                 border-radius:10px;overflow:hidden;max-height:560px;overflow-y:auto;">
            <table class="tbl">
              <thead><tr>
                <th>#</th><th>Model</th>
                <th style="text-align:right">Tokens</th>
                <th style="text-align:right">Share</th>
                <th style="text-align:right">Input</th>
                <th style="text-align:right">Output</th>
                <th style="text-align:right">Users</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table></div>""", unsafe_allow_html=True)
        with mr:
            st.markdown('<div class="sec-hdr">Top Models by Volume</div>',
                        unsafe_allow_html=True)
            top8m = msum.head(8)
            if not top8m.empty:
                st.plotly_chart(
                    hbar_chart(top8m["modelLabel"].tolist(),
                               top8m["totalTokens"].tolist(), height=320),
                    use_container_width=True, config={"displayModeBar": False})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Model Detail View</div>', unsafe_allow_html=True)
        sel_m = st.selectbox("Select a model to explore",
                             ["— select —"] + all_models, key="mdd")
        if sel_m and sel_m != "— select —":
            md = df_f[df_f["modelLabel"] == sel_m]
            if not md.empty:
                m_tot  = int(md["totalTokens"].sum())
                m_in   = int(md["totalInput"].sum())
                m_out  = int(md["totalOutput"].sum())
                m_u    = md["user"].nunique()
                ratio  = round(m_out / m_in, 2) if m_in > 0 else 0
                _cp2 = C["purple"]; _ca2 = C["accent"]; _cg2 = C["green"]
                _cb2 = C["amber"];  _cr2 = C["red"]
                model_drill_html = (
                    f"<div class='drill' style='border-left-color:{_cp2};'>"
                    f"<div style='font-size:15px;font-weight:700;margin-bottom:12px;"
                    f"word-break:break-word;'>{sel_m}</div>"
                    "<div class='stat-row'>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_ca2};'>{fmt(m_tot)}</div>"
                    "<div class='stat-l'>Total</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cg2};'>{fmt(m_in)}</div>"
                    "<div class='stat-l'>Input</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cp2};'>{fmt(m_out)}</div>"
                    "<div class='stat-l'>Output</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cb2};'>{m_u}</div>"
                    "<div class='stat-l'>Users</div></div>"
                    "<div class='stat-box'>"
                    f"<div class='stat-v' style='color:{_cr2};'>{ratio}x</div>"
                    "<div class='stat-l'>Out/In</div></div>"
                    "</div></div>"
                )
                st.markdown(model_drill_html, unsafe_allow_html=True)
                ma1, ma2 = st.columns(2, gap="large")
                with ma1:
                    st.markdown('<div class="sec-hdr" style="margin-top:16px;">Who Uses This Model</div>',
                                unsafe_allow_html=True)
                    muf = (md.groupby("user", as_index=False)["totalTokens"]
                           .sum().sort_values("totalTokens", ascending=False))
                    st.plotly_chart(
                        hbar_chart(muf["user"].tolist(),
                                   muf["totalTokens"].tolist(), height=230),
                        use_container_width=True, config={"displayModeBar": False})
                with ma2:
                    st.markdown('<div class="sec-hdr" style="margin-top:16px;">Input vs Output</div>',
                                unsafe_allow_html=True)
                    sp = go.Figure(go.Pie(
                        labels=["Input","Output"], values=[m_in, m_out], hole=0.58,
                        marker=dict(colors=[C["green"],C["purple"]],
                                    line=dict(color=C["bg"],width=2)),
                        textinfo="percent+label",
                    ))
                    sp.update_layout(**PB, height=230, showlegend=False)
                    st.plotly_chart(sp, use_container_width=True,
                                    config={"displayModeBar": False})

    # ═════════════════════════════════════════════
    # TIMELINE
    # ═════════════════════════════════════════════
    with tabs[3]:
        st.markdown('<div class="sec-hdr">Hourly Output Tokens by Model</div>',
                    unsafe_allow_html=True)
        tf = timeline_chart(df_tf)
        if tf:
            st.plotly_chart(tf, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.info("No timeline data for the current filters.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="sec-hdr">Input vs Output Trend</div>',
                    unsafe_allow_html=True)
        iotf = io_trend_chart(df_tf)
        if iotf:
            st.plotly_chart(iotf, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.info("No trend data available.")

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-top:32px;padding-top:14px;border-top:1px solid {C['border']};
         display:flex;justify-content:space-between;align-items:center;
         flex-wrap:wrap;gap:8px;">
      <span style="font-size:11px;color:{C['muted']};">
        Last refresh: {datetime.now().strftime("%H:%M:%S  %d %b %Y")}
      </span>
      <span style="font-size:11px;color:{C['muted']};">
        /aws/bedrock/invocations · auto-refresh 5 min
      </span>
    </div>""", unsafe_allow_html=True)

    time.sleep(300)
    fetch_data_region.clear()
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.authenticated:
    render_dashboard()
else:
    render_login()
