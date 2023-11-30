# Copyright (c) 2022, AgriTheory and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	return get_columns(filters), get_data(filters)


def get_columns(filters):
	return [
		{
			"label": frappe._("Cash Account"),
			"fieldname": "cash_account",
			"fieldtype": "Data",
			"options": "Cash Account",
			"width": "150px"
		},
		{
			"label": frappe._("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": "150px"
		},
		{
			"label": frappe._("Check Number"),
			"fieldname": "check_number",
			"fieldtype": "Data",
			"width": "200px",
		},
		{
			"label": frappe._("Check Date"),
			"fieldname": "check_date",
			"fieldtype": "Date",
			"width": "150px",
		},
		{
			"label": frappe._("Party Name"),
			"fieldname": "party_name",
			"fieldtype": "Data",
			"width": "400px",
		},
	]

def get_dataOLDWAYBEFOREREMORAT(filters):
	paymentEntries = frappe.db.sql("""
		SELECT
			`tabPayment Entry`.reference_no AS check_number,
			`tabPayment Entry`.reference_date AS check_date,
			`tabPayment Entry`.party_name AS party_name,
			`tabPayment Entry`.paid_amount AS amount,
			`tabPayment Entry`.paid_from AS cash_account
		FROM `tabPayment Entry`
		WHERE
		`tabPayment Entry`.reference_date >= %(start_date)s 
		AND `tabPayment Entry`.reference_date <= %(end_date)s
		AND `tabPayment Entry`.bank_account = %(bank_account)s
		AND `tabPayment Entry`.payment_type = 'Pay'
		AND `tabPayment Entry`.mode_of_payment = 'Check'
		AND `tabPayment Entry`.docstatus = 1
		ORDER BY check_date
		""", {
			'start_date': filters.start_date,
			'end_date': filters.end_date,
			'bank_account': filters.bank_account
	}, as_dict=True)

	#only keep the first numbers in the paid_from field
	for paymentEntry in paymentEntries:
		paymentEntry.cash_account = paymentEntry.cash_account.split("-")[0]

	return paymentEntries

def get_data(filters):
	pe = frappe.qb.DocType("Payment Entry")
	mop = frappe.qb.DocType("Mode of Payment")
	return (
		frappe.qb.from_(pe)
		.inner_join(mop)
		.on(pe.mode_of_payment == mop.name)
		.select(
			(pe.reference_no).as_("check_number"),
			(pe.reference_date).as_("check_date"),
			(pe.paid_amount).as_("amount"),
			(pe.paid_from).as_("cash_account"),
			(pe.party_name).as_("party_name"),
			pe.party_name,
		)
		.where(pe.reference_date >= filters.start_date)
		.where(pe.reference_date <= filters.end_date)
		.where(pe.bank_account == filters.bank_account)
		.where(mop.type == "Bank")
		.where(pe.docstatus == 1)
		.orderby(pe.reference_date)
		.run(as_dict=True)
	)
