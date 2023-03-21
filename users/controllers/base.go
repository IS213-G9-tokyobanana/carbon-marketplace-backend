package controllers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

//	@BasePath	/api/v1

// PingExample godoc
//
//	@Summary		Healthcheck
//	@Schemes		http https
//	@Description	Pings the server to see if it's up
//	@Tags			example
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	object{success=bool,data=string}	"healthcheck"
//	@Router			/healthcheck [get]
func Healthcheck(g *gin.Context) {
	g.JSON(http.StatusOK, gin.H{
		"success": true,
		"data":    gin.H{"message": "healthy"},
	})
}
