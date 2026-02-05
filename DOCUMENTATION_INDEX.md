# Documentation Index: Carbon Credit Calculator with Chave Equation

## Welcome 👋

This is your guide to navigating the complete **real-time carbon credit calculator** implementation with the **Chave allometric equation** for tree biomass estimation.

---

## Quick Navigation

### I Want to...

**Get Started Quickly (5 minutes)**
→ Read: [`QUICKSTART.md`](#quickstart)

**Understand the System Architecture**
→ Read: [`README_CHAVE_INTEGRATION.md`](#readme) + [`IMPLEMENTATION_SUMMARY.md`](#implementation)

**Set Up ESP32 Hardware**
→ Read: [`REALTIME_ESP32_SETUP.md`](#realtime-setup)

**Know What Changed**
→ Read: [`CHANGES_MADE.md`](#changes)

**Deploy to Production**
→ Read: [`DEPLOYMENT_CHECKLIST.md`](#deployment)

**Understand Tree Species Data**
→ Read: [`TREE_SPECIES_REFERENCE.md`](#species)

**Test Locally Before Deploying**
→ Use: `python victori/functions/test_chave.py`

**Troubleshoot Issues**
→ See: [`DEPLOYMENT_CHECKLIST.md` - Troubleshooting Section](#deployment)

---

## Documentation Files

### README_CHAVE_INTEGRATION.md {#readme}
**📖 Main Overview Document**

**What it covers:**
- System overview with ASCII diagrams
- Key features explained
- Chave equation formula and explanation
- Real-world calculation example
- Technology stack
- Real-time data flow
- Quick testing commands
- Troubleshooting quick reference

**Best for:**
- Understanding what was built
- Getting a high-level overview
- Sharing with team members
- Quick reference

**Read time:** 15-20 minutes

---

### QUICKSTART.md {#quickstart}
**⚡ 5-Minute Setup Guide**

**What it covers:**
- 5-minute ESP32 configuration
- Quick webhook testing
- Dashboard verification
- Key metrics explanation
- Chave equation reference
- Sensor calibration tips
- Troubleshooting checklist
- File structure

**Best for:**
- First-time setup
- Getting dashboard running quickly
- Testing basic functionality
- Quick reference during setup

**Read time:** 5-10 minutes

---

### REALTIME_ESP32_SETUP.md {#realtime-setup}
**🔧 Complete Integration Guide**

**What it covers:**
- System architecture diagrams
- Complete Chave equation derivation
- ESP32 hardware setup (pin configuration)
- Arduino sketch setup and configuration
- Data flow explanation
- Dashboard real-time updates
- Health score calculation
- Image capture & analysis
- Webhook testing procedures
- Dashboard features
- Troubleshooting detailed guide
- File location reference

**Best for:**
- Detailed hardware setup
- Understanding the full system
- Solving integration issues
- Reference during development

**Read time:** 30-45 minutes

---

### TREE_SPECIES_REFERENCE.md {#species}
**🌳 Tree Species & Carbon Offset Data**

**What it covers:**
- 20+ tree species with wood densities
- Regional recommendations
- Carbon offset calculations by species
- Detailed calculation examples
- Testing with Python script
- Monthly CO₂ tables by tree size
- Wood density categories
- Regional carbon strategies
- Species integration in dashboard

**Best for:**
- Understanding species differences
- Calculating carbon offsets
- Planning which trees to monitor
- Testing different scenarios

**Read time:** 20-25 minutes

---

### IMPLEMENTATION_SUMMARY.md {#implementation}
**📋 Architecture & Technical Details**

**What it covers:**
- What was implemented (overview)
- Chave equation reference with math
- Health score calculation
- Real-time data architecture
- Database schema
- Configuration file details
- Testing procedures
- File modifications summary
- Equations summary table
- Support resources

**Best for:**
- Understanding technical implementation
- Reference during debugging
- Understanding database schema
- Learning the calculations

**Read time:** 25-30 minutes

---

### DEPLOYMENT_CHECKLIST.md {#deployment}
**✅ Production Deployment Guide**

**What it covers:**
- Pre-deployment requirements checklist
- Hardware preparation steps
- Supabase configuration
- ESP32 programming guide
- Dashboard configuration
- Security setup
- Performance optimization
- Post-deployment monitoring
- Troubleshooting quick reference
- Sign-off section
- Version control

**Best for:**
- Preparing for production
- Ensuring nothing is missed
- Post-deployment monitoring
- Troubleshooting in production

**Read time:** 45-60 minutes

---

### CHANGES_MADE.md {#changes}
**📝 Summary of All Modifications**

**What it covers:**
- Complete list of modified files
- New files created
- Line-by-line explanation of changes
- Technical implementation details
- Integration points
- Performance characteristics
- Security considerations
- Backward compatibility
- Testing completed
- Deployment steps

**Best for:**
- Understanding what changed
- Code review
- Integration planning
- Understanding modified files

**Read time:** 30-40 minutes

---

### DOCUMENTATION_INDEX.md {#index}
**📑 This File - Your Navigation Guide**

Helps you find the right document for your needs.

---

## Documentation by Purpose

### For Setup & Configuration

1. **First time?** → Start with [`QUICKSTART.md`](#quickstart) (5 min)
2. **Need details?** → Read [`REALTIME_ESP32_SETUP.md`](#realtime-setup) (45 min)
3. **Ready to deploy?** → Use [`DEPLOYMENT_CHECKLIST.md`](#deployment) (60 min)

### For Understanding the System

1. **High-level overview?** → Read [`README_CHAVE_INTEGRATION.md`](#readme) (20 min)
2. **Technical deep-dive?** → Read [`IMPLEMENTATION_SUMMARY.md`](#implementation) (30 min)
3. **What changed?** → Read [`CHANGES_MADE.md`](#changes) (40 min)

### For Reference Data

1. **Tree species info?** → See [`TREE_SPECIES_REFERENCE.md`](#species) (25 min)
2. **Chave equation?** → See [`README_CHAVE_INTEGRATION.md`](#readme#chave) + [`REALTIME_ESP32_SETUP.md`](#realtime-setup#chave)
3. **Health score?** → See [`IMPLEMENTATION_SUMMARY.md`](#implementation#health)
4. **Database schema?** → See [`IMPLEMENTATION_SUMMARY.md`](#implementation#schema)

### For Testing & Troubleshooting

1. **Test locally?** → Run `python victori/functions/test_chave.py --help`
2. **Quick troubleshooting?** → See [`QUICKSTART.md`](#quickstart#troubleshooting)
3. **Detailed troubleshooting?** → See [`DEPLOYMENT_CHECKLIST.md`](#deployment#troubleshooting)
4. **Real-time issues?** → See [`REALTIME_ESP32_SETUP.md`](#realtime-setup#troubleshooting)

---

## File Structure Reference

```
Documentation Files:
├── DOCUMENTATION_INDEX.md          ← You are here
├── README_CHAVE_INTEGRATION.md     ← Main overview
├── QUICKSTART.md                   ← 5-minute setup
├── REALTIME_ESP32_SETUP.md        ← Complete guide
├── TREE_SPECIES_REFERENCE.md      ← Species data
├── IMPLEMENTATION_SUMMARY.md      ← Technical details
├── DEPLOYMENT_CHECKLIST.md        ← Production ready
└── CHANGES_MADE.md                ← What changed

Code Files:
├── victori/
│   ├── ESP32_SETUP/
│   │   └── tree_sensor_esp32.ino       ← ESP32 firmware
│   ├── functions/
│   │   ├── chave_calculator.py         ← Biomass calculator
│   │   └── test_chave.py               ← Testing utility
│   └── src/
│       └── App.vue                      ← Dashboard
├── supabase/functions/
│   ├── receive-sensor-data/index.ts   ← Webhook
│   └── upload-tree-image/index.ts     ← Image upload
```

---

## Key Concepts Explained

### Chave Allometric Equation
Calculates tree biomass from measurements:
$$AGB = 0.0919 \times (\rho \times DBH^2 \times H)^{0.906}$$

**Where:**
- AGB = Above Ground Biomass (kg)
- ρ = Wood density (species-specific)
- DBH = Diameter at Breast Height (cm)
- H = Tree height (m)

**See:** [`README_CHAVE_INTEGRATION.md`](#readme#chave) for full explanation

### Health Score
Tree health based on environmental factors (0-100%):
- Optimal temperature: 25°C
- Optimal humidity: 70%
- Optimal light: 800 µmol/m²/s

**See:** [`IMPLEMENTATION_SUMMARY.md`](#implementation#health) for calculation

### Carbon Credits
1 credit = 10 kg of CO₂ offset annually

**See:** [`TREE_SPECIES_REFERENCE.md`](#species) for examples

### Real-time Updates
Dashboard updates < 2 seconds after ESP32 sends data via webhook

**See:** [`README_CHAVE_INTEGRATION.md`](#readme#dataflow) for architecture

---

## Quick Reference Tables

### Document Difficulty Levels

| Level | Documents | Time |
|-------|-----------|------|
| **Beginner** | QUICKSTART | 5-10 min |
| **Intermediate** | README + IMPLEMENTATION | 30-40 min |
| **Advanced** | REALTIME_SETUP + DEPLOYMENT | 60-90 min |
| **Reference** | SPECIES + CHANGES | 30-50 min |

### Document Update Frequency

| Document | Update Frequency | Last Updated |
|----------|------------------|--------------|
| QUICKSTART | Rarely | 2026-02-05 |
| README | Rarely | 2026-02-05 |
| REALTIME_SETUP | As needed | 2026-02-05 |
| DEPLOYMENT | As needed | 2026-02-05 |
| SPECIES | Quarterly | 2026-02-05 |
| CHANGES | Never (historical) | 2026-02-05 |

---

## Common Workflows

### Workflow 1: Initial Setup (30 minutes)
1. Read [`QUICKSTART.md`](#quickstart) (5 min)
2. Configure ESP32 sketch (10 min)
3. Upload firmware (5 min)
4. Test webhook with cURL (5 min)
5. Verify dashboard (5 min)

### Workflow 2: Production Deployment (2-3 hours)
1. Review [`DEPLOYMENT_CHECKLIST.md`](#deployment) (30 min)
2. Check all items in checklist (60 min)
3. Configure security (20 min)
4. Deploy functions (20 min)
5. Test thoroughly (20 min)

### Workflow 3: Troubleshooting (varies)
1. Check browser console errors
2. See quick troubleshooting in [`QUICKSTART.md`](#quickstart)
3. See detailed troubleshooting in [`DEPLOYMENT_CHECKLIST.md`](#deployment)
4. Run `python test_chave.py` for calculation issues
5. Review [`REALTIME_ESP32_SETUP.md`](#realtime-setup) for details

### Workflow 4: Understanding Species Differences (45 minutes)
1. Read [`TREE_SPECIES_REFERENCE.md`](#species) (25 min)
2. Test calculations: `python test_chave.py --list-species` (5 min)
3. Run examples: `python test_chave.py --species mango` (10 min)
4. Review dashboard integration (5 min)

---

## Links to Key Sections

### Formulas & Equations
- **Chave Equation**: [`README_CHAVE_INTEGRATION.md`](README_CHAVE_INTEGRATION.md#chave) | [`REALTIME_ESP32_SETUP.md`](REALTIME_ESP32_SETUP.md#chave)
- **Health Score**: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md#health)
- **CO₂ Conversion**: [`TREE_SPECIES_REFERENCE.md`](TREE_SPECIES_REFERENCE.md#conversion)

### Configuration Guides
- **ESP32 Setup**: [`REALTIME_ESP32_SETUP.md`](REALTIME_ESP32_SETUP.md#esp32-setup)
- **Dashboard Config**: [`QUICKSTART.md`](QUICKSTART.md#dashboard)
- **Supabase Setup**: [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md#supabase)

### Testing & Verification
- **Local Testing**: `python victori/functions/test_chave.py`
- **Webhook Testing**: [`QUICKSTART.md`](QUICKSTART.md#webhook-test)
- **Real-time Testing**: [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md#realtime)

### Troubleshooting
- **Quick Fix**: [`QUICKSTART.md`](QUICKSTART.md#troubleshooting)
- **Detailed Help**: [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md#troubleshooting)
- **Integration Help**: [`REALTIME_ESP32_SETUP.md`](REALTIME_ESP32_SETUP.md#troubleshooting)

---

## Version & Support

**Current Version**: 1.0  
**Released**: February 5, 2026  
**Status**: Production Ready ✅

**For Support:**
1. Check relevant documentation section
2. Run local tests with `test_chave.py`
3. Review browser console (F12)
4. Check ESP32 serial output (115200 baud)
5. Review Supabase function logs

---

## Document Statistics

| Aspect | Count |
|--------|-------|
| Total Documentation Pages | 8 |
| Total Words | 15,000+ |
| Code Examples | 50+ |
| Diagrams | 15+ |
| Tables | 40+ |
| Formulas | 10+ |
| Tree Species Covered | 20+ |

---

## Getting Help

### If you're stuck on...

| Topic | See Document | Section |
|-------|------|---------|
| Setup | QUICKSTART | Getting Started |
| ESP32 | REALTIME_SETUP | ESP32 Hardware |
| Dashboard | README | Real-time Dashboard |
| Calculations | TREE_SPECIES | Examples |
| Deployment | DEPLOYMENT_CHECKLIST | Full Checklist |
| Trees | TREE_SPECIES | Species Reference |
| Real-time | REALTIME_SETUP | Data Flow |
| Issues | DEPLOYMENT_CHECKLIST | Troubleshooting |

---

## Next Steps

**Start here based on your situation:**

### 👤 I'm New to This Project
1. Read [`README_CHAVE_INTEGRATION.md`](#readme) (overview)
2. Read [`QUICKSTART.md`](#quickstart) (setup)
3. Start configuring ESP32

### 🚀 I'm Ready to Deploy
1. Read [`DEPLOYMENT_CHECKLIST.md`](#deployment) (full checklist)
2. Work through each item
3. Deploy to production

### 🔍 I'm Troubleshooting
1. See [`QUICKSTART.md`](#quickstart#troubleshooting) (quick fixes)
2. See [`DEPLOYMENT_CHECKLIST.md`](#deployment#troubleshooting) (detailed)
3. Run `python test_chave.py` (verify locally)

### 📚 I'm Learning the Details
1. Read [`IMPLEMENTATION_SUMMARY.md`](#implementation) (technical)
2. Read [`TREE_SPECIES_REFERENCE.md`](#species) (reference data)
3. Review [`REALTIME_ESP32_SETUP.md`](#realtime-setup) (complete guide)

---

## Document Maintenance

Last updated: February 5, 2026  
Maintained by: Carbon Credit Calculator Team  
Questions? Check relevant section or run tests locally.

---

**Ready to get started?** Start with [`QUICKSTART.md`](#quickstart)! 🌱
