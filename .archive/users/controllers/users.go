package controllers

import (
	"fmt"
	"go-rest-api/models"
	"go-rest-api/rest"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/lib/pq"
	"gorm.io/gorm"
)

// GetUsers godoc
//
//	@Summary		Get list of users
//	@Schemes		http https
//	@Description	fetch all Users' data based on the query parameters
//	@Tags			users
//	@Accept			json
//	@Produce		json
//	@Param			type		query		string									false	"type"
//	@Param			project_id	query		string									false	"project_id"
//	@Success		200			{object}	object{success=bool,data=[]models.User}	"list of users matching the query"
//	@Router			/users [get]
func GetUsers(c *gin.Context) {
	db := models.DB
	var (
		users     []interface{}
		err       error
		buyers    []models.Buyer
		sellers   []models.Seller
		verifiers []models.Verifier
	)

	// Check for query parameters
	queryUserType := c.Query("type")
	queryProjectId := c.Query("project_id")

	// If no query parameters are provided, return all users
	if queryUserType == "" && queryProjectId == "" {
		err = db.Find(&buyers).Error
		if err == nil {
			for _, buyer := range buyers {
				users = append(users, buyer)
			}
		}

		err = db.Find(&sellers).Error
		if err == nil {
			for _, seller := range sellers {
				users = append(users, seller)
			}
		}

		err = db.Find(&verifiers).Error
		if err == nil {
			for _, verifier := range verifiers {
				users = append(users, verifier)
			}
		}
	} else {
		// Prepare the WHERE clause for query
		where := ""
		args := []interface{}{}
		if queryUserType != "" {
			where = "type = ?"
			args = append(args, queryUserType)
		}
		if queryProjectId != "" {
			if where != "" {
				where += " AND "
			}
			where += "project_ids @> ?"
			args = append(args, pq.Array([]string{queryProjectId}))
		}

		// Query the database
		err = db.Where(where, args...).Find(&buyers).Error
		if err == nil {
			for _, buyer := range buyers {
				users = append(users, buyer)
			}
		}

		err = db.Where(where, args...).Find(&sellers).Error
		if err == nil {
			for _, seller := range sellers {
				users = append(users, seller)
			}
		}

		err = db.Where(where, args...).Find(&verifiers).Error
		if err == nil {
			for _, verifier := range verifiers {
				users = append(users, verifier)
			}
		}
	}

	if len(users) == 0 {
		rest.SuccessWithData([]interface{}{}).Send(c)
		return
	}

	rest.SuccessWithData(users).Send(c)
}

// GetUsersById godoc
//
//	@Summary		Get user by id
//	@Schemes		http https
//	@Description	fetch a User's data based on the id
//	@Tags			users
//	@Accept			json
//	@Produce		json
//	@Param			id	path		string									true	"id"
//	@Success		200	{object}	object{success=bool,data=models.User}	"user matching the id"
//	@Router			/users/{id} [get]
func GetUserById(c *gin.Context) {
	db := models.DB
	id := c.Param("id")

	// Check for the user in each table
	buyer := models.Buyer{}
	err := db.Where("id = ?", id).First(&buyer).Error
	if err == nil {
		rest.SuccessWithData(buyer).Send(c)
		return
	}

	seller := models.Seller{}
	err = db.Where("id = ?", id).First(&seller).Error
	if err == nil {
		rest.SuccessWithData(seller).Send(c)
		return
	}

	verifier := models.Verifier{}
	err = db.Where("id = ?", id).First(&verifier).Error
	if err == nil {
		rest.SuccessWithData(verifier).Send(c)
		return
	}

	// If the user wasn't found in any table, return a not found error
	rest.UserNotFound.Send(c)
}

// CreateUser godoc
//
//	@Summary		Create a user
//	@Schemes		http https
//	@Description	create a new user
//	@Tags			users
//	@Accept			json
//	@Produce		json
//	@Param			name				body		string									true	"name"
//	@Param			email				body		string									true	"email"
//	@Param			type				body		string									true	"type"
//	@Param			project_id			body		string									false	"project_id"
//	@Param			footprint_in_tco2e	body		string									false	"footprint_in_tco2e"
//	@Success		200					{object}	object{success=bool,data=models.User}	"user created"
//	@Router			/users [post]
func CreateUser(c *gin.Context) {
	// Parse request body params
	var params struct {
		Name             string   `json:"name" binding:"required"`
		Email            string   `json:"email" binding:"required,email"`
		Type             string   `json:"type" binding:"required,oneof=verifier buyer seller"`
		ProjectID        *string  `json:"project_id"`
		FootprintInTco2e *float64 `json:"footprint_in_tco2e"`
	}
	if err := c.ShouldBindJSON(&params); err != nil {
		rest.InvalidParams.Send(c)
		return
	}

	// Create user based on type
	var user interface{}
	commonFields := models.User{
		ID:        uuid.New(),
		Name:      params.Name,
		Email:     params.Email,
		Type:      params.Type,
		CreatedAt: time.Now().UTC(),
		UpdatedAt: time.Now().UTC(),
	}
	switch params.Type {
	case "verifier":
		user = &models.Verifier{
			User: commonFields,
		}
	case "buyer":
		user = &models.Buyer{
			User: commonFields,
		}
	case "seller":
		user = &models.Seller{
			User: commonFields,
		}
	}

	// Add project ID if provided
	if params.ProjectID != nil {
		switch u := user.(type) {
		case *models.Verifier:
			u.ProjectIds = pq.StringArray([]string{*params.ProjectID})
		case *models.Seller:
			u.ProjectIds = pq.StringArray([]string{*params.ProjectID})
		}
	}

	// Add footprint if provided
	if params.FootprintInTco2e != nil {
		switch u := user.(type) {
		case *models.Buyer:
			u.FootprintInTco2e = *params.FootprintInTco2e
		}
	}

	// Save user to database
	if err := models.DB.Create(user).Error; err != nil {
		if err == gorm.ErrDuplicatedKey {
			rest.UserAlreadyExists.Send(c)
		} else {
			rest.ServerErrorWithData(
				fmt.Sprintf("creating %s user", params.Type),
				err,
			).Send(c)
		}
		return
	}

	rest.SuccessWithData(user).Send(c)
}
