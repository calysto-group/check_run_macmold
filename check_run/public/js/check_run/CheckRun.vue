<template>
	<div>
		<ModeOfPaymentSummary :transactions="transactions" :pay_to_account_currency="pay_to_account_currency" :status="state.status"/>
		<table class="table table-compact table-hover check-run-table" style="text-align: center; margin: 0">
			<thead>
				<tr>
					<th style="text-align: left" class="col col-sm-2" id="check-run-party-filter">
						<span class="party-onclick party-display">Supplier</span>
						<span class="filter-icon">
							<svg class="icon icon-sm" style="" @click="toggleShowPartyFilter()">
								<use class="" href="#icon-filter"></use>
							</svg>
						</span>
						<div class="party-filter" v-if="state.show_party_filter">
							<input type="text" class="form-control" v-model="state.party_filter" />
						</div>
					</th>
					<th class="col col-sm-2 sup">Sup. Invoice NO</th>
					<th class="col col-sm-2" style="white-space: nowrap; width: 12.49%">
						Invoice Date
						<span
							@click="sortTransactions('posting_date')"
							class="check-run-sort-indicator"
							id="check-run-doc-date-sort"
							>&#11021;</span
						>
					</th>
					<th class="col col-sm-2">
						Outstanding Amount
						<span @click="sortTransactions('amount')" class="check-run-sort-indicator" id="check-run-outstanding-sort"
							>&#11021;</span
						>
					</th>
					<th class="col col-sm-2">
						Amount Paid
					</th>
					<th class="col col-sm-1">
						Due Date
						<span @click="sortTransactions('due_date')" class="check-run-sort-indicator" id="check-run-due-date-sort"
							>&#11021;</span
						>
					</th>
					<th v-if="state.status == 'Draft'" class="col col-sm-1" style="text-align: left">
						<input
							type="checkbox"
							autocomplete="off"
							class="input-with-feedback reconciliation"
							data-fieldtype="Check"
							id="select-all"
							v-model="selectAll" /><span>Select All</span>
					</th>
					<th v-else class="col col-sm-1">Check Number | Reference</th>
				</tr>
			</thead>
			<tbody>
				<template v-for="(item, i) in transactions">
					<tr
						v-if="partyIsInFilter(item.party)"
						:key="i"
						class="checkrun-row-container"
						:class="{ selectedRow: state.selectedRow == i }"
						tabindex="1"
						@click="state.selectedRow = i">
						<td style="text-align: left">{{ item.party_name || item.party }}</td>
						<td style="text-align: left;white-space: nowrap;">
							<a :href="transactionUrl(item)" target="_blank">
								{{ item.ref_number || item.name }}
							</a>
							<div v-if="item.attachments.length > 1" style="float: right;" class="dropdown show">
							  <a class="btn btn-default btn-xs dropdown-toggle" href="#" role="button" :id="item.name" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
							    <i class="fa fa-search"></i>
							  </a>
							  <div class="dropdown-menu" :aria-labelledby="item.name">
							    <a v-for="attachment in item.attachments" class="dropdown-item" href="javascript:;" @click="showPreview(attachment.file_url)" data-pdf-preview="item">{{ attachment.file_name }}</a>
							  </div>
							</div>

							<button v-if="item.attachments.length == 1" style="float: right;" type="button" class="btn btn-secondary btn-xs" @click="showPreview(item.attachments)" data-pdf-preview="item">
								<i @click="showPreview(item.attachments)" data-pdf-preview="item" class="fa fa-search"></i>
							</button>
						</td>
						<td>{{ item.posting_date }}</td>
						<td>{{ format_currency(item.amount, pay_to_account_currency, 2) }}</td>
						<td>
							<input
								type="text"
								class="form-control"
								v-model="item.amount"
								:data-amount-paid-index="i"
								@change="onAmountPaidChange(i)"
								:disabled="state.docstatus > 0"
							/>
						</td>
						<td>{{ moment(item.due_date).format('MM/DD/YY') }}</td>
						<td v-if="state.status == 'Draft'" style="text-align: left">
							<input
								type="checkbox"
								class="input-with-feedback checkrun-check-box"
								data-fieldtype="Check"
								@change="onPayChange(i)"
								:data-checkbox-index="i"
								v-model="item.pay"
								:id="item.id" />Pay
						</td>
						<td v-else>
							<a target="_blank" :href="paymentEntryUrl(item)"> {{ item.payment_entry }}</a>
						</td>
					</tr>
				</template>
			</tbody>
		</table>
	</div>
</template>
<script>
import ADropdown from './ADropdown.vue'
import ModeOfPaymentSummary from './ModeOfPaymentSummary.vue'

