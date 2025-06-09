import requests
import os
from slack_sdk.webhook import WebhookClient

jobURL = "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/refs/heads/dev/README.md" #CHANGE ME EACH YEAR

#load previously posted jobs
if os.path.exists("pastJobs.txt"):
    with open("pastJobs.txt", "r") as f:
        posted = set(line.strip() for line in f)
else:
    posted = set()

#get raw data
def fetch_github_jobs():
    response = requests.get(jobURL)
    return response.text

#extract data into it's parts
def extract_jobs(markdown_text):
    jobs = []
    for line in markdown_text.splitlines():
        if line.startswith("|") and "http" in line:
            parts = line.split("|")
            company = parts[1].strip()
            title = parts[2].strip()
            location = parts[3].strip()
            link = parts[4].strip()
            date = parts[5].strip()
            linkParts = link.split("\"")
            cleanLink = linkParts[1].strip()

            if cleanLink not in posted:#check if job already sent to slack
                jobs.append((company, title, location, cleanLink, date))
                posted.add(cleanLink)
    return jobs

#send new jobs to slack
def send_to_slack(jobs):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    webhook = WebhookClient(webhook_url)
    for job in jobs:
        message = f"New Internship Posted on {job[4]}!\nCompany: {job[0]}\nRole: {job[1]}\nLocation: {job[2]}\nLink: {job[3]}"
        webhook.send(text=message)

def main():
    markdown = fetch_github_jobs()
    jobs = extract_jobs(markdown)
    send_to_slack(jobs)
    #save updated job list
    with open("pastJobs.txt", "w") as f:
        f.write("\n".join(posted))

if __name__ == "__main__":
    main()