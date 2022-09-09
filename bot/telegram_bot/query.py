import json
import os
from typing import List

import pandas as pd


def check_user_snps(snps: List, clinvar_df: pd.DataFrame) -> List:
    snps_df = pd.DataFrame.from_records(snps)
    snps_df = snps_df.merge(clinvar_df, how='left', left_on='rs', right_on='rs')

    snps_df = snps_df[~snps_df['rs_id'].isna()].copy()

    significant_items = []
    for _, row in snps_df.iterrows():
        gt = row['genotype']
        alt = row['alt']
        for a in alt:
            if a in gt:
                significant_items.append(
                    {
                        'rs': row['rs'],
                        'alt': alt,
                        'genotype': gt,
                        'significance': row['clnsig'],
                        'description': row['clndn']
                    }
                )

    return significant_items


def main():
    snps = []
    with open('2037-9118.txt') as f:
        for line in f.readlines():
            if line[0] == '#':
                continue
            tokens = line.split()
            if tokens[1] != '1':
                continue
            try:
                snp = {
                    'rs': int(tokens[0][2:]),
                    'genotype': tokens[3]
                }
                snps.append(snp)
            except ValueError:
                pass
    # print(len(snps))

    clinvar_dir = os.path.join(os.path.dirname(__file__), 'api/data/clinvar_filtered.json')
    with open(clinvar_dir, 'r') as file:
        clinvar = json.load(file)

    clinvar_df = pd.DataFrame.from_records(clinvar)
    clinvar_df['rs_int'] = clinvar_df['rs_id'].apply(lambda x: x.isnumeric())
    clinvar_df = clinvar_df[clinvar_df['rs_int']].copy().drop('rs_int', axis=1)
    clinvar_df['rs'] = clinvar_df['rs_id'].astype(int)

    result = check_user_snps(snps, clinvar_df)

    df = pd.DataFrame.from_records(result)
    print(df)


if __name__ == '__main__':
    main()