export default {
	name: 'CheckRun',
	components: {
		ADropdown,
		ModeOfPaymentSummary,
	},
	props: ['transactions', 'modes_of_payment', 'status', 'state'],
	data() {
		return {
			selectAll: false,
			sort_order: {
				posting_date: 1,
				mode_of_payment: 1,
				amount: 1,
				due_date: 1,
			},
			modeOfPaymentNames: this.modes_of_payment.map(mop => mop.name),
			pay_to_account_currency: '',
		}
	},
	watch: {
		selectAll: (val, oldVal) => {
			cur_frm.check_run_state.transactions.forEach(row => {
				row.pay = val
			})
			cur_frm.doc.amount_check_run = cur_frm.check_run_state.check_run_total()
			cur_frm.refresh_field('amount_check_run')
			cur_frm.dirty()
		},
	},
	methods: {
		onAmountPaidChange(index) {
			//change to parseint
			let amount = parseInt(this.transactions[index].amount)
			if(isNaN(amount)) {
				amount = 0
			}
			this.transactions[index].amount = amount
			cur_frm.doc.amount_check_run = cur_frm.check_run_state.check_run_total()
			cur_frm.dirty()
		},
		transactionUrl: transaction => {
			if (transaction.doctype !== 'Journal Entry') {
				return encodeURI(
					`${frappe.urllib.get_base_url()}/app/${transaction.doctype.toLowerCase().replace(' ', '-')}/${
						transaction.name
					}`
				)
			} else {
				return encodeURI(
					`${frappe.urllib.get_base_url()}/app/${transaction.doctype.toLowerCase().replace(' ', '-')}/${
						transaction.ref_number
					}`
				)
			}
		},
		paymentEntryUrl: transaction => {
			if (!transaction.payment_entry) {
				return ''
			}
			return encodeURI(`${frappe.urllib.get_base_url()}/app/payment-entry/${transaction.payment_entry}`)
		},
		sortTransactions(key) {
			this.transactions.sort((a, b) => (a[key] > b[key] ? this.sort_order[key] : this.sort_order[key] * -1))
			this.sort_order[key] *= -1
		},
		partyIsInFilter(party) {
			return (
				cur_frm.check_run_state.party_filter.length < 1 ||
				party.toLowerCase().includes(cur_frm.check_run_state.party_filter.toLowerCase())
			)
		},
		toggleShowPartyFilter() {
			cur_frm.check_run_state.party_filter = ''
			cur_frm.check_run_state.show_party_filter = !cur_frm.check_run_state.show_party_filter
		},
		markDirty() {
			cur_frm.dirty()
		},
		onPayChange(selectedRow) {
			cur_frm.doc.amount_check_run = cur_frm.check_run_state.check_run_total()
			cur_frm.refresh_field('amount_check_run')
			this.markDirty()
			if (this.transactions[selectedRow].pay && !this.transactions[selectedRow].mode_of_payment) {
				frappe.show_alert(__('Please add a Mode of Payment for this row'))
			}
		},
		checkPay() {
			if (this.state.status == 'Draft' || !this.transactions.length) {
				return
			}
			this.transactions[this.state.selectedRow].pay = !this.transactions[this.state.selectedRow].pay
			this.onPayChange(this.state.selectedRow)
		},
		openMopWithSearch(keycode) {
			if (!this.transactions.length || !this.$refs.dropdowns) {
				return
			}
			this.$refs.dropdowns[this.state.selectedRow].openWithSearch()
		},
		showPreview(attachment) {
			debugger
			var file_url = typeof attachment == 'string' ? attachment : attachment[0].file_url
			frappe.ui.addFilePreviewWrapper()
			frappe.ui.pdfPreview(cur_frm, file_url)
		}
	},
	beforeMount() {
		this.moment = moment
		this.format_currency = format_currency
		frappe.db.get_value('Account', cur_frm.doc.pay_to_account, 'account_currency').then(r => {
			this.pay_to_account_currency = r.message.pay_to_account_currency
		})
		cur_frm.check_run_component = this
	},
}
</script>
<style scoped>
.party-filter {
	margin-top: 5px;
}
.table thead th {
	vertical-align: top;
}
.checkrun-check-box {
	vertical-align: sub; /* weird but this gives the best alignment */
}
.check-run-table td,
.check-run-table th {
	max-height: 1.5rem;
	padding: 0.4rem;
	vertical-align: middle;
}
.table tr.selectedRow {
	background-color: var(--yellow-highlight-color);
}
.table tr {
	height: 50px;
}
.sup {
    text-align: left;
}
</style>
