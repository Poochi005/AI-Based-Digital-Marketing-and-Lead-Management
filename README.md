# GreenNest Home Essentials – AI-Assisted Digital Campaign Planning and Lead Management

A student demonstration CRM and marketing dashboard built with **Flask, SQLite, HTML5, CSS3 and Jinja2**.
It is *inspired by* the Zoho marketing ecosystem but is **not connected** to Zoho CRM, Zoho Campaigns, Zoho Marketing Automation, Zoho Analytics or any live AI API.
Campaign performance and most analytics figures are **sample data** and are labelled that way in the app.

## Modules
Dashboard · Leads · Contacts · Deals Pipeline · Campaigns · Campaign Performance · AI Content Studio (local templates) · Marketing Automation (visual workflow) · Analytics · Settings

## Run it on Windows (VS Code)
1. Install **Python 3.10+** from python.org (tick *Add Python to PATH*).
2. Open this folder in VS Code (**File → Open Folder**), then open the terminal (**Terminal → New Terminal**).
3. Create a virtual environment and activate it:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` first.
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Start the app:
   ```
   python app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser. Press `Ctrl+C` in the terminal to stop.

The database file `greennest.db` is created automatically with sample records on first run. Delete it to reset the data.

## How the data works
- **Leads** and **Campaigns** are the two SQLite tables.
- Dashboard numbers are counted from the database. *Contacts* = leads with status Contacted, Qualified, Proposal or Converted. *Deals in progress* = Qualified + Proposal.
- Changing a lead's status (Leads page, Deals page or Edit form) updates the database immediately.

## Project structure
```
app.py            Flask routes, database setup, sample data
templates/        Jinja2 pages
static/style.css  Styling
requirements.txt  Python dependencies
```

## Git and GitHub
```
git init
git add .
git commit -m "GreenNest CRM"
```
Then create an empty repository on GitHub and follow its "push an existing repository" steps.
