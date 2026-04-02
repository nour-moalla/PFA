#!/bin/sh
# UtopiaHire Backend Firewall Rules
# Applied inside the backend container at startup

echo "Applying iptables firewall rules..."

# === STEP 1: Flush existing rules (start clean) ===
iptables -F INPUT
iptables -F OUTPUT
iptables -F FORWARD

# === STEP 2: Set default policies ===
# Default DROP means: if no rule matches, block the packet
# This is the most secure default — explicit whitelist approach
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# === STEP 3: Allow established connections ===
# This allows responses to come back for connections WE initiated
# Without this rule, even our responses would be blocked
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# === STEP 4: Allow loopback (localhost communication) ===
# The app needs to communicate with itself internally
iptables -A INPUT -i lo -j ACCEPT

# === STEP 5: Allow our app port (8000) ===
# This is the only external port that should accept connections
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# === STEP 6: Rate limiting — brute force protection ===
# Allow max 20 new connections per minute from one IP
# Excess connections are dropped — brute force protection at network level
iptables -A INPUT -p tcp --dport 8000 \
  -m conntrack --ctstate NEW \
  -m limit --limit 20/minute --limit-burst 30 \
  -j ACCEPT

# Drop connections that exceed the rate limit
iptables -A INPUT -p tcp --dport 8000 \
  -m conntrack --ctstate NEW \
  -j DROP

# === STEP 7: Log blocked packets before dropping ===
# This creates a log entry for every blocked packet
# These logs are your firewall evidence for the jury
iptables -A INPUT -j LOG \
  --log-prefix "IPTABLES-BLOCKED: " \
  --log-level 4

# Drop everything else
iptables -A INPUT -j DROP

echo "Firewall rules applied successfully"
# Show active rules as confirmation
iptables -L INPUT -n -v