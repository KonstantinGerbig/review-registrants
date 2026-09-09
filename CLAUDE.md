# review-registrants

Scripts that process a raw Google Form CSV of conference registrant submissions into a sorted review sheet.

The method (scripts, defaults) is committed. All data — raw CSVs, email/name lists, outputs — lives in `data/`, which is gitignored.

`defaults/` contains template files to copy into `data/` and fill in per conference. `sort_registrants.py` deduplicates entries and assigns each registrant to one of four tiers (I Whitelisted, II Preferred, III Normal, IV Incomplete) based on rules defined in `data/tier_rules.py`, then adds empty reviewer columns to `data/outputs/review_sheet.csv`. `render_abstracts.py` renders that sorted output as a formatted markdown document. `plot_registrants.py` generates overview bar and pie charts.
