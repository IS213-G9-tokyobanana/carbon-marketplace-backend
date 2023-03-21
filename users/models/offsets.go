package models

import (
	"time"

	"github.com/google/uuid"
)

type OffsetInTco2e struct {
	ID          uint      `json:"id" gorm:"primary_key"`
	MilestoneId string    `json:"milestone_id"`
	UserId      uuid.UUID `json:"user_id" gorm:"foreignKey:user_id;constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
	Amount      float64   `json:"amount"`
	State       string    `json:"state"`
	CreatedAt   time.Time `json:"created_at" gorm:"autoCreateTime"`
	UpdatedAt   time.Time `json:"updated_at" gorm:"autoUpdateTime"`
}
