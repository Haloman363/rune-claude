# UI Fix Workflow

1. Before changing CSS, check if the issue is in the image asset itself (baked-in backgrounds, borders, padding)
2. Make the minimal CSS change needed — do NOT rewrite surrounding styles
3. Use Playwright to take a screenshot and verify the fix visually
4. If the fix didn't work, explain the root cause before trying another approach
5. Never cycle through random z-index/positioning changes
