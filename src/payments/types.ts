export interface TransactionInput {
  payment_id: string; // stripe checkout session id
  quantity_tco2e: number;
  project_id: string;
  milestone_id: string;
  owner_id: string;
  buyer_id: string;
}

export interface DbTransactionOutput {
  payment_id: string;
  quantity_tco2e: number;
  project_id: string;
  milestone_id: string;
  owner_id: string;
  buyer_id: string;
  created_at: Date;
  updated_at: Date;
}
