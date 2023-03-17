import { ObjectId } from "mongodb"

export default class PaymentIntent {
	constructor(public payment_id?: ObjectId) {}
}
