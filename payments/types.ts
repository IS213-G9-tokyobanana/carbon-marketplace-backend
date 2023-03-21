import Stripe from "stripe"

export interface TransactionInput {
	amount: number
	currency: string
	quantity_tco2e: number
	milestone_id: string
	owner_id: string
	buyer_id: string
}

export interface DbTransactionOutput {
	payment_id: string
	payment_intent: Stripe.PaymentIntent
	quantity_tco2e: number
	milestone_id: string
	owner_id: string
	buyer_id: string
	created_at: Date
	updated_at: Date
}
