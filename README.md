# Courier_API
An API that connects Vendors to Users

This project was made using the Django Rest Framework

## Requirements
* Django == 3.2
* Django Rest Framework == 3.12
* Postgresql Database
* PostGIS Extension on Postgresql Database (Enabling coordintate data to be better stored in the database)
* Swagger (API documentation)
* Simple-Jwt-Token 
* Celery == 5.0.5 (Asynchronous Tasks)
* A Rabbit MQ Server (Server Celery Uses)
* A Google Maps API Key 

* In your command line type:
```bash
pip install requirements.txt
```

## Project Rundown
* As the description says above this project is a means to connect Vendors to their users. It increases the availability of Vendors to Users.
* Vendors Register themselves as well as their products and location on this platform, then users get the chance to see all the products from their internet-enabled device.
* Any products the user is interested in He adds to the cart and orders it. The products are then collected from all respective vendors and delivered to the user.
* The User gets access to see how long the delivery will take and the total distance of the delivery.
* Other Features include things like, a Schedule system for the vendors so that users cannot order products when vendors are closed and also a rating system for vendors to be rated..

## Documentation
* In this Section I talk about this project in detail.
* I will talk about the project almost chronologically so the flow of the process can be visualized.

### Naming Conventions
* The naming conventions used in this project involve using the model names of the object followed by what the object does, then lastly what the object is.
* To deal with ForeignKey Relationships the convention followed using the model name of the object, followed by the foreignkey relationship, then the what the object does and lastly what the object is.

* Here is an example:
```python
class Vendor(models.Model):
  pass

class VendorCreateSerializer(serializers.Serializer):
  pass

class VendorCreateView(APIView):
  pass

def vendor_create(**vendor_objects):
  pass
 
class TagVendorSerializer(serializers.Serializer):
  id = serializers.UUIDField()
```
<br/>
<br/>

### Project initialization
* So the Normal set up of a normal django project is done here. Then you configure your env_variables, the Postgresql database, PostGIS extension, Swagger.

### User/Vendor Authentication
#### Workflow
* The User registers their first and last names, phone number email and password. (Appropriate validations put for phone number)
* Emails would be sent to verify their account. Naturally only a verified account can be a Vendor.
* Password Change, Password Reset, Email-Resend verification endpoints are included.
* Celery is used for Asynchronous Mail sending and token generation.

#### Details
* User Authentication involves both Json-web-Token and Session Authentication.
* In production Session Authentication would be removed, The session Authentication just helped with the development ease and speed.
* The only details the user can update are their names. Phone numbers and Emails are immutable.
* Emails replace the username.

### Services(APP)
* The more appropriate name for the app should have been "Vendors", but head-way had already been made and changing the app name was complicated.
* This app handles every other thing apart from authentication, It handles Tag creation and updates, Vendor creation, Product creation, Geocoding etc.

#### Workflow
##### Tags
* Administrators alone can create and update Tags, Tags are to be used by Vendors so that users understand at a glance the kind of services offered.
* Tags are linked to Vendors with a Many-To-Many Relationship.

##### Vendors
* Only Verified Users can Create a Vendor and Vendors won't be recognized until approved by administrators.
* It's adviceable that Users do not use their personal accounts to create Vendors.
* Currently Vendors can categorize their services among four service areas: Restaurant, Party, Pharmacy, Groceries and Clothing.
* A vendor can Link different tags to their establishment.
* The address field in vendors can only be filled when vendors input their location in the Location Model, This is so that the Google Recognized address is associated with the vendor.
* A Vendor can upload an image to represent their establishment.
* Ratings linked to vendors are the aggregate of ratings provided by users that have used their products.

##### Schedule
* A Vendor can input their opening and closing times for everyday of the week.
* Based on the current time and day of the week the algorithm would determine if the vendor is currently open to serve their products or closed.

##### Location
* This model determines the google recognized address for the location input by the vendor.
* This is the location that would be used for Transit time and distance calculations.
* Also records the coordinates for more accurate calculations.

##### Product Category
* A Vendor can have an array of products and would like them to be categorized into different sections.
* This model creates the different sections for the vendor.
* By default once a vendor object is created a default product category is also created depending on the service the vendor provides.
* In any event a product category is deleted and it has contained products, the products are set to the default product category.
* The default product cateogory cannot be edited or deleted.

##### Product
* The Product model directly portrays the products and services provided by the vendors.
* It has the fields: "Name", "Detail", "Price", "Looks" all to allow the user to understand the product they want to procure.
* The product object is linked to the vendor that creates it and the product category they want it under.

