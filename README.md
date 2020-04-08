# marathon

API service for Marathon


## Installation

`sudo apt install postgresql`

`sudo apt install postgresql-server-dev-10`

`pip install -r requirements.txt`

Create postgreSQL database

Go to `settings.py` and change database name, user and password accordingly

Make migrations `python manager.py makemigrations`

Migrate `python manager.py migrate`


## Running
`cd marathon/`

`python manage.py runserver`

To access the API go to http://localhost:8000/


## API Documentation

### Available HTTP Methods & Their Standard Usage
* **GET:** For listing/retrieving resource(s)
* **POST:** For creating a resource
* **PUT:** For updating a resource fully(Send data with all fields required during resource creation)
* **PATCH:** For updating a resource partially(Send data with only fields which you want to update)
* **DELETE:** For deleting a resource


### Available Routes
* **register:** [`/register/`](#Register-User)
* **login:** [`/auth/`](#Authenticate-User)
* **users:** [`/users/`](#Users)
* **marathons:** [`/marathons/`](#Marathons)
* **categories:** [`/categories/`](#Categories)
* **sponsors:** [`/sponsors/`](#Sponsors)
* **payments:** [`/payments/`](#Payments)


### Register User
Available Routes
* `/register/`

Available HTTP Method
* POST

Data Format
```js
{
    "username": "string",  // Must be a valid username
    "email": "string",  // Must be a valid email
    "password": "password",  // Must be a valid password
    "role": "string"  // Value must be either "client", "organizer" or "admin"
}
```


### Authenticate User
Available Routes
* `/auth/`

Available HTTP Methods
* POST

Data Format
```js
{
    "username": "valid username",
    "password": "valid password"
}
```

### Users 
Available Routes
* `/users/`
* `/users/{user_id}/`

Available HTTP Methods
* GET
* PUT
* PATCH

Data Format
```js
{
    "username": "valid username",
    "email": "valid email",
    "phone": "valid phone number",
    "full_name": "string",
    "gender": "M/F", // Value must be one of these charactors
    "is_active": "Boolean"
}
```


### Marathons
Available Routes
* `/marathons/`
* `/marathons/{id}/`

Available HTTP Methods
* GET
* POST(only for admin or organizer)
* PUT(only for admin or organizer)
* PATCH(only for admin or organizer)
* DELETE(only for admin or organizer)

Data Format
```js
{
    "name": "string, 
    "theme": "text, 
    "sponsors": "dict", // e.g {"create": [{"name": "Stripe Company"}, {"name", "Lite Company"}]} 
    "categories": "dict", // e.g {"create": [{"name": "FULL", "price": "40", "currency": "USD"}]}
    "start_date": "date in YYMMDD format", // eg "20201227"
    "end_date": "date in YYMMDD format", // eg "20201228"
}
```


### Categories
Available Routes
* `/categories/`
* `/categories/{id}/`

**Note:** This is not meant to be used directly(use marathon's categories field to create and update instead)

Available HTTP Methods
* GET(only for admin or organizer)
* POST(only for admin or organizer)
* PUT(only for admin or organizer)
* PATCH(only for admin or organizer)
* DELETE(only for admin or organizer)

All methods are available for admin or organizer only

Data Format
```js
{
    "name": "string"  // Must be either FULL or HALF
    "price": "float",
    "currency": "string", // Must be USD or TZS for now
    "marathon": "int" // Marathon id
}
```


### Sponsors
Available Routes 
* `/sponsors/`
* `/sponsors/{id}/`

**Note:** This also is not meant to be used directly(use marathon's sponsors field to create and update instead)

Available HTTP Methods
* GET(only for admin or organizer)
* POST(only for admin or organizer)
* PUT(only for admin or organizer)
* PATCH(only for admin or organizer)
* DELETE(only for admin or organizer)

Data Format
```js
{
    "name": "string",
    "marathon": "int" // Marathon id
}
```


### Payments
Available Routes
* `/payments/`
* `/payments/{id}/`

Available HTTP Methods
* GET(only for admin or organizer or client)
* POST(only for admin or client)
* PUT(only for admin)
* PATCH(only for admin)
* DELETE(only for admin or client)


Data Format
```js
{
    "marathon": "int", // Marathon id
    "category": "int" // Category id
}
```