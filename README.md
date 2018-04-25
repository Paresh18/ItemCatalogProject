# Item Catalog App
This web app is a project for the Udacity [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## About
This project is a RESTful web application utilizing the Flask framework which accesses a SQL database that populates categories and their items. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

## In This Repo
This project has one main Python module `webserver.py` which runs the Flask application. A SQL database is created using the `database_setup.py` module and you can populate the database with test data using `lotsofmenu.py`.
The Flask application uses stored HTML templates in the tempaltes folder to build the front-end of the application. CSS are stored in the static directory.

## Skills Honed
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework

## Installation
There are some dependancies and a few instructions on how to run the application.
Seperate instructions are provided to get GConnect working also.

## Dependencies
- [Vagrant](https://www.vagrantup.com/)
- [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## How to Install
1. Install Vagrant & VirtualBox
2. Clone the Udacity Vagrantfile
3. Go to Vagrant directory and either clone this repo or download and place zip here
3. Launch the Vagrant VM (`vagrant up`)
4. Log into Vagrant VM (`vagrant ssh`)
5. Navigate to `cd/vagrant` as instructed in terminal
6. The app imports requests which is not on this vm. Run sudo pip install requests
7. Setup application database `python /ItemCatalog/database_setup.py`
8. *Insert fake data `python /ItemCatalog/lotsofmenu.py`
9. Run application using `python /ItemCatalog/webserver.py`
10. Access the application locally using http://localhost:3000

*Optional step(s)

## Using Google Login
To get the Google login working there are a few additional steps:

1. Go to [Google Dev Console](https://console.developers.google.com)
2. Sign up or Login if prompted
3. Go to Credentials
4. Select Create Crendentials > OAuth Client ID
5. Select Web application
6. Enter name 'Item-Catalog'
7. Authorized JavaScript origins = 'http://localhost:3000'
8. Authorized redirect URIs = 'http://localhost:3000/login' && 'http://localhost:3000/gconnect'
9. Select Create
10. Copy the Client ID and paste it into the `data-clientid` in login.html
11. On the Dev Console Select Download JSON
12. Rename JSON file to client_secrets.json
13. Place JSON file in ItemCatalog directory that you cloned from here
14. Run application using `python /ItemCatalog/webserver.py`


## How to use the App
After running webserver.py,the server will be hosted on http://localhost:3000.
- At this page you will see the category,and the menuitems related to categories.(logged off)
- At clicking the category you will be redirected to the http://localhost:3000/category/1/item which will show you items related to particular category(suppose in this case the category is soccer and the id is 1)(logged off)
- Ar clicking the menuitems you will be redirected to the http://localhost:3000/menuitem/Hockeyballs/description/
description page of the menuitem,you will not be able to see the "EditItem" and "DeleteItem" as you are not login.(logged off)

Now here I have reduced one step of login separately through a separate login button.

Suppose you have to Add the item you will click the "AddItem" button and it will ask you to login through Google once
you are sign in you will be redirected to the  http://localhost:3000category/new/ this will add the new menuItem related
to particular category and after adding you will be redirected to http://localhost:3000 page with all the values entered.
- Now since you are logged in when you again click on "AddItem" it will redirect you to  http://localhost:3000category/new/
page and will not ask to login again.


### (After login)
At http://localhost:300 you will see login username and Logout link at the right corner.
- When you click at MenuItem it will redirect you to http://localhost:3000/menuitem/Hockeyballs/description/ at this page since you are login you are now will see "EditItem" and "DeleteItem" and which you can use to deleteItems and ediitems.

### For public view I have pages
You will only be able to see the pages and will not have the authority to do anything unless you are loggedin.
- http://localhost:3000/
- http://localhost:3000/menuitem/Hockeyballs/description/
- http://localhost:3000/category/1/item

(After logging in)
You will have the ability to edit and delete item and add item.

I have implemented all the functionality in a different way and the above described workflow will let you follow it. 

## JSON Endpoints
The following are open to the public:

Catalog JSON: `/category/JSON`
    - Displays the whole Categories

Categories JSON: `/items/JSON`
    - Displays all items

Category Items JSON: `category/<int:category_id/item/JSON`
    - Displays items for a specific category