##### Rating
* The Rating model allows users to vote for vendors they have used their services.
* The Rating is ranged from 0-5 and of course can be changed on demand.
* The Ratings are linked to the vendor that is being rated and the person rated. There cannot be duplicates of this.

##### CustomerCart
* This model allows users to store the products they want to order in a cart.
* The fields for this model will be shown below explicitly for explanation sake:

```python
class CustomerCart(BaseModel, models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    quantity = models.IntegerField(default = 1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null = True)
    ordered = models.BooleanField(default = False)
    ordered_time = models.TimeField(null = True)
    delivered_time = models.TimeField(null = True)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE, null = True)
    user = models.ForeignKey(get_user_model(), on_delete = models.CASCADE, null = True)
```
* The only field the user controls for creation are the product and quantity field.
* Then for updates the user only controls the quantity field.
* Every other field is used to control how this Model is handled and queried.
* For example: To get all the products the user has input into their cart we query for all products, filter by the user and then filter by ordered being false.
* If there is inactivity by the user on the site for a while and they have products in their cart the cart will be emptied.
* Total price is calculated by the price of the product and the quantity the user ordered.
* Ordered time is determined when the user has finally Checked out their products.
* The vendor field is added for easy querying of this model
* For example: To get all the products that users have ordered we query for all products, filter by the vendor filter by ordered being True.

#### UserLocation
* This model is where the user inputs the location they want their goods to be delivered.
* From this location among the location gotten from the customercart the transit time and transit distance is calculated.


##### Checkout
* This Field is the final summary gotten from everything the user has put in their cart.
* The final price is the sum total of all the total prices of the products the user has ordered.
* Transit time is how long it would take to deliver all the products to the user.
* Transit distance is how far in kilometers the journey to go from vendor to vendor is.
* location is the location the user input in the UserLocation model.
* The Products just contains all the information of the products being ordered in Json, This field serves as a record and can be queried for data.

### Details
* Appropriate User Restrictions have been put in place to ensure users and vendors can access their own endpoints.
* The Google Matrix API and Geocoding API feed the data for locations, Transit times and Distance times.

## Notes About Development
### Notes on Scalability
* As many serializers as required were used on each view. This is to ensure that each view is properly decoupled from other views and remove unecessary abstractions.
* Serializers For Creating, Listing, and Updating were separated from one another.
* To deal with ForeignKey relationships we created a separate serializer just for that foreignkey instead of using serializers already used.
* For Creating and Updating Model serializers were avoided to ensure abstractions for writing to the database were avoided.
* For Creating and Updating generic views were avoided to ensure abstractions for writing to the database were avoided.

#### Service Layer
* The service layer file is "Services.py"
* This file is the file that handles fetching objects from the database and linking them to the views.
* It also handles taking objects from the views and placing them in the database.

* The service layer is very important in API development because it allows proper decoupling of different functions, and creates high resusabliltiy of functions.
* Logic is not meant to be placed in the views instead it should be placed in the service layer.
* The service layer also handles creating, updating, and destroying of objects.
* Applying this layer allows more flexibility in the development process and allows new features to be added easily.
 
 ### Alternative routes for Development
* For the Schedule model that was created, the Places/Place API provided by google could have served to also provide this schedule but it's better considered to reduce the calls placed on the google api.


### A Review of the Code 
* This section looks on places that should be refactored and potential unnecessary code.
* The password change Validation should be refactored instead of being repeated in different locations.
* There are places within the code that contains relative imports instead of the Pep 8 recommended absolute imports.
* Imports were not separated according to: Python standard Library, Third-Party Packages, and Project imports accordingly.
* The Vendor_create function needs to be refactored to do only one task.
* Location-Address naming discrepancy as regards the location of the vendor.
* Schedule_create function does double validation.
* Schdedule_create function does too many tasks.
* Schedule_retrieve View for loop can be moved to the service layer.
* Error as regards incorrect UUIDS in the URLs give an error instead of 404.
* Product_create function should be refactored.
* Same with Product_update
* Rating_create function should be refactored.
* Superuser does not have absolute control as he should have, restrictions should be adjusted to accmmodate superuser authority.
* Naming discrepancy with CustomerCartRetrieve function lacks the Update part of the name.
* Did not add validation to check if user is already linked with a vendor.
* Google time parser can be extracted with regex.
* Having both post and get calls to the google api is not efficient.
* Another thing is the urls should be renamed, in such a way that it does solely what its method action represents or the views should fit the method action.

Most of the part of the review can be seen in the service.py layer that is in the services app.


