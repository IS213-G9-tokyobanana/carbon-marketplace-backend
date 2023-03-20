package rest

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

var (
	ServerError = Response{
		Status:  http.StatusInternalServerError,
		Success: false,
		Data:    gin.H{"message": "server error"},
	}
	InvalidParams = Response{
		Status:  http.StatusBadRequest,
		Success: false,
		Data:    gin.H{"message": "invalid parameters"},
	}
	UserNotFound = Response{
		Status:  http.StatusBadRequest,
		Success: false,
		Data:    gin.H{"message": "user not found"},
	}
	UserAlreadyExists = Response{
		Status:  http.StatusBadRequest,
		Success: false,
		Data:    gin.H{"message": "user already exists"},
	}
)

func SuccessWithData(data interface{}) Response {
	return Response{
		Status:  http.StatusOK,
		Success: true,
		Data:    data,
	}
}

func ServerErrorWithData(data string, err error) Response {
	return Response{
		Status:  http.StatusInternalServerError,
		Success: false,
		Data: gin.H{
			"message": fmt.Sprintf(
				"server encountered an error while trying to %s",
				data,
			),
			"error": err.Error(),
		},
	}
}

type Response struct {
	Status  int         `json:"status"`
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
}

func (r Response) Send(c *gin.Context) {
	c.JSON(r.Status, gin.H{"success": r.Success, "data": r.Data})
}
