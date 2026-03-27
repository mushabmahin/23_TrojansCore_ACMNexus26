from backend.pipeline import run_pipeline, get_output

# Run full pipeline
df = run_pipeline()

print("\n=== FULL DATAFRAME ===")
print(df.head())

print("\n=== OUTPUT (FOR UI) ===")
output = get_output()

for row in output:
    print(row)