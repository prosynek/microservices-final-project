# **Microservices & Cloud Computing Final Project** 
##### Paige Rosynek
##### CSC 5201 301
##### 05.03.2024

---

# **Wrapify - Spotify Listening History Summary**


## **Description**

Wrapify is an application that allows users to summarize their listening habits on Spotify over varying time frames. This application was inspired by the annual Spotify Wrapped which at the end of the year, provides users with a fun and insightful report of their listening habits on the app over the last year with information on the number of minutes listened, top tracks, and much more. Wrapify is a simplified version of this. With Wrapify a user can login with their Spotify account to generate, save, and delete summaries of their listening habits all year round. Each summary consists of information on the user's top 10 tracks, top 10 artists, and top 5 genres for the specified time frame. There are 3 time frames a wrap can be generated for: short (last ~4 weeks), medium (last ~6 months), long (last ~1 year). Each wrap generated is stored in a MongoDB database and users can view and delete their past wraps from within the application. With Wrapify, users can get insight into their music taste year-round!

## **Installation**

The application is deployed on a DigitalOcean Droplet running at `http://146.190.166.177:5000` so no further installation is needed.



### Run Locally (Docker-Compose)

To run the application locally:

1. Clone this repo using `git clone`
2. Navigate to the `authentication_service.py` file in the `auth_service` directory
3. Uncomment the `REDIRECT_URI` constant at the top of the file to `http://localhost:5000` and save
4. In the project root directory, run:
- `docker-compose build`
- `docker-compose up -d`

5. Enter `http://localhost:5000` in your browser to access the running application
6. To stop the application run: `docker-compose down`

**NOTE**

Due to Spotify's developer restrictions, in order to log into the application your Spotify email must be whitelisted. Optionally you can follow the steps to retrieve your own Spotify client credentials at the link here: `https://developer.spotify.com/documentation/web-api/concepts/apps` and replace the CLIENT_ID and CLIENT_SECRET variables in the config.py file in the auth_service directory.


## **Documentation**

### **Endpoints**

#### `/`
- **Method:** `GET`
- **Description:** Renders the home page of the application.


#### `/login`
- **Method:** `GET`
- **Description:** Initiates the authentication process with Spotify OAuth. Communicates with the authentication service to retrieve an authorization URL from Spotify and redirects the user.


#### `/callback`
- **Method:** `GET`
- **Description:** Handles the callback from the Spotify OAuth service after successful authorization. Retrieves the access token and stores it in the session. Redirects the user to the `/userhome` endpoint.


#### `/userhome`
- **Method:** `GET`
- **Description:** Renders the user's home page. This page allows the user to generate their wrap and navigate to their wrap home page.


#### `/wrap?term=<short, medium, long>`
- **Method:** `GET`
- **Query Parameters: term** Specifies the time frame to generate a user's wrap for. Valid values are `short` (last ~4 weeks), `medium` (last ~6 months), `long` (last ~1 year)
- **Description:** Generates a summary ("wrap") with information on the user's top 10 tracks, top 10 artists, and top 5 genres for the specified time frame (term). The summary is rendered directly on the user home page. Returns summary as JSON if not using UI.


#### `/wrap-home`
- **Method:** `GET`
- **Description:** Renders the web page that allows a user to retrieve and delete the wraps using the following endpoints.


#### `/my-wraps`
- **Methods:** `GET`, `POST`
- **Description:**
  - `GET` : Retrieves all wraps from the MongoDB database for the current user
  - `POST` : Retrieves a specific wrap by index. Passed as query parameter (?index=<value>)
  

#### `/my-wraps/<index>`
- **Method:** `GET`
- **Description:** Retrieves the wrap at the specified index for the current user. Returns error if index is out of range.


#### `/my-wraps/delete`
- **Methods:** `GET`, `POST`
- **Description:**
  - `GET` : Deletes all wraps from the MongoDB database for the current user
  - `POST` : Deletes a specific wrap by index. Passed as query parameter (?index=<value>)
 
#### `/my-wraps/delete/<index>`
- **Method:** `GET`
- **Description:** Deletes the wrap at the specified index and returns the updated list of summaries for the current user. Returns an error if the index is out of range.

#### `/logout`
- **Method:** `GET`
- **Description:** Clears the user's session and redirects to the home page (index)


## **Use Cases**

### **1. Generating a Wrap**
- Navigate to the home page
- Login with a valid Spotify account
- On the user homepage, locate the 'Generate My Wrap' button and the radio buttons below
- Select a radio button with the time frame you want to get your wrap for (short = ~4 weeks, medium = ~6 months, long = ~1 year)
- Click 'Generate My Wrap'
- Your 'wrap' will render on the same page & will be saved to the database


### **2. Viewing & Deleting Saved Wraps**
- From the user homepage, click on the 'My Saved Wraps' button
- You will be redirected to the wrap homepage
- **View all saved wraps**
    - Click on the 'Get All Wraps' button
    - Returns a list of JSON objects of all of the user's past saved wraps stored in the database
- **View a specific wrap**
    - Enter the index for the wrap you want to retrieve
    - Click the 'Retrieve Wrap' button
    - Returns the corresponding wrap as JSON, or an error if the index is out of range
- **Delete all saved wraps**
    - Click on the 'Delete All Wraps' button
    - Returns an empty list
- **Delete a specific wrap**
    - Enter the index for the wrap you want to delete
    - Click the 'Delete Wrap' button
    - Returns the updated list of all the user's saved wraps from the database

### **3. Logout**
- On the user homepage
- Click the 'Logout' button
- The user's session is cleared and is redirected to the homepage `/`

### **4. View monitoring dashboard**
- Make sure your address matches the port of the service you want to monitor (app service = 5000, auth service = 8000, spotify service = 8080)
- Navigate to the `/dashboard` endpoint
- Enter admin credentials to login
- Displays a dashboard containing information on the request latency, request count, and more for each endpoint over various time frames
