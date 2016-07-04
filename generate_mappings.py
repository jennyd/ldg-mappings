#!/usr/bin/env python

import csv


# Find all the LGSLs used in the LDG service CSV and put them in a dict, where
# we will collate the URLs they should redirect to.
with open('local_authority_service_details-20160628.csv') as f:
    reader = csv.DictReader(f)
    all_ldg_lgsls = [int(row['LGSL']) for row in reader]

ldg_lgsls = sorted(list(set(all_ldg_lgsls)))
lgsls_to_mappings = {lgsl: None for lgsl in ldg_lgsls}


# Add the redirects for orange transactions into the LGSL mapping dict.
with open('orange-transaction-redirects.csv') as f:
	reader = csv.DictReader(f)
	orange_transactions_by_lgsl = {}
	for row in reader:
		lgsl = int(row['LGSL'])
		if lgsl in orange_transactions_by_lgsl:
			print 'LGSL already in orange_transactions_by_lgsl: {}'.format(lgsl)
		else:
			orange_transactions_by_lgsl[lgsl] = row


def clean_url_from_spreadsheet(url):
	if url and url.startswith('gov.uk'):
		return 'https://www.' + url
	elif url == 'n/a':
		return ''
	else:
		return url

for lgsl, row in orange_transactions_by_lgsl.items():
	if lgsl in lgsls_to_mappings:
		lgsls_to_mappings[lgsl] = clean_url_from_spreadsheet(row['redirect to'])
	else:
		print 'Found LGSL for orange transaction which wasn\'t in the LDG CSV: {}'.format(lgsl)


# Add the redirects for transactions on GOV.UK into the LGSL mapping dict.
with open('govuk-local-transactions.csv') as f:
	reader = csv.DictReader(f)
	govuk_local_transactions_by_lgsl = {}
	for row in reader:
		lgsl = int(row['lgsl'])
		if lgsl in govuk_local_transactions_by_lgsl:
			if govuk_local_transactions_by_lgsl[lgsl]['lgil_override'] == '8':
				continue
			elif row['lgil_override'] == '8':
				govuk_local_transactions_by_lgsl[lgsl] = row
			else:
				print 'LGSL {} already in govuk_local_transactions_by_lgsl but LGIL 8 not found'.format(lgsl)
		else:
			govuk_local_transactions_by_lgsl[lgsl] = row

for lgsl, row in govuk_local_transactions_by_lgsl.items():
	if lgsl in lgsls_to_mappings:
		lgsls_to_mappings[lgsl] = row['url']
	else:
		print 'Found LGSL for GOV.UK local transaction which wasn\'t in the LDG CSV: {}'.format(lgsl)


# Write the LGSLs and their mappings to a new CSV file.
ldg_lgsls_for_csv = sorted([
	{'LDG LGSL': lgsl, 'mapping': mapping}
	for lgsl, mapping in lgsls_to_mappings.items()
])
lgsl_csv = 'ldg_lgsls_with_mappings.csv'
with open(lgsl_csv, 'w') as f:
    writer = csv.DictWriter(f, ['LDG LGSL', 'mapping'])
    writer.writeheader()
    for row in ldg_lgsls_for_csv:
        writer.writerow(row)


# Use the LGSL dict to construct mappings using all the paths for LGSLs and
# write them to a new CSV file.
paths_for_lgsl_mappings = (
	'/ldgredirect/locationsearch.do?lgsl={}',
	'/ldgredirect/maplocationsearch.do?lgsl={}',
	'/ldgredirect/start.do?lgsl={}',
	'/ldgredirect/index.jsp?lgsl={}'
)
mappings_for_csv = [
	{'path': path.format(lgsl), 'mapping': mapping}
	for lgsl, mapping in lgsls_to_mappings.items()
	for path in paths_for_lgsl_mappings
]
mappings_csv = 'mappings.csv'
with open(mappings_csv, 'w') as f:
    writer = csv.DictWriter(f, ['path', 'mapping'])
    writer.writeheader()
    for row in mappings_for_csv:
        writer.writerow(row)
