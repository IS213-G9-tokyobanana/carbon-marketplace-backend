# Users Microservice

Built with Go, this microservice is responsible for managing users.

## Prerequisites

- [Docker](https://www.docker.com/)
- [Go 1.20+](https://go.dev/dl/)

## Initial Setup

1. Clone the repository

```bash
git clone
```

2. Run docker compose

```bash
docker compose up
```

## Local Development

1. Stop the go-rest-api container

```bash
docker stop go-rest-api
```

2. Run the gin app with hot reload

```bash
go run main.go
```

3. Make necessary code changes & test with Postman. Restart the go-rest-api container once satisfied.

```bash
docker start go-rest-api
```

## Testing

You can run automated test with postman by importing the collection from the `postman` folder.

## API Documentation

You can view the API documentation by running the app and navigating to `http://localhost:8080/swagger/index.html`

API documentation are automatically generated using [swag](https://github.com/swaggo/swag) and [gin-swagger](https://github.com/swaggo/gin-swagger).

To update the API documentation, run the following command:

```bash
swag init
```

For more information on syntax of the comment parameters used to generate the API documentation, refer to the [swag documentation](https://github.com/swaggo/gin-swagger)

Example:

```go
package controller

import (
    "fmt"
    "net/http"
    "strconv"

    "github.com/gin-gonic/gin"
    "github.com/swaggo/swag/example/celler/httputil"
    "github.com/swaggo/swag/example/celler/model"
)

// ShowAccount godoc
// @Summary      Show an account
// @Description  get string by ID
// @Tags         accounts
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "Account ID"
// @Success      200  {object}  model.Account
// @Failure      400  {object}  httputil.HTTPError
// @Failure      404  {object}  httputil.HTTPError
// @Failure      500  {object}  httputil.HTTPError
// @Router       /accounts/{id} [get]
func (c *Controller) ShowAccount(ctx *gin.Context) {
  id := ctx.Param("id")
  aid, err := strconv.Atoi(id)
  if err != nil {
    httputil.NewError(ctx, http.StatusBadRequest, err)
    return
  }
  account, err := model.AccountOne(aid)
  if err != nil {
    httputil.NewError(ctx, http.StatusNotFound, err)
    return
  }
  ctx.JSON(http.StatusOK, account)
}
//...
```

## Built With

- [Go](https://golang.org/) - Programming Language
- [Gin-gonic](https://gin-gonic.com/) - Web framework
- [GORM](https://gorm.io/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Swagger](https://swagger.io/) - API documentation
