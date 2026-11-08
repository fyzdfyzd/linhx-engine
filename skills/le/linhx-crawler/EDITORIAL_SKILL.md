---
name: linhx-editorial-pipeline
description: Filter crawled news articles based on editorial principles (AI4BIZ) and write them as professional News Stories in DTL's personal brand voice (Linh's Alt). Automatically creates wiki logs in the run directory.
---

# LinhX Editorial Pipeline

A pipeline to process crawled news articles and convert them into strategic, conversational, and highly engaging News Stories in DTL's personal brand voice (Linh's Alt), aligning with the CafeBiz AI4BIZ editorial principles.

## Use this skill when

- A project scan has completed (e.g., project `RUN_3WEB_2PAGE`) and you have fresh crawled articles.
- You need to filter out noise/hype and select high-value articles about practical business AI, AI workforce, or micro-businesses.
- You need to group/cluster relevant articles into core themes (News Stories).
- You want to rewrite these themes into complete Vietnamese posts/articles using the DTL content creation process.
- You need to automatically document what was written in a central wiki log file (`wiki_written_log.md`).

## Instructions

### Prerequisites
The python environment should have `google-genai` installed and the `.env` file must contain `GEMINI_API_KEY`.

### 1. Run the Pipeline on the Latest Scan
To auto-discover the latest project scan run and process it:

```powershell
cd d:\LINHX_CRAWLER\server
python run_editorial_pipeline.py
```

### 2. Run the Pipeline on a Specific Run Folder
If you want to target a specific run datetime folder:

```powershell
cd d:\LINHX_CRAWLER\server
python run_editorial_pipeline.py --run-dir d:\LINHX_CRAWLER\data\RUN_3WEB_2PAGE\2026-06-04_11-46-38
```

## Outputs Produced

For every successful run, the pipeline creates:
1. `editorial/stories/`: Folder under the targeted run folder.
   - `<story-slug>_dtl.json`: Structured JSON containing DTL's title, hook, body, meta description, visual design proposal, and references.
   - `<story-slug>_dtl.md`: Markdown version of the rewritten story.
2. `wiki_written_log.md`: Located in the run folder root.
   - Contains a summary index table of written stories.
   - Contains the full markdown content of each written story.

## Best Practices

### Brand Persona (Linh's Alt)
- Avoid using corporate buzzwords, empty PR praise, or overly technical jargon.
- Write in a natural, conversational, and intellectually curious tone (conversing with the reader).
- Infuse every article with a unique strategic angle (e.g., the psychological or business model shifts behind the tech).
- Always include the **Visual Model Proposal** to help readers visualize the logical argument of the article.
