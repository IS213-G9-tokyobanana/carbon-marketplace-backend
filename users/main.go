package main

import (
	// "go-rest-api/middleware" // if there's middleware
	"go-rest-api/controllers"
	"go-rest-api/models"
	"log"
	"os"

	docs "go-rest-api/docs"

	"github.com/gin-gonic/gin"
	swaggerfiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

func main() {
	mode := os.Getenv("APP_MODE")

	r := SetupRouter(mode)
	models.ConnectDatabase()

	if err := r.Run(":8080"); err != nil {
		log.Fatal(err)
	}
}

func SetupRouter(mode string) *gin.Engine {
	if mode == "production" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}
	r := gin.Default()

	// use middlewares
	// r.Use(middleware.XssMiddleware())
	// if gin.Mode() == gin.ReleaseMode {
	// 	r.Use(middleware.SecurityMiddleware())
	// }
	// r.Use(middleware.CorsMiddleware())

	docs.SwaggerInfo.BasePath = "/api/v1"
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))

	v1 := r.Group("/api/v1")
	{
		v1.GET("/healthcheck", controllers.Healthcheck)
		v1.GET("/users", controllers.GetUsers)
		v1.POST("/users", controllers.CreateUser)
		v1.GET("/users/:id", controllers.GetUserById)
	}

	return r
}
