package models

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"
)

// Generic User model
type User struct {
	ID        uuid.UUID `json:"id" gorm:"type:uuid;primaryKey"`
	Name      string    `json:"name" gorm:"not null"`
	Email     string    `json:"email" gorm:"not null;unique"`
	Type      string    `json:"type" gorm:"not null"`
	CreatedAt time.Time `json:"created_at" gorm:"type:timestamp with time zone;not null"`
	UpdatedAt time.Time `json:"updated_at" gorm:"type:timestamp with time zone;not null"`
}

// Specific User models
type Buyer struct {
	User
	FootprintInTco2e float64 `json:"footprint_in_tco2e"`
}

type Seller struct {
	User
	ProjectIds pq.StringArray `json:"project_ids" gorm:"type:text[]"`
}

func (s Seller) MarshalJSON() ([]byte, error) {
	type Alias Seller        // create an alias of the Seller type to avoid infinite recursion
	if s.ProjectIds == nil { // check if the slice is nil
		s.ProjectIds = []string{} // if nil, set it to an empty slice
	}
	return json.Marshal(&struct {
		*Alias
	}{
		Alias: (*Alias)(&s),
	})
}

type Verifier struct {
	User
	MilestoneIds pq.StringArray `json:"milestone_ids" gorm:"type:text[]"`
	ProjectIds   pq.StringArray `json:"project_ids" gorm:"type:text[]"`
}

func (v Verifier) MarshalJSON() ([]byte, error) {
	type Alias Verifier      // create an alias of the Verifier type to avoid infinite recursion
	if v.ProjectIds == nil { // check if the slice is nil
		v.ProjectIds = []string{} // if nil, set it to an empty slice
	}
	if v.MilestoneIds == nil { // check if the slice is nil
		v.MilestoneIds = []string{} // if nil, set it to an empty slice
	}

	return json.Marshal(&struct {
		*Alias
	}{
		Alias: (*Alias)(&v),
	})
}
