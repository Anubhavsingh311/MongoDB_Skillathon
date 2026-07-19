# 04 — MongoDB Atlas

## Self-Managed vs. Fully-Managed

| | Self-Managed | Fully-Managed |
|---|---|---|
| Setup | Administrator handles all hardware and software | Vendor handles operational tasks |
| Control | Full | Configurable but not total |
| Overhead | High — security, backups, upgrades are manual | Low — vendor automates routine operations |
| Best for | Environments requiring total control | Teams that want to focus on the application, not infrastructure |

---

## SaaS and DBaaS

**SaaS (Software as a Service):** Software hosted centrally; users pay a subscription and access it without local installation. The vendor handles hosting, maintenance, and hardware. Example: Google Docs.

**DBaaS (Database as a Service):** SaaS applied specifically to database provisioning and management. The vendor handles security patches, hardware provisioning, and infrastructure.

**MongoDB Atlas** is MongoDB's DBaaS offering.

---

## MongoDB Atlas

- Available on **all major cloud providers**: AWS, Google Cloud, Azure
- MongoDB manages security updates and cloud hardware provisioning on your behalf
- You retain control over configuration without managing the underlying infrastructure
- Supports a rich, modern feature set beyond just hosting (search, analytics, data federation, etc.)

### Free Tier (M0)
- Available at signup with no credit card required
- Sufficient for learning, prototyping, and small projects
- Includes the option to preload a **sample dataset** for immediate experimentation

---

## Deploying a Free Cluster — Steps

1. **Create an Atlas account** at the registration page
2. **Verify your email** via the confirmation link MongoDB sends
3. **Complete account setup** by answering the onboarding form
4. **Deploy a cluster:**
   - Select **M0** (free tier)
   - Name the cluster
   - Enable *Automate security setup* to whitelist your current IP
   - Enable *Preload sample dataset* for built-in sample data
   - Select a cloud provider and region (defaults to AWS with a recommended region)
   - Click **Create Deployment**
5. **Create a database user** with credentials (separate from your Atlas login)

---

## Key Takeaways

- **Self-managed** gives full control at the cost of significant operational overhead
- **Fully-managed / DBaaS** offloads infrastructure work so you can focus on building
- **MongoDB Atlas** is the DBaaS for MongoDB, available on AWS, GCP, and Azure
- The **M0 free tier** is enough to start learning and prototyping immediately
- Students are eligible for **$50 in Atlas credits** via the MongoDB Student Pack

---

## Full Course Summary

| Module | Core Concept |
|---|---|
| 01 — Database Fundamentals | DBMS, SQL vs. NoSQL, schemas, data types |
| 02 — The Document Model | Flexible schema, hierarchy, JSON syntax, the golden rule |
| 03 — Distributed Architecture | Scaling, sharding, replication, CAP theorem |
| 04 — MongoDB Atlas | DBaaS, fully-managed hosting, free cluster setup |
